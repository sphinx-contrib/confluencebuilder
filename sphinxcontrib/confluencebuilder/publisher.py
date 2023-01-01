# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2017-2023 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)

See also:
    Confluence Cloud REST API Reference
    https://docs.atlassian.com/confluence/REST/latest/
"""

from sphinx.util.logging import skip_warningiserror
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceBadApiError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceBadServerUrlError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceBadSpaceError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceConfigurationError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceMissingPageIdError
from sphinxcontrib.confluencebuilder.exceptions import ConfluencePermissionError
from sphinxcontrib.confluencebuilder.exceptions import ConfluencePublishAncestorError
from sphinxcontrib.confluencebuilder.exceptions import ConfluencePublishSelfAncestorError
from sphinxcontrib.confluencebuilder.exceptions import ConfluenceUnreconciledPageError
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger as logger
from sphinxcontrib.confluencebuilder.rest import Rest
import json
import logging
import time


class ConfluencePublisher:
    def __init__(self):
        self.cloud = None
        self.editor = None
        self.space_display_name = None
        self.space_type = None
        self._ancestors_cache = set()
        self._name_cache = {}

    def init(self, config, cloud=None):
        self.cloud = cloud
        self.config = config
        self.append_labels = config.confluence_append_labels
        self.debug = config.confluence_publish_debug
        self.dryrun = config.confluence_publish_dryrun
        self.editor = config.confluence_editor
        self.notify = not config.confluence_disable_notifications
        self.onlynew = config.confluence_publish_onlynew
        self.parent_id = config.confluence_parent_page_id_check
        self.parent_ref = config.confluence_parent_page
        self.server_url = config.confluence_server_url
        self.space_key = config.confluence_space_key
        self.watch = config.confluence_watch

        # append labels by default
        if self.append_labels is None:
            self.append_labels = True

        # if debugging, enable requests (urllib3) logging
        if self.debug:
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            rlog = logging.getLogger('requests.packages.urllib3')
            rlog.setLevel(logging.DEBUG)

    def connect(self):
        self.rest_client = Rest(self.config)
        server_url = self.config.confluence_server_url

        try:
            rsp = self.rest_client.get('space', {
                'spaceKey': self.space_key,
                'limit': 1
            })
        except ConfluenceBadApiError as e:
            raise ConfluenceBadServerUrlError(server_url, e)

        # if no size entry is provided, this a non-Confluence API server
        if 'size' not in rsp:
            raise ConfluenceBadServerUrlError(server_url,
                'server did not provide an expected response (no size)')

        # handle if the provided space key was not found
        if rsp['size'] == 0:
            if self.debug:
                logger.info('''could not find the configured space

(notice to debugging user)
Either the space does not exist, or the user does not have permission to see
the space. Another space search will be performed to sanity check the
configuration to see if a similar space key exists, which can hint to a user
that the space key may be misconfigured. If the following search request
results in an access restriction, it is most likely that the authentication
options are not properly configured, even if the previous search request
reported a success (which can be permitted for anonymous users).
''')

            extra_desc = ''

            # If the space key was not found, attempt to search for the space
            # based off its descriptive name. If something is found, hint to the
            # user to use a space's key value instead.
            search_fields = {
                'cql': 'type=space and space.title~"' + self.space_key + '"',
                'limit': 2,
            }
            rsp = self.rest_client.get('search', search_fields)

            if rsp['size'] == 1:
                detected_space = rsp['results'][0]
                space_key = detected_space['space']['key']
                space_name = detected_space['title']
                extra_desc = \
                    '''\n\n''' \
                    '''There appears to be a space '{0}' which has a name ''' \
                    ''''{1}'. Did you mean to use this space?\n''' \
                    '''\n''' \
                    '''   confluence_space_key = '{0}'\n''' \
                    ''''''.format(space_key, space_name)

            elif rsp['size'] > 1:
                extra_desc = \
                    '''\n\n''' \
                    '''Multiple spaces have been detected which use the ''' \
                    '''name '{}'. The unique key of the space should be ''' \
                    '''used instead. See also:\n\n''' \
                    '''   https://support.atlassian.com/confluence-cloud/docs/choose-a-space-key/\n''' \
                    ''''''.format(self.space_key)

            pw_set = bool(self.config.confluence_server_pass)
            token_set = bool(self.config.confluence_publish_token)

            raise ConfluenceBadSpaceError(
                self.space_key,
                self.config.confluence_server_user,
                pw_set,
                token_set,
                extra_desc)

        # sanity check that we have any result
        if 'results' not in rsp or not rsp['results']:
            raise ConfluenceBadServerUrlError(server_url,
                'server did not provide an expected response (no results)')

        result = rsp['results'][0]

        if not isinstance(result, dict) or not result.get('name'):
            raise ConfluenceBadServerUrlError(server_url,
                'server did not provide an expected response (no name)')

        # track required space information
        self.space_display_name = result['name']
        self.space_type = result['type']

    def disconnect(self):
        self.rest_client.close()

    def archive_page(self, page_id):
        if self.dryrun:
            self._dryrun('archive page', page_id)
            return
        elif self.onlynew:
            self._onlynew('page archive restricted', page_id)
            return

        try:
            data = {
                'pages': [{'id': page_id}],
            }

            rsp = self.rest_client.post('content/archive', data)
            longtask_id = rsp['id']

            # wait for the archiving of the page to complete
            MAX_WAIT_FOR_PAGE_ARCHIVE = 4  # ~2 seconds
            attempt = 1
            while attempt <= MAX_WAIT_FOR_PAGE_ARCHIVE:
                time.sleep(0.5)

                rsp = self.rest_client.get('longtask/{}'.format(longtask_id))
                if rsp['finished']:
                    break

                attempt += 1
                if attempt > MAX_WAIT_FOR_PAGE_ARCHIVE:
                    raise ConfluenceBadApiError(
                        -1, 'timeout waiting for archive completion')
        except ConfluencePermissionError:
            raise ConfluencePermissionError(
                """Publish user does not have permission to archive """
                """from the configured space."""
            )

    def archive_pages(self, page_ids):
        if self.dryrun:
            self._dryrun('archiving pages', ', '.join(page_ids))
            return
        elif self.onlynew:
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
            self.rest_client.post('content/archive', data)

        except ConfluencePermissionError:
            raise ConfluencePermissionError(
                """Publish user does not have permission to archive """
                """from the configured space."""
            )

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

        _, page = self.get_page_by_id(page_id, 'ancestors')

        if 'ancestors' in page:
            for ancestor in page['ancestors']:
                ancestors.add(ancestor['id'])

        return ancestors

    def get_base_page_id(self):
        base_page_id = self.config.confluence_publish_root

        if not self.parent_ref:
            return base_page_id

        if isinstance(self.parent_ref, int):
            base_page_id, page = self.get_page_by_id(self.parent_ref)

            if not page:
                raise ConfluenceConfigurationError(
                    '''Configured parent page identifier does not exist.''')

            return base_page_id

        rsp = self.rest_client.get('content', {
            'type': 'page',
            'spaceKey': self.space_key,
            'title': self.parent_ref,
            'status': 'current'
        })
        if rsp['size'] == 0:
            raise ConfluenceConfigurationError(
                '''Configured parent page name does not exist.''')
        page = rsp['results'][0]
        if self.parent_id and page['id'] != str(self.parent_id):
            raise ConfluenceConfigurationError("""Configured parent """
                """page ID and name do not match.""")
        base_page_id = page['id']
        self._name_cache[base_page_id] = self.parent_ref

        if not base_page_id and self.parent_id:
            raise ConfluenceConfigurationError("""Unable to find the """
                """parent page matching the ID or name provided.""")

        return base_page_id

    def get_descendants(self, page_id):
        """
        generate a list of descendants

        Queries the configured Confluence instance for a set of descendants for
        the provided `page_id` or (if set to `None`) the configured space.

        Args:
            page_id: the ancestor to search on (if not `None`)

        Returns:
            the descendants
        """
        descendants = set()

        if page_id:
            search_fields = {'cql': 'ancestor=' + str(page_id)}
        else:
            search_fields = {'cql': 'space="' + self.space_key +
                '" and type=page'}

        # Configure a larger limit value than the default (no provided
        # limit defaults to 25). This should reduce the number of queries
        # needed to fetch a complete descendants set (for larger sets).
        search_fields['limit'] = 1000

        rsp = self.rest_client.get('content/search', search_fields)
        idx = 0
        while rsp['size'] > 0:
            for result in rsp['results']:
                descendants.add(result['id'])
                self._name_cache[result['id']] = result['title']

            if rsp['size'] != rsp['limit']:
                break

            idx += int(rsp['limit'])
            sub_search_fields = dict(search_fields)
            sub_search_fields['start'] = idx
            rsp = self.rest_client.get('content/search', sub_search_fields)

        return descendants

    def get_descendants_compat(self, page_id):
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

        Returns:
            the descendants
        """
        visited_pages = set()

        def find_legacy_pages(page_id, pages):
            descendants = self.get_descendants(page_id)
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

        url = 'content/{}/child/attachment'.format(page_id)
        rsp = self.rest_client.get(url, {
            'filename': name,
        })

        if rsp['size'] != 0:
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

        url = 'content/{}/child/attachment'.format(page_id)
        search_fields = {}

        # Configure a larger limit value than the default (no provided
        # limit defaults to 25). This should reduce the number of queries
        # needed to fetch a complete attachment set (for larger sets).
        search_fields['limit'] = 1000

        rsp = self.rest_client.get(url, search_fields)
        idx = 0
        while rsp['size'] > 0:
            for result in rsp['results']:
                attachment_info[result['id']] = result['title']
                self._name_cache[result['id']] = result['title']

            if rsp['size'] != rsp['limit']:
                break

            idx += int(rsp['limit'])
            sub_search_fields = dict(search_fields)
            sub_search_fields['start'] = idx
            rsp = self.rest_client.get(url, sub_search_fields)

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

        rsp = self.rest_client.get('content', {
            'type': 'page',
            'spaceKey': self.space_key,
            'title': page_name,
            'status': status,
            'expand': expand,
        })

        if rsp['size'] != 0:
            page = rsp['results'][0]
            page_id = page['id']
            self._name_cache[page_id] = page_name

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

        page = self.rest_client.get('content/{}'.format(page_id), {
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
        search_fields['limit'] = 1000

        rsp = self.rest_client.get('content/search', search_fields)
        idx = 0
        while rsp['size'] > 0:
            for result in rsp['results']:
                result_title = result['title']
                if page_name == result_title.lower():
                    page_id, page = self.get_page(result_title)
                    break

            if page_id or rsp['size'] != rsp['limit']:
                break

            idx += int(rsp['limit'])
            sub_search_fields = dict(search_fields)
            sub_search_fields['start'] = idx
            rsp = self.rest_client.get('content/search', sub_search_fields)

        return page_id, page

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
        if attachment and 'metadata' in attachment:
            metadata = attachment['metadata']
            if 'comment' in metadata:
                comment = metadata['comment']

        if not force and comment:
            parts = comment.split(HASH_KEY + ':', 1)
            if len(parts) > 1:
                tracked_hash = ''.join(parts[1].split())
                if hash_ == tracked_hash:
                    logger.verbose('attachment ({}) is already '
                        'published to document with same hash'.format(name))
                    return attachment['id']

        if self.dryrun:
            if not attachment:
                self._dryrun('adding new attachment ' + name)
                return None
            else:
                self._dryrun('updating existing attachment', attachment['id'])
                return attachment['id']
        elif self.onlynew and attachment:
            self._onlynew('skipping existing attachment', attachment['id'])
            return attachment['id']

        # publish attachment
        try:
            # split hash comment into chunks to minimize rendering issues with a
            # single one-world-long-hash value
            hash_ = '{}:{}'.format(HASH_KEY, hash_)
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
                url = 'content/{}/child/attachment'.format(page_id)
                rsp = self.rest_client.post(url, None, files=data)
                uploaded_attachment_id = rsp['results'][0]['id']
            else:
                url = 'content/{}/child/attachment/{}/data'.format(
                    page_id, attachment['id'])
                rsp = self.rest_client.post(url, None, files=data)
                uploaded_attachment_id = rsp['id']

            if not self.watch:
                self.rest_client.delete('user/watch/content',
                    uploaded_attachment_id)
        except ConfluencePermissionError:
            raise ConfluencePermissionError(
                """Publish user does not have permission to add an """
                """attachment to the configured space."""
            )

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
            else:
                misc = ''
                if parent_id and 'ancestors' in page:
                    if not any(a['id'] == parent_id for a in page['ancestors']):
                        if parent_id in self._name_cache:
                            misc += '[new parent page {} ({})]'.format(
                                self._name_cache[parent_id], parent_id)
                        else:
                            misc += '[new parent page]'

                self._dryrun('updating existing page', page['id'], misc)
                return page['id']

        expand = 'version'
        if self.append_labels:
            expand += ',metadata.labels'

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

        try:
            # new page
            if not page:
                new_page = self._build_page(page_name, data)
                self._populate_labels(new_page, data['labels'])

                if parent_id:
                    new_page['ancestors'] = [{'id': parent_id}]

                try:
                    rsp = self.rest_client.post('content', new_page)

                    if 'id' not in rsp:
                        api_err = ('Confluence reports a successful page ' +
                                  'creation; however, provided no ' +
                                  'identifier.\n\n')
                        try:
                            api_err += 'DATA: {}'.format(json.dumps(
                                rsp, indent=2))
                        except TypeError:
                            api_err += 'DATA: <not-or-invalid-json>'
                        raise ConfluenceBadApiError(-1, api_err)

                    uploaded_page_id = rsp['id']

                    # if we have labels and this is a non-cloud instance,
                    # initial labels need to be applied in their own request
                    labels = new_page['metadata']['labels']
                    if not self.cloud and labels:
                        url = 'content/{}/label'.format(uploaded_page_id)
                        self.rest_client.post(url, labels)

                except ConfluenceBadApiError as ex:
                    # Check if Confluence reports that the new page request
                    # fails, indicating it already exists. This is usually
                    # (outside of possible permission use cases) that the page
                    # name's casing does not match. In this case, attempt to
                    # re-check for the page in a case-insensitive fashion. If
                    # found, attempt to perform an update request instead.
                    if str(ex).find('title already exists') == -1:
                        raise

                    logger.verbose('title already exists warning '
                        'for page {}'.format(page_name))

                    _, page = self.get_page_case_insensitive(page_name)
                    if not page:
                        raise

                    if self.onlynew:
                        self._onlynew('skipping existing page', page['id'])
                        return page['id']

            # update existing page
            if page:
                self._update_page(page, page_name, data, parent_id=parent_id)
                uploaded_page_id = page['id']

        except ConfluencePermissionError:
            raise ConfluencePermissionError(
                """Publish user does not have permission to add page """
                """content to the configured space."""
            )

        if not self.watch:
            self.rest_client.delete('user/watch/content', uploaded_page_id)

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
            else:
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
            raise ConfluenceMissingPageIdError(self.space_key, page_id)

        try:
            self._update_page(page, page_name, data)
        except ConfluencePermissionError:
            raise ConfluencePermissionError(
                """Publish user does not have permission to add page """
                """content to the configured space."""
            )

        if not self.watch:
            self.rest_client.delete('user/watch/content', page_id)

        return page_id

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
        elif self.onlynew:
            self._onlynew('attachment removal restricted', id_)
            return

        try:
            self.rest_client.delete('content', id_)
        except ConfluencePermissionError:
            raise ConfluencePermissionError(
                """Publish user does not have permission to delete """
                """from the configured space."""
            )

    def remove_page(self, page_id):
        if self.dryrun:
            self._dryrun('removing page', page_id)
            return
        elif self.onlynew:
            self._onlynew('page removal restricted', page_id)
            return

        try:
            try:
                self.rest_client.delete('content', page_id)
            except ConfluenceBadApiError as ex:
                if str(ex).find('Transaction rolled back') == -1:
                    raise

                with skip_warningiserror():
                    logger.warn('delete failed; retrying...')
                time.sleep(3)

                self.rest_client.delete('content', page_id)

        except ConfluenceBadApiError as ex:
            # Check if Confluence reports that this content does not exist. If
            # so, we want to suppress the API error. This is most likely a
            # result of a Confluence instance reporting a page descendant
            # identifier which no longer exists (possibly a caching issue).
            if str(ex).find('No content found with id') == -1:
                raise

            logger.verbose('ignore missing delete for page '
                'identifier: {}'.format(page_id))
        except ConfluencePermissionError:
            raise ConfluencePermissionError(
                """Publish user does not have permission to delete """
                """from the configured space."""
            )

    def restrict_ancestors(self, ancestors):
        """
        restrict the provided ancestors from being changed

        Registers the provided set of ancestors from being used when page
        updates will move the location of a page. This is a pre-check update
        requests so that a page cannot be flagged as a descendant of itsel
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
        elif self.onlynew:
            self._onlynew('space home updates restricted')
            return

        page = self.rest_client.get('content/' + page_id, None)
        try:
            self.rest_client.put('space', self.space_key, {
                'key': self.space_key,
                'name': self.space_display_name,
                'homepage': page,
                'type': self.space_type,
            })
        except ConfluencePermissionError:
            raise ConfluencePermissionError(
                """Publish user does not have permission to update """
                """space's homepage."""
            )

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
                }
            },
            'metadata': {
                'properties': {},
            },
            'space': {
                'key': self.space_key,
            },
        }

        if self.editor:
            page['metadata']['properties'] = {
                'editor': {
                    'value': self.editor,
                },
            }

        if self.config.confluence_full_width is not None:
            if self.config.confluence_full_width:
                content_appearance = 'full-width'
            else:
                content_appearance = 'default'

            page['metadata']['properties'] = {
                'content-appearance-published': {
                    'value': content_appearance,
                },
            }

        return page

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
        update_page['version'] = {
            'number': last_version + 1,
            'message': self.config.confluence_version_comment,
        }

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

        page_id_explicit = page['id'] + '?status=current'
        try:
            self.rest_client.put('content', page_id_explicit, update_page)
        except ConfluenceBadApiError as ex:

            # Handle select API failures by waiting a moment and retrying the
            # content request. If it happens again, the put request will fail as
            # it normally would.
            retry_errors = [
                # Confluence Cloud may (rarely) fail to complete a content
                # request with an OptimisticLockException/
                # StaleObjectStateException exception. It is suspected that this
                # is just an instance timing/processing issue.
                'OptimisticLockException',

                # Confluence Cloud may (rarely) fail to complete a content
                # request with an UnexpectedRollbackException exception. It is
                # suspected that this is just a failed update event due to
                # processing other updates.
                'UnexpectedRollbackException',

                # Confluence may report an unreconciled error -- either from a
                # conflict with another instance updating the same page or some
                # select backend issues processing previous updates on a page.
                'unreconciled',
            ]

            if not any(x in str(ex) for x in retry_errors):
                raise

            with skip_warningiserror():
                logger.warn('remote page updated failed; retrying...')
            time.sleep(3)

            try:
                self.rest_client.put('content', page_id_explicit, update_page)
            except ConfluenceBadApiError as ex:
                if 'unreconciled' in str(ex):
                    raise ConfluenceUnreconciledPageError(
                        page_name, page['id'], self.server_url, ex)

                raise

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
            s += ' ({})'.format(id_)
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
            s += ' ({})'.format(id_)
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
