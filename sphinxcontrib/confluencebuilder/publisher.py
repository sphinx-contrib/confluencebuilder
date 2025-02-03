# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

"""
See also:
    Confluence Cloud REST API Reference
    https://docs.atlassian.com/confluence/REST/latest/
"""

from sphinxcontrib.confluencebuilder.config.exceptions import ConfluenceConfigError
from sphinxcontrib.confluencebuilder.debug import PublishDebug
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceBadApiError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceBadServerUrlError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceMissingPageIdError
from sphinxcontrib.confluencebuilder.exceptions import ConfluencePermissionError
from sphinxcontrib.confluencebuilder.exceptions import ConfluencePublishAncestorError
from sphinxcontrib.confluencebuilder.exceptions import ConfluencePublishSelfAncestorError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceUnexpectedCdataError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceUnknownInstanceError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceUnreconciledPageError
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
from sphinxcontrib.confluencebuilder.rest import Rest
from sphinxcontrib.confluencebuilder.std.confluence import API_REST_V1
from sphinxcontrib.confluencebuilder.std.confluence import API_REST_V2
from sphinxcontrib.confluencebuilder.util import ConfluenceUtil
from sphinxcontrib.confluencebuilder.util import detect_cloud
from urllib.parse import parse_qsl
from urllib.parse import urlparse
import json
import logging
import time


# number of elements to fetch for bulk requests
# (Confluence v2 APIs indicate a max of 250; a good enough number as any)
BULK_LIMIT = 250

# key used for managing this extension's properties on a Confluence instance
CB_PROP_KEY = 'sphinxcontrib.confluencebuilder'


class ConfluencePublisher:
    def __init__(self):
        self.cloud = None
        self.space_display_name = None
        self.space_id = None
        self.space_type = None
        self._ancestors_cache = set()
        self._name_cache = {}

    def init(self, config, cloud=None):
        self.cloud = cloud
        self.config = config
        self.rest = None

        self.append_labels = config.confluence_append_labels
        self.dryrun = config.confluence_publish_dryrun
        self.notify = not config.confluence_disable_notifications
        self.onlynew = config.confluence_publish_onlynew
        self.parent_id = config.confluence_parent_page_id_check
        self.parent_ref = config.confluence_parent_page
        self.server_url = config.confluence_server_url
        self.space_key = config.confluence_space_key
        self.watch = config.confluence_watch

        # track api prefix values to apply
        prefix_overrides = config.confluence_publish_override_api_prefix or {}
        self.APIV1 = prefix_overrides.get('v1', f'{API_REST_V1}/')
        self.APIV2 = prefix_overrides.get('v2', f'{API_REST_V2}/')

        # if a default cloud value is provided, attempt to detect the cloud
        # type
        if cloud is None:
            if config.confluence_adv_cloud is not None:
                self.cloud = config.confluence_adv_cloud
            else:
                self.cloud = detect_cloud(config.confluence_server_url)

        # determine api mode to use
        # - if an explicit api mode is configured, use it
        # - if this is a cloud instance, use v2
        # - for all other cases, use v1
        if config.confluence_api_mode:
            self.api_mode = config.confluence_api_mode
        elif self.cloud:
            self.api_mode = 'v2'
        else:
            self.api_mode = 'v1'

        # append labels by default
        if self.append_labels is None:
            self.append_labels = True

        # if debugging, enable requests (urllib3) logging
        if PublishDebug.urllib3 in self.config.confluence_publish_debug:
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            rlog = logging.getLogger('requests.packages.urllib3')
            rlog.setLevel(logging.DEBUG)

    def connect(self):
        self.rest = Rest(self.config)
        server_url = self.config.confluence_server_url

        # Example space fetch points:
        # https://sphinxcontrib-confluencebuilder.atlassian.net/wiki/rest/api/space/STABLE
        # https://sphinxcontrib-confluencebuilder.atlassian.net/wiki/api/v2/spaces?keys=STABLE

        api_token_set = bool(self.config.confluence_api_token)
        pw_set = bool(self.config.confluence_server_pass)
        auth_set = api_token_set or pw_set
        pat_set = bool(self.config.confluence_publish_token)

        try:
            if self.api_mode == 'v2':
                spaces_url = f'{self.APIV2}spaces'
                rsp_spaces = self.rest.get(spaces_url, {
                    'keys': self.space_key,
                    'limit': 1,
                })

                # if no size entry is provided, this a non-Confluence instance
                if 'results' not in rsp_spaces:
                    raise ConfluenceBadServerUrlError(server_url,
                        'server provided an unexpected response; no results')

                # handle if the provided space key was not found
                if len(rsp_spaces['results']) == 1:
                    rsp = rsp_spaces['results'][0]
                else:
                    raise ConfluenceUnknownInstanceError(
                        server_url,
                        self.space_key,
                        self.config.confluence_server_user,
                        auth_set,
                        pat_set,
                    )
            else:
                rsp = self.rest.get(f'{self.APIV1}space/{self.space_key}')
        except ConfluenceBadApiError as ex:
            if ex.status_code == 404:
                # if this is a 404 (not found), give a more custom message
                # since on an initial connect, this may be either that the
                # instance url is wrong, the space could not be found since
                # the key is wrong or that the user does not have permission
                # to see that the space exists
                raise ConfluenceUnknownInstanceError(
                    server_url,
                    self.space_key,
                    self.config.confluence_server_user,
                    auth_set,
                    pat_set,
                ) from ex

            raise ConfluenceBadServerUrlError(server_url, ex) from ex

        # sanity check that we have a sane response
        if not isinstance(rsp, dict):
            msg = 'server did not provide an expected response; no dictionary'
            raise ConfluenceBadServerUrlError(server_url, msg)

        expected_entries = [
            'id',
            'key',
            'name',
            'type',
        ]

        if not all(entry in rsp for entry in expected_entries):
            msg = 'server did not provide an expected response; missing entries'
            raise ConfluenceBadServerUrlError(server_url, msg)

        # track required space information
        self.space_display_name = rsp['name']
        self.space_id = rsp['id']
        self.space_type = rsp['type']

    def disconnect(self):
        if self.rest:
            self.rest.close()

    def archive_page(self, page_id):
        if self.dryrun:
            self._dryrun('archive page', page_id)
            return

        if self.onlynew:
            self._onlynew('page archive restricted', page_id)
            return

        try:
            data = {
                'pages': [{'id': page_id}],
            }

            rsp = self.rest.post(f'{self.APIV1}content/archive', data)
            longtask_id = rsp['id']

            # wait for the archiving of the page to complete
            MAX_WAIT_FOR_PAGE_ARCHIVE = 4  # ~2 seconds
            attempt = 1
            while attempt <= MAX_WAIT_FOR_PAGE_ARCHIVE:
                time.sleep(0.5)

                rsp = self.rest.get(f'{self.APIV1}longtask/{longtask_id}')
                if rsp['finished']:
                    break

                attempt += 1
                if attempt > MAX_WAIT_FOR_PAGE_ARCHIVE:
                    msg = 'timeout waiting for archive completion'
                    raise ConfluenceBadApiError(-1, msg)
        except ConfluencePermissionError as ex:
            msg = (
                'Publish user does not have permission to archive '
                'from the configured space.'
            )
            raise ConfluencePermissionError(msg) from ex

    def archive_pages(self, page_ids):
        if self.dryrun:
            self._dryrun('archiving pages', ', '.join(page_ids))
            return

        if self.onlynew:
            self._onlynew('page archiving restricted', ', '.join(page_ids))
            return

        try:
            data = {
                'pages': [],
            }

            for page_id in page_ids:
                data['pages'].append({'id': page_id})

            # Note, multi-page archive can result in Confluence reporting the
            # following message:
            #  Cannot use bulk archive feature for non premium edition
            self.rest.post(f'{self.APIV1}content/archive', data)

        except ConfluencePermissionError as ex:
            msg = (
                'Publish user does not have permission to archive '
                'from the configured space.'
            )
            raise ConfluencePermissionError(msg) from ex

    def get_ancestors(self, page_id):
        """
        generate a list of ancestors

        Queries the configured Confluence instance for a set of ancestors for
        the provided `page_id`.

        Args:
            page_id: the ancestor to search on

        Returns:
            the ancestors
        """

        assert page_id
        ancestors = set()

        if self.api_mode == 'v2':
            rsp = self.rest.get(f'{self.APIV2}pages/{page_id}/ancestors')

            for result in rsp['results']:
                ancestors.add(result['id'])
        else:
            _, page = self.get_page_by_id(page_id, 'ancestors')

            if 'ancestors' in page:
                for ancestor in page['ancestors']:
                    ancestors.add(ancestor['id'])

        return ancestors

    def get_base_page_id(self):
        base_page_id = self.config.confluence_publish_root

        if not self.parent_ref:
            return base_page_id

        # fetching a base page by a numerical identifier
        if isinstance(self.parent_ref, int):
            base_page_id, page = self.get_page_by_id(self.parent_ref)

            if not page:
                msg = 'Configured parent page identifier does not exist.'
                raise ConfluenceConfigError(msg)

            return base_page_id

        # fetching a base page by a page-name identifier
        base_page_id, page = self.get_page(self.parent_ref)

        if not page:
            msg = 'Configured parent page name does not exist.'
            raise ConfluenceConfigError(msg)

        if self.parent_id and base_page_id != str(self.parent_id):
            msg = 'Configured parent page ID and name do not match.'
            raise ConfluenceConfigError(msg)

        self._name_cache[base_page_id] = self.parent_ref

        if not base_page_id and self.parent_id:
            msg = 'Unable to find parent page matching the ID/name provided.'
            raise ConfluenceConfigError(msg)

        return base_page_id

    def get_descendants(self, page_id, mode):
        """
        generate a list of descendants

        Queries the configured Confluence instance for a set of descendants for
        the provided `page_id` or (if set to `None`) the configured space.

        There are a series of modes supported by this call:

        - `direct`
            Descendants will be queried for by asking Confluence the list of
            descendants by looking at the content data cached for the specified
            page/space. In theory, this should be the proper/fastest call to
            use. However, it has been observed in some scenarios that not all
            descendants will be listed (depending on the version of Confluence,
            possible caching, etc.).

        - `search`
            Descendants will be queried for by asking Confluence the list of
            descendants by performing a CQL search for descendants of a
            specified page/space. This method of searching for descendants is
            available since it appeared to provide more consistent results in
            earlier versions of Confluence. However, this method (in the
            same manner for `direct`), may be missing some descendants
            (depending on the version of Confluence, possible caching, etc.).

        - `<mode>-aggressive`
            Descendants will be queried in the same manner as the specied mode
            type, with the addition that for each page found, an additional
            fetching will be performed to check for descendants for a found
            descendant. Querying stops when all descendants have been fetched
            on. This method of searching provides the most consistent results in
            populating known descendants. However, this call significantly
            increases the amount of API calls performed.

        Args:
            page_id: the ancestor to search on (if not `None`)
            mode: the mode to search for descendants

        Returns:
            the descendants
        """

        if 'aggressive' in mode:
            descendants = self._get_descendants_aggressive(page_id, mode)
        else:
            descendants = self._get_descendants(page_id, mode)

        return descendants

    def _get_descendants(self, page_id, mode):
        """
        generate a list of descendants

        Queries the configured Confluence instance for a set of descendants for
        the provided `page_id` or (if set to `None`) the configured space.

        Args:
            page_id: the ancestor to search on (if not `None`)
            mode: the mode to search for descendants

        Returns:
            the descendants
        """

        api_endpoint = f'{self.APIV1}content/search'
        descendants = set()
        search_fields = {}

        if page_id:
            if 'direct' in mode:
                api_endpoint = f'{self.APIV1}content/{page_id}/descendant/page'
            else:
                search_fields['cql'] = f'ancestor={page_id}'
        else:
            # always use search if no page id was provided (e.g. a space search)
            search_fields['cql'] = f'space="{self.space_key}" and type=page'

        # Configure a larger limit value than the default (no provided
        # limit defaults to 25). This should reduce the number of queries
        # needed to fetch a complete descendants set (for larger sets).
        search_fields['limit'] = BULK_LIMIT

        rsp = self.rest.get(api_endpoint, search_fields)
        idx = 0
        while rsp['results']:
            for result in rsp['results']:
                descendants.add(result['id'])
                self._name_cache[result['id']] = result['title']

            count = len(rsp['results'])
            if count != BULK_LIMIT:
                break

            idx += count
            next_fields = self._next_page_fields(rsp, search_fields, idx)
            if not next_fields:
                break

            rsp = self.rest.get(api_endpoint, next_fields)

        return descendants

    def _get_descendants_aggressive(self, page_id, mode):
        """
        generate a list of descendants (aggressive)

        Queries the configured Confluence instance for a set of descendants for
        the provided `page_id` or (if set to `None`) the configured space. This
        request is a more aggressive search for descendants when compared to
        `getDescendants`. Each page found will be again searched on for
        descendants. This is to handle rare cases where a Confluence instance
        does not provide a complete set of descendants (this has been observed
        on some instances of Confluence server; speculated to be possible
        cache corruption). This search can be extremely slow for large document
        sets.

        Args:
            page_id: the ancestor to search on (if not `None`)
            mode: the mode to search for descendants

        Returns:
            the descendants
        """
        visited_pages = set()

        def find_legacy_pages(page_id, pages):
            descendants = self._get_descendants(page_id, mode)
            for descendant in descendants:
                if descendant not in pages:
                    pages.add(descendant)
                    find_legacy_pages(descendant, pages)

        find_legacy_pages(page_id, visited_pages)
        return visited_pages

    def get_attachment(self, page_id, name):
        """
        get attachment information with the provided page id and name

        Performs an API call to acquire known information about a specific
        attachment. This call can returns both the attachment identifier (for
        convenience) and the attachment object. If the attachment cannot be
        found, the returned tuple will return ``None`` entries.

        Args:
            page_id: the page identifier
            name: the attachment name

        Returns:
            the attachment id and attachment object
        """
        attachment = None
        attachment_id = None

        if self.api_mode == 'v2':
            url = f'{self.APIV2}pages/{page_id}/attachments'
        else:
            url = f'{self.APIV1}content/{page_id}/child/attachment'

        rsp = self.rest.get(url, {
            'filename': name,
        })

        if rsp['results']:
            attachment = rsp['results'][0]
            attachment_id = attachment['id']
            self._name_cache[attachment_id] = name

        return attachment_id, attachment

    def get_attachments(self, page_id):
        """
        get all known attachments for a provided page id

        Query a specific page identifier for all attachments being held by the
        page.

        Args:
            page_id: the page identifier

        Returns:
            dictionary of attachment identifiers to their respective names
        """
        attachment_info = {}

        if self.api_mode == 'v2':
            url = f'{self.APIV2}pages/{page_id}/attachments'
        else:
            url = f'{self.APIV1}content/{page_id}/child/attachment'

        search_fields = {}

        # Configure a larger limit value than the default (no provided
        # limit defaults to 25). This should reduce the number of queries
        # needed to fetch a complete attachment set (for larger sets).
        search_fields['limit'] = BULK_LIMIT

        rsp = self.rest.get(url, search_fields)
        idx = 0
        while rsp['results']:
            for result in rsp['results']:
                attachment_info[result['id']] = result['title']
                self._name_cache[result['id']] = result['title']

            count = len(rsp['results'])
            if count != BULK_LIMIT:
                break

            idx += count
            next_fields = self._next_page_fields(rsp, search_fields, idx)
            if not next_fields:
                break

            rsp = self.rest.get(url, next_fields)

        return attachment_info

    def get_page(self, page_name, expand='version', status='current'):
        """
        get page information with the provided page name

        Performs an API call to acquire known information about a specific page.
        This call can returns both the page identifier (for convenience) and the
        page object. If the page cannot be found, the returned tuple will
        return ``None`` entries.

        Args:
            page_name: the page name
            expand (optional): data to expand on
            status (optional): the page status to search for

        Returns:
            the page id and page object
        """
        page = None
        page_id = None

        if self.api_mode == 'v2':
            rsp = self.rest.get(f'{self.APIV2}pages', {
                'body-format': 'storage',
                'space-id': self.space_id,
                'status': status,
                'title': page_name,
            })
        elif self.config.confluence_page_search_mode == 'search':
            rsp = self.rest.get(f'{self.APIV1}content/search', {
                'cql': 'space="' + self.space_key +
                    '" and type=page and title="' + page_name + '"',
                "cqlcontext": json.dumps({
                    'contentStatuses': [
                        status,
                    ],
                }),
                'expand': expand,
                'limit': 1,
            })
        else:
            rsp = self.rest.get(f'{self.APIV1}content', {
                'type': 'page',
                'spaceKey': self.space_key,
                'title': page_name,
                'status': status,
                'expand': expand,
            })

        if rsp['results']:
            page = rsp['results'][0]
            page_id = page['id']
            self._name_cache[page_id] = page_name

        # if `expand` is set and this is a v2 API request, perform additional
        # queries for various options requested; we will emulate the response
        # observed in a v1 request (by populating a page with additional data;
        # which we later need to strip if updating a page)
        if page_id and self.api_mode == 'v2':
            assert 'ancestors' not in page
            assert 'metadata' not in page

            opts = expand.split(',')
            metadata = page.setdefault('metadata', {})
            meta_props = metadata.setdefault('properties', {})

            if 'ancestors' in opts:
                rsp = self.rest.get(f'{self.APIV2}pages/{page_id}/ancestors', {
                    'limit': BULK_LIMIT,
                })
                page['ancestors'] = rsp['results']

            if 'metadata.labels' in opts:
                rsp = self.rest.get(f'{self.APIV2}pages/{page_id}/labels', {
                    'limit': BULK_LIMIT,
                })

                metadata['labels'] = rsp

            props_to_fetch = []

            # if certain properties are request, ensure we generate a
            # request to fetch these values; we will populate the "legacy"
            # metadata field for processed, but also keep track of these
            # properties for possible updates
            if 'metadata.properties.content_appearance_published' in opts:
                props_to_fetch.append('content-appearance-published')

            if 'metadata.properties.editor' in opts:
                props_to_fetch.append('editor')

            for prop_key in props_to_fetch:
                prop_entry = self.get_page_property(page_id, prop_key, {
                    'value': None,
                })
                meta_props[prop_key] = prop_entry

        return page_id, page

    def get_page_by_id(self, page_id, expand='version'):
        """
        get page information with the provided page name

        Performs an API call to acquire known information about a specific page.
        This call can returns both the page identifier (for convenience) and the
        page object. If the page cannot be found, the returned tuple will
        return ``None`` entries.

        Args:
            page_id: the page identifier
            expand (optional): data to expand on

        Returns:
            the page id and page object
        """

        if self.api_mode == 'v2':
            page = self.rest.get(f'{self.APIV2}pages/{page_id}')
        else:
            page = self.rest.get(f'{self.APIV1}content/{page_id}', {
                'status': 'current',
                'expand': expand,
            })

        if page:
            assert int(page_id) == int(page['id'])
            self._name_cache[page_id] = page['title']

        return page_id, page

    def get_page_case_insensitive(self, page_name):
        """
        get page information with the provided page name (case-insensitive)

        Performs a case-insensitive search for a page with a given page name.
        This is to aid in situations where `getPage` cannot find a page based
        off a provided name since the exact casing is not known. This call will
        perform a CQL search for similar pages (using the `~` hint), which each
        will be cycled through for a matching instance to the provided page
        name.

        Args:
            page_name: the page name

        Returns:
            the page id and page object
        """
        page = None
        page_id = None

        page_name = page_name.lower()
        search_fields = {'cql': 'space="' + self.space_key +
            '" and type=page and title~"' + page_name + '"'}
        search_fields['limit'] = BULK_LIMIT

        api_endpoint = f'{self.APIV1}content/search'
        rsp = self.rest.get(api_endpoint, search_fields)
        idx = 0
        while rsp['results']:
            for result in rsp['results']:
                result_title = result['title']
                if page_name == result_title.lower():
                    page_id, page = self.get_page(result_title)
                    break

            count = len(rsp['results'])
            if page_id or count != BULK_LIMIT:
                break

            idx += count
            next_fields = self._next_page_fields(rsp, search_fields, idx)
            if not next_fields:
                break

            rsp = self.rest.get(api_endpoint, next_fields)

        return page_id, page

    def get_page_property(self, page_id, key, default=None):
        """
        get a property from the provided page id

        Performs an API call to acquire a property held on a specific page.
        This call can returns the page properties dictionary if found;
        otherwise ``None`` will be returned.

        Args:
            page_id: the page identifier
            key: the property key
            default (optional): default value if no property exists

        Returns:
            the property value
        """

        props = default

        if page_id:
            try:
                if self.api_mode == 'v2':
                    prop_path = f'{self.APIV2}pages/{page_id}/properties'
                    rsp = self.rest.get(prop_path, {
                        'key': key,
                    })
                    if rsp['results']:
                        props = rsp['results'][0]
                else:
                    prop_path = f'{self.APIV1}content/{page_id}/property/{key}'
                    props = self.rest.get(prop_path)
            except ConfluenceBadApiError as ex:
                if ex.status_code != 404:
                    raise

        return props

    def store_attachment(self, page_id, name, data, mimetype, hash_, force=False):
        """
        request to store an attachment on a provided page

        Makes a request to a Confluence instance to either publish a new
        attachment or update an existing attachment. If the attachment's hash
        matches the tracked hash (via the comment field) of an existing
        attachment, this call will assume the attachment is already published
        and will return (unless forced).

        Args:
            page_id: the identifier of the page to attach to
            name: the attachment name
            data: the attachment data
            mimetype: the mime type of this attachment
            hash_: the hash of the attachment
            force (optional): force publishing if exists (defaults to False)

        Returns:
            the attachment identifier
        """
        HASH_KEY = 'SCB_KEY'
        uploaded_attachment_id = None

        if self.dryrun:
            attachment = None
        else:
            _, attachment = self.get_attachment(page_id, name)

        # check if attachment (of same hash) is already published to this page
        comment = None
        if attachment:
            if self.api_mode == 'v2':
                comment = attachment.get('comment')
            elif 'metadata' in attachment:
                metadata = attachment['metadata']
                comment = metadata.get('comment')

        if not force and comment:
            parts = comment.split(HASH_KEY + ':', 1)
            if len(parts) > 1:
                tracked_hash = ''.join(parts[1].split())
                if hash_ == tracked_hash:
                    logger.verbose(f'attachment ({name}) is already '
                        'published to document with same hash')
                    return attachment['id']

        if self.dryrun:
            if not attachment:
                self._dryrun('adding new attachment ' + name)
                return None

            self._dryrun('updating existing attachment', attachment['id'])
            return attachment['id']

        if self.onlynew and attachment:
            self._onlynew('skipping existing attachment', attachment['id'])
            return attachment['id']

        # publish attachment
        try:
            # split hash comment into chunks to minimize rendering issues with a
            # single one-world-long-hash value
            hash_ = f'{HASH_KEY}:{hash_}'
            chunked_hash = '\n'.join(
                [hash_[i:i + 16] for i in range(0, len(hash_), 16)])

            data = {
                'comment': chunked_hash,
                'file': (name, data, mimetype),
            }

            if not self.notify:
                # using str over bool to support requests pre-v2.19.0
                data['minorEdit'] = 'true'

            if not attachment:
                url = f'{self.APIV1}content/{page_id}/child/attachment'

                try:
                    rsp = self.rest.post(url, None, files=data)
                    uploaded_attachment_id = rsp['results'][0]['id']
                except ConfluenceBadApiError as ex:
                    # file type restricted? generate a warning
                    #
                    # Be a bit flexible in the situation where a specific
                    # file type is restricted. Instead of hard failing, only
                    # generate a warning that an attachment could not be added.
                    # This has been observed for environments using Akeles
                    # Consulting's "Attachment Checker for Confluence".
                    if 'file type is not allowed' in str(ex):
                        fail_msg = f'unable to upload attachment "{name}" '
                        fail_msg += f'(page: "{self._name_cache[page_id]}"); '
                        fail_msg += 'this Confluence instance restricts this '
                        fail_msg += f'file extension ({mimetype})'
                        logger.warn(fail_msg)
                        return None

                    if ex.status_code != 503:
                        raise

                    # retry 503-failed new attachment uploads
                    #
                    # It has been observed on Confluence Cloud that in some
                    # cases when a user publishes a new attachment to a page
                    # (and maybe specifically attached to a newly created page),
                    # Confluence may report a 503 error. The behaviour is odd
                    # since Confluence does partially process the new
                    # attachment (a viewable entry on the page's list of
                    # attachments), but the data for the attachment entry is
                    # corrupted. And in a next publish attempt, since the
                    # comment hash is unchanged, this extension will not
                    # attempt to re-upload. To help prevent this case, if a 503
                    # error state is detected, check to see if the attachment
                    # entry was created with corrupted data (i.e. can we query
                    # for an existing attachment). If we find it, re-attempt
                    # to publish the attachment.
                    logger.info('attachment failure (503); retrying...')
                    time.sleep(0.5)
                    _, attachment = self.get_attachment(page_id, name)

            if attachment:
                url = '{}content/{}/child/attachment/{}/data'.format(
                    self.APIV1, page_id, attachment['id'])
                rsp = self.rest.post(url, None, files=data)
                uploaded_attachment_id = rsp['id']

            if not self.watch:
                self.rest.delete(f'{self.APIV1}user/watch/content',
                    uploaded_attachment_id)
        except ConfluencePermissionError as ex:
            msg = (
                'Publish user does not have permission to add an '
                'attachment to the configured space.'
            )
            raise ConfluencePermissionError(msg) from ex

        return uploaded_attachment_id

    def store_page(self, page_name, data, parent_id=None):
        """
        request to store page information to a confluence instance

        Performs a request which will attempt to store the provided page
        information and publish it to either a new page with the provided page
        name or update an existing page with a matching page name. Pages will be
        published at the root of a Confluence space unless a provided parent
        page identifier is provided.

        Args:
            page_name: the page title to use on the updated page
            data: the page data to apply
            parent_id (optional): the id of the ancestor to use
        """
        uploaded_page_id = None

        if self.config.confluence_adv_trace_data:
            logger.trace('data', data['content'])

        if self.dryrun:
            _, page = self.get_page(page_name, 'version,ancestors')

            if not page:
                self._dryrun('adding new page ' + page_name)
                return None

            misc = ''
            if parent_id and 'ancestors' in page:
                if not any(a['id'] == parent_id for a in page['ancestors']):
                    desc = ''
                    if parent_id in self._name_cache:
                        desc = f': {self._name_cache[parent_id]} ({parent_id})'
                    misc += f'[new parent page{desc}]'

            self._dryrun('updating existing page', page['id'], misc)
            return page['id']

        # fetch the page data
        # (expand on certain fields that may be required)
        expand = 'version'
        if parent_id:
            expand += ',ancestors'
        if self.append_labels or self.config.confluence_global_labels:
            expand += ',metadata.labels'
        if data.get('full-width'):
            expand += ',metadata.properties.content_appearance_published'
        if data.get('editor'):
            expand += ',metadata.properties.editor'

        _, page = self.get_page(page_name, expand=expand)

        # if the page is not found, but it determined to be an archived page,
        # Confluence Cloud does not appear to support moving/updating an
        # archived page back into a `current` mode -- instead, try to delete
        # the archived page before generating a new page
        if not page:
            _, page = self.get_page(page_name, expand=expand, status='archived')
            if page:
                self.remove_page(page['id'])
                page = None

        if self.onlynew and page:
            self._onlynew('skipping existing page', page['id'])
            return page['id']

        # fetch known properties (associated with this extension) from the page
        page_id = page['id'] if page else None
        cb_props = self.get_page_property(page_id, CB_PROP_KEY, {
            'key': CB_PROP_KEY,
            'value': {},
        })

        # calculate the hash for a page; we will first use this to check if
        # there is a update to apply, and if we do need to update, we will
        # add this value into the page's properties
        new_page_hash = ConfluenceUtil.hash(data['content'])

        # check if we have to force a page update
        force_publish = self.config.confluence_publish_force
        if page and not force_publish:
            metadata = page.get('metadata', {})
            meta_props = metadata.get('properties', {})

            # if the parent page has changed, force an update
            if parent_id:
                parent_changed = True
                last_ancestor = page.get('ancestors', [])[-1:]
                if last_ancestor:
                    if last_ancestor[0].get('id') == str(parent_id):
                        parent_changed = False

                if parent_changed:
                    logger.verbose(f'parent changed: {page_name}')
                    force_publish = True

            # if we are missing any global variables, force publish
            if self.config.confluence_global_labels:
                expected_labels = set(self.config.confluence_global_labels)
                existing_labels = [lbl.get('name')
                    for lbl in page.get('metadata', {}).get(
                        'labels', {}).get('results', {})
                ]
                if expected_labels.difference(existing_labels):
                    logger.verbose(f'labels missing: {page_name}')
                    force_publish = True

            # if instance supports appearance changes and the appearance
            # looks to be changed, force publish
            cap_props = meta_props.get('content-appearance-published', {})
            if cap_props and data.get('full-width'):
                current_appearance = cap_props.get('value')
                if data.get('full-width') != current_appearance:
                    logger.verbose(f'appearance changed: {page_name}')
                    force_publish = True

            # if instance supports editors and the editor to be changed,
            # force publish
            editor_props = meta_props.get('editor', {})
            if editor_props and data.get('editor'):
                current_editor = editor_props.get('value')
                if data.get('editor') != current_editor:
                    logger.verbose(f'editor changed: {page_name}')
                    force_publish = True

        # if we are not force uploading, check if the new page hash matches
        # the remote hash; if so, do not publish
        if not force_publish:
            remote_hash = cb_props['value'].get('hash')
            if new_page_hash == remote_hash:
                logger.verbose(f'no changes in page: {page_name}')
                return page['id']

        try:
            # new page
            if not page:
                new_page = self._build_page(page_name, data)

                self._populate_labels(new_page, data['labels'])

                new_labels = None
                new_prop_requests = []
                if self.api_mode == 'v2':
                    # use newer space id refrence for v2
                    new_page.pop('space', None)
                    new_page['spaceId'] = self.space_id

                    # strip out metadata updates that need to be processed
                    # in a different request
                    new_metadata = new_page.pop('metadata', None)
                    new_labels = new_metadata.get('labels')
                    new_meta_props = new_metadata.setdefault('properties', {})

                    for prop_key, entry in new_meta_props.items():
                        new_prop = {
                            'key': prop_key,
                            'value': entry['value'],
                        }

                        new_prop_requests.append(new_prop)

                # configure parent page for this new page
                if parent_id:
                    if self.api_mode == 'v2':
                        new_page['parentId'] = parent_id
                    else:
                        new_page['ancestors'] = [{'id': parent_id}]

                try:
                    if self.api_mode == 'v2':
                        build_path = f'{self.APIV2}pages'
                    else:
                        build_path = f'{self.APIV1}content'

                    rsp = self.rest.post(build_path, new_page)
                except ConfluenceBadApiError as ex:
                    if str(ex).find('CDATA block has embedded') != -1:
                        raise ConfluenceUnexpectedCdataError from ex

                    # Check if Confluence reports that the new page request
                    # fails, indicating it already exists. This is usually
                    # (outside of possible permission use cases) that the page
                    # name's casing does not match. In this case, attempt to
                    # re-check for the page in a case-insensitive fashion. If
                    # found, attempt to perform an update request instead.
                    if str(ex).find('title already exists') == -1:
                        raise

                    logger.verbose(f'title already exists for page {page_name}')

                    _, page = self.get_page_case_insensitive(page_name)
                    if not page:
                        # If here, the original `get_page` call failed to find
                        # a page with a specific name and then a retry with
                        # `get_page_case_insensitive` also failed again, even
                        # though Confluence reports the title already exists.
                        # At this time, this appears to be limited to users
                        # who use `confluence_page_search_mode` with `search`.
                        # There appears to be some scenarios where a Confluence
                        # instance will not report the existence of a deleted
                        # page when queried via CQL, which prevents us from
                        # reviving a page from the dead.
                        raise

                    if self.onlynew:
                        self._onlynew('skipping existing page', page['id'])
                        return page['id']
                else:
                    if 'id' not in rsp:
                        api_err = (
                            'Confluence reports a successful page '
                            'creation; however, provided no identifier.\n\n'
                        )
                        try:
                            json_data = json.dumps(rsp, indent=2)
                            api_err += f'DATA: {json_data}'
                        except TypeError:
                            api_err += 'DATA: (not-or-invalid-json)'
                        raise ConfluenceBadApiError(-1, api_err)

                    uploaded_page_id = rsp['id']

                    # we have properties we would like to apply, but we cannot
                    # just create new ones if Confluence already created ones
                    # implicitly in the new page update -- we will need to
                    # query the page for any of these properties are form
                    # either new or update requests
                    self._update_page_properties(rsp['id'], new_prop_requests)

                    # if we have labels and this is a non-cloud instance,
                    # initial labels need to be applied in their own request
                    if not self.cloud and self.api_mode == 'v1':
                        new_labels = new_page['metadata']['labels']

                    # add new labels if we have any to force add
                    if new_labels:
                        url = f'{self.APIV1}content/{uploaded_page_id}/label'
                        self.rest.post(url, new_labels)

            # update existing page
            if page:
                self._update_page(page, page_name, data, parent_id=parent_id)
                uploaded_page_id = page['id']

        except ConfluencePermissionError as ex:
            msg = (
                'Publish user does not have permission to add page '
                'content to the configured space.'
            )
            raise ConfluencePermissionError(msg) from ex

        # update page hash
        cb_props['value']['hash'] = new_page_hash

        # perform any required post-page update actions
        self._post_page_actions(uploaded_page_id, cb_props)

        return uploaded_page_id

    def store_page_by_id(self, page_name, page_id, data):
        """
        request to store page information on the page with a matching id

        Performs a request which will attempt to store the provided page
        information and publish it to a page with the provided ``page_id``.

        Args:
            page_name: the page title to use on the updated page
            page_id: the id of the page to update
            data: the page data to apply
        """
        assert page_id

        if self.onlynew:
            self._onlynew('skipping explicit page update for', page_id)
            return page_id

        if self.dryrun:
            _, page = self.get_page_by_id(page_id)

            if not page:
                self._dryrun('unable to find page with id', page_id)
                return None

            self._dryrun('updating existing page', page_id)
            return page_id

        expand = 'version'
        if self.append_labels:
            expand += ',metadata.labels'

        try:
            _, page = self.get_page_by_id(page_id, expand=expand)
        except ConfluenceBadApiError as ex:
            if str(ex).find('No content found with id') == -1:
                raise
            raise ConfluenceMissingPageIdError(self.space_key, page_id) from ex

        # fetch known properties (associated with this extension) from the page
        cb_props = self.get_page_property(page_id, CB_PROP_KEY, {
            'key': CB_PROP_KEY,
            'value': {},
        })

        # calculate the hash for a page; we will first use this to check if
        # there is a update to apply, and if we do need to update, we will
        # add this value into the page's properties
        new_page_hash = ConfluenceUtil.hash(data['content'])

        # if we are not force uploading, check if the new page hash matches
        # the remote hash; if so, do not publish
        if not self.config.confluence_publish_force:
            remote_hash = cb_props['value'].get('hash')
            if new_page_hash == remote_hash:
                logger.verbose(f'no changes in page: {page_name}')
                return page_id

        try:
            self._update_page(page, page_name, data)
        except ConfluencePermissionError as ex:
            msg = (
                'Publish user does not have permission to add page '
                'content to the configured space.'
            )
            raise ConfluencePermissionError(msg) from ex

        # update page hash
        cb_props['value']['hash'] = new_page_hash

        # perform any required post-page update actions
        self._post_page_actions(page_id, cb_props)

        return page_id

    def _update_page_properties(self, page_id, properties):
        """
        update properties on a specific page

        Perform a request to update properties on a page. This call will
        fetch an existing property value to determine if an update is
        required.

        Args:
            page_id: the id of the page to update
            properties: the properties to update
        """

        # always wait a little moment before updating properties on
        # cloud -- it seems to take a moment to complete creating or
        # updating properties after we build process a page, and we want
        # to avoid a conflict (409) if possible
        if self.cloud:
            if not self.config.confluence_adv_disable_cloud_prop_delay:
                time.sleep(0.5)

        # we have properties we would like to apply, but we cannot
        # just create new ones if Confluence already created ones
        # implicitly in the new page update -- we will need to
        # query the page for any of these properties are form
        # either new or update requests
        for prop in properties:
            # we permit two attempts to update a property as it has been
            # observed when we create a new page, Confluence may build a
            # desired property that an initial `get_page_property` will not
            # return (timing issue); so if we get a conflict error (409),
            # we will retry a fetch/update again
            MAX_ATTEMPTS_TO_UPDATE_PROPERTY = 2
            attempt = 1
            while attempt <= MAX_ATTEMPTS_TO_UPDATE_PROPERTY:
                prop_key = prop['key']
                prop_entry = self.get_page_property(page_id, prop_key, {
                    'value': None,
                })

                # ignore if the property already matches the desired
                # value
                if prop_entry['value'] == prop['value']:
                    break

                prop_entry['value'] = prop['value']

                try:
                    self.store_page_property(
                        page_id,
                        prop_key,
                        prop_entry,
                    )
                except ConfluenceBadApiError as ex:
                    if ex.status_code != 409:
                        raise

                    # retry on conflict
                    logger.info('property update conflict; retrying...')

                    attempt += 1
                else:
                    break

    def store_page_property(self, page_id, key, data):
        """
        request to store properties on a page to a confluence instance

        Performs a request which will attempt to store properties on a
        provided page.

        Args:
            page_id: the id of the page to update
            key: the property key
            data: the properties data to apply
        """

        # set or bump the known version on this property
        prop_version = data.setdefault('version', {})
        last_props_version = int(prop_version.get('number', 0))
        prop_version['number'] = last_props_version + 1

        if self.api_mode == 'v2':
            # v2 api expects the key in the body
            data['key'] = key
            property_path = f'{self.APIV2}pages/{page_id}/properties'

            if prop_version['number'] == 1:
                self.rest.post(property_path, data)
            else:
                prop_id = data.pop('id')
                self.rest.put(property_path, prop_id, data)
        else:
            property_path = f'{self.APIV1}content/{page_id}/property'
            self.rest.put(property_path, key, data)

    def remove_attachment(self, id_):
        """
        request to remove an attachment

        Makes a request to a Confluence instance to remove an existing
        attachment.

        Args:
            id_: the attachment
        """
        if self.dryrun:
            self._dryrun('removing attachment', id_)
            return

        if self.onlynew:
            self._onlynew('attachment removal restricted', id_)
            return

        if self.api_mode == 'v2':
            delete_path = f'{self.APIV2}attachments'
        else:
            delete_path = f'{self.APIV1}content'

        try:
            self.rest.delete(delete_path, id_)
        except ConfluencePermissionError as ex:
            msg = (
                'Publish user does not have permission to delete '
                'from the configured space.'
            )
            raise ConfluencePermissionError(msg) from ex

    def remove_page(self, page_id):
        if self.dryrun:
            self._dryrun('removing page', page_id)
            return

        if self.onlynew:
            self._onlynew('page removal restricted', page_id)
            return

        if self.api_mode == 'v2':
            delete_path = f'{self.APIV2}pages'
        else:
            delete_path = f'{self.APIV1}content'

        try:
            self.rest.delete(delete_path, page_id)
        except ConfluenceBadApiError as ex:
            # Check if Confluence reports that this content does not exist. If
            # so, we want to suppress the API error. This is most likely a
            # result of a Confluence instance reporting a page descendant
            # identifier which no longer exists (possibly a caching issue).
            if str(ex).find('No content found with id') == -1:
                raise

            logger.verbose(f'ignore missing delete for page id: {page_id}')
        except ConfluencePermissionError as ex:
            msg = (
                'Publish user does not have permission to delete '
                'from the configured space.'
            )
            raise ConfluencePermissionError(msg) from ex

    def restrict_ancestors(self, ancestors):
        """
        restrict the provided ancestors from being changed

        Registers the provided set of ancestors from being used when page
        updates will move the location of a page. This is a pre-check update
        requests so that a page cannot be flagged as a descendant of itself
        (where Confluence self-hosted instances may not report an ideal error
        message).

        Args:
            ancestors: the ancestors to check against
        """
        self._ancestors_cache = ancestors

    def update_space_home(self, page_id):
        if not page_id:
            return

        if self.dryrun:
            self._dryrun('updating space home to', page_id)
            return

        if self.onlynew:
            self._onlynew('space home updates restricted')
            return

        if self.api_mode == 'v2':
            page = self.rest.get(f'{self.APIV2}pages/{page_id}')
        else:
            page = self.rest.get(f'{self.APIV1}content/{page_id}', None)
        try:
            self.rest.put(f'{self.APIV1}space', self.space_key, {
                'key': self.space_key,
                'name': self.space_display_name,
                'homepage': page,
                'type': self.space_type,
            })
        except ConfluencePermissionError as ex:
            msg = (
                'Publish user does not have permission to update '
                "space's homepage."
            )
            raise ConfluencePermissionError(msg) from ex

    def _build_page(self, page_name, data):
        """
        build a page entity used for a new or updated page event

        Will return a dictionary containing the minimum required information
        needed for a `put` event when publishing a new or update page.

        Args:
            page_name: the page title to use on the page
            data: the page data to apply
        """
        page = {
            'type': 'page',
            'title': page_name,
            'body': {
                'storage': {
                    'representation': 'storage',
                    'value': data['content'],
                },
            },
            'metadata': {
                'properties': {},
            },
            'space': {
                'key': self.space_key,
            },
            'version': {
                'number': 1,
                'message': self.config.confluence_version_comment,
            },
        }

        if data.get('editor'):
            page['metadata']['properties']['editor'] = {
                'value': data['editor'],
            }

        if data.get('full-width'):
            page['metadata']['properties']['content-appearance-published'] = {
                'value': data['full-width'],
            }

        return page

    def _next_page_fields(self, rsp, fields, offset):
        """
        extract next query fields from a response

        For paged search requests, Confluence can report a "next" link to use
        for the "next page". This call can be used to extract the query options
        provided by Confluence that should be included in a next request.

        Original CQL search calls would use a "start" offset to manage pages.
        Confluence Cloud (at least) has not used the `start` field for search
        options for some time [1]. Note on Confluence Data Center, the "start"
        offset may still be used.

        [1]: https://developer.atlassian.com/cloud/confluence/change-notice-moderize-search-rest-apis/

        Args:
            rsp: the response to pull a next query from
            fields: the recommended search fields
            offset: the recommended start offset

        Returns:
            the extract query fields
        """

        reported_links = rsp.get('_links')
        if reported_links:
            next_query = reported_links.get('next')
            if next_query:
                try:
                    parsed = urlparse(next_query)
                    return dict(parse_qsl(parsed.query))
                except ValueError:
                    return None

                return None

        # If no next link, on Confluence Cloud this would mean there are no
        # pages left. On Confluence Data Center, a next link may not be
        # provided (we try to assume it does, but most likely will use the
        # old paging method). If we detect that a "totalSize" field is
        # provided, the instance should support the "start" field.
        if not self.cloud:
            total_sz = rsp.get('totalSize')
            if total_sz and total_sz > offset:
                sub_search_fields = dict(fields)
                sub_search_fields['start'] = offset
                return sub_search_fields

        return None

    def _post_page_actions(self, page_id, cb_props):
        """
        post page actions

        Perform additional actions needed after creating or updating a page.

        Args:
            page_id: the identifier of the new/updated page
            cb_props: confluence builder page properties
        """

        # push an updated to confluence builder property which includes an
        # updated hash value
        self._update_page_properties(page_id, [cb_props])

        # ensure remove any watch flags on the update if watching is disabled
        if not self.watch:
            self.rest.delete(f'{self.APIV1}user/watch/content', page_id)

    def _update_page(self, page, page_name, data, parent_id=None):
        """
        build a page update and publish it to the confluence instance

        This call is invoked when the updated page data is ready to be published
        to a Confluence instance (i.e. pre-checks like "dry-run" mode have been
        completed).

        Args:
            page: the page data from confluence to update
            page_name: the page title to use on the update page
            data: the new page data to apply
            parent_id (optional): the id of the ancestor to use
        """
        last_version = int(page['version']['number'])

        update_page = self._build_page(page_name, data)
        update_page['id'] = page['id']
        update_page['version']['number'] = last_version + 1

        labels = list(data['labels'])
        if self.append_labels:
            labels.extend([lbl.get('name')
                for lbl in page.get('metadata', {}).get(
                    'labels', {}).get('results', {})
            ])

        self._populate_labels(update_page, labels)

        if not self.notify:
            update_page['version']['minorEdit'] = True

        if parent_id:
            if page['id'] in self._ancestors_cache:
                raise ConfluencePublishAncestorError(page_name)

            update_page['ancestors'] = [{'id': parent_id}]

            if page['id'] == parent_id:
                raise ConfluencePublishSelfAncestorError(page_name)

        # zero-id parent ~ a hint to remove the ancestor
        # (looks like setting a value of "1" is a way to "clear" the option)
        elif parent_id is not None:
            update_page['ancestors'] = [{'id': '1'}]

        # if this is an api v2 mode, prepare any extra requests needed for
        # populating ancestors or metadata information
        pending_new_labels = []
        pending_prop_requests = []
        if self.api_mode == 'v2':
            orig_metadata = page.get('metadata', {})
            update_metadata = update_page.pop('metadata', {})

            # configure parent page for this page update
            #
            # For v2, we need to strip out `ancestors` and place it with an
            # expected `parentId` value.
            ancestors_request = update_page.pop('ancestors', None)
            if ancestors_request:
                update_page['parentId'] = ancestors_request[0]['id']

            # extract labels to set
            pending_new_labels = update_metadata.get('labels')

            # build a list of property creation/update requests needed
            #
            # This call will look at the `update_page` page for newly set
            # properties needed to be set. When cycling through updated
            # properties, we will also compare against the original page's
            # properties (`page`) to see if properties are being created or
            # updated, where we can track the identifier for updated entries
            # as well as pre-populating a version bump. This will also check
            # if each property value to be updated has changed. If there is
            # no change to a given property, it will be ignored.
            orig_meta_props = orig_metadata.setdefault('properties', {})
            update_meta_props = update_metadata.setdefault('properties', {})

            for prop_key, entry in update_meta_props.items():
                updated_prop = {
                    'key': prop_key,
                    'value': entry['value'],
                    'version': {
                        'number': 1,
                    },
                }

                orig_entry = orig_meta_props.get(prop_key, None)

                # if an original entry exists, make sure we bump the version
                # number for this property; note that the value may be set to
                # `None`, where this extension requested information about
                # a property, but Confluence does not have one defined for
                # a page (i.e. so we treat it as new; no version bump)
                if orig_entry and orig_entry.get('value') is not None:
                    if orig_entry['value'] == entry['value']:
                        continue

                    updated_prop['id'] = orig_entry['id']
                    last_props_version = int(orig_entry['version']['number'])
                    updated_prop['version']['number'] = last_props_version + 1

                pending_prop_requests.append(updated_prop)

        if self.api_mode == 'v2':
            update_path = f'{self.APIV2}pages'
        else:
            update_path = f'{self.APIV1}content'

        update_page['status'] = 'current'
        try:
            self.rest.put(update_path, page['id'], update_page)
        except ConfluenceBadApiError as ex:
            if str(ex).find('CDATA block has embedded') != -1:
                raise ConfluenceUnexpectedCdataError from ex

            if 'unreconciled' in str(ex):
                raise ConfluenceUnreconciledPageError(
                    page_name, page['id'], self.server_url, ex) from ex

        # post-update requests (api v2 mode)
        update_page_id = update_page['id']

        self._update_page_properties(update_page_id, pending_prop_requests)

        # add any new labels
        if pending_new_labels:
            url = f'{self.APIV1}content/{update_page_id}/label'
            self.rest.post(url, pending_new_labels)

    def _dryrun(self, msg, id_=None, misc=''):
        """
        log a dry run mode message

        Accepts a message to be printed out when running in "dry run" mode. A
        message may be accompanied by an identifier which should be translated
        to a name (if possible).

        Args:
            msg: the message
            id_ (optional): identifier (name mapping) associated with the message
            misc (optional): additional information to append
        """
        s = '[dryrun] '
        s += msg
        if id_ and id_ in self._name_cache:
            s += ' ' + self._name_cache[id_]
        if id_:
            s += f' ({id_})'
        if misc:
            s += ' ' + misc
        logger.info(s + min(80, 80 - len(s)) * ' ')  # 80c-min clearing

    def _onlynew(self, msg, id_=None):
        """
        log an only-new mode message

        Accepts a message to be printed out when running in "only-new" mode. A
        message may be accompanied by an identifier which should be translated
        to a name (if possible).

        Args:
            msg: the message
            id_ (optional): identifier (name mapping) associated with the message
        """
        s = '[only-new] '
        s += msg
        if id_ and id_ in self._name_cache:
            s += ' ' + self._name_cache[id_]
        if id_:
            s += f' ({id_})'
        logger.info(s + min(80, 80 - len(s)) * ' ')  # 80c-min clearing

    def _populate_labels(self, page, labels):
        """
        populate a page with label metadata information

        Accepts a page definition (new or existing page) and populates the
        metadata portion with the provided label data.

        Args:
            page: the page
            labels: the labels to set
        """
        metadata = page.setdefault('metadata', {})
        metadata['labels'] = [{'name': v} for v in set(labels)]
