# -*- coding: utf-8 -*-
"""
    :copyright: Copyright 2017-2020 by the contributors (see AUTHORS file).
    :license: BSD-2-Clause, see LICENSE for details.

    See also:
     Confluence Cloud REST API Reference
     https://docs.atlassian.com/confluence/REST/latest/
"""

from .exceptions import ConfluenceBadApiError
from .exceptions import ConfluenceBadSpaceError
from .exceptions import ConfluenceConfigurationError
from .exceptions import ConfluencePermissionError
from .logger import ConfluenceLogger
from .rest import Rest
import json
import sys
import time

class ConfluencePublisher():
    def __init__(self):
        self.space_display_name = None

    def init(self, config):
        self.config = config
        self.notify = not config.confluence_disable_notifications
        self.parent_id = config.confluence_parent_page_id_check
        self.parent_name = config.confluence_parent_page
        self.server_url = config.confluence_server_url
        self.server_user = config.confluence_server_user
        self.server_pass = config.confluence_server_pass
        self.space_name = config.confluence_space_name
        self.timeout = config.confluence_timeout
        self.ca_cert = config.confluence_ca_cert
        self.client_cert = config.confluence_client_cert
        self.client_cert_pass = config.confluence_client_cert_pass

    def connect(self):
        self.rest_client = Rest(self.config);
        
        rsp = self.rest_client.get('space', {
            'spaceKey': self.space_name,
            'limit': 1
            })
        if rsp['size'] == 0:
            raise ConfluenceBadSpaceError(self.space_name)
        self.space_display_name = rsp['results'][0]['name']

    def disconnect(self):
        self.rest_client.close()

    def getBasePageId(self):
        base_page_id = None

        if not self.parent_name:
            return base_page_id

        rsp = self.rest_client.get('content', {
            'type': 'page',
            'spaceKey': self.space_name,
            'title': self.parent_name,
            'status': 'current'
            })
        if rsp['size'] == 0:
            raise ConfluenceConfigurationError("""Configured parent """
                """page name do not exist.""")
        page = rsp['results'][0]
        if self.parent_id and page['id'] != str(self.parent_id):
            raise ConfluenceConfigurationError("""Configured parent """
                """page ID and name do not match.""")
        base_page_id = page['id']

        if not base_page_id and self.parent_id:
            raise ConfluenceConfigurationError("""Unable to find the """
                """parent page matching the ID or name provided.""")

        return base_page_id

    def getDescendants(self, page_id):
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
            search_fields = {'cql': 'space="' + self.space_name +
                '" and type=page'}

        # Configure a larger limit value than the default (no provided
        # limit defaults to 25). This should reduce the number of queries
        # needed to fetch a complete descendants set (for larger sets).
        search_fields['limit'] = 1000;

        rsp = self.rest_client.get('content/search', search_fields)
        idx = 0
        while rsp['size'] > 0:
            for result in rsp['results']:
                descendants.add(result['id'])

            if rsp['size'] != rsp['limit']:
                break

            idx += int(rsp['limit'])
            sub_search_fields = dict(search_fields)
            sub_search_fields['start'] = idx;
            rsp = self.rest_client.get('content/search', sub_search_fields)

        return descendants

    def getDescendantsCompat(self, page_id):
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
            descendants = self.getDescendants(page_id)
            for descendant in descendants:
                if descendant not in pages:
                    pages.add(descendant)
                    find_legacy_pages(descendant, pages)

        find_legacy_pages(page_id, visited_pages)
        return visited_pages

    def getAttachment(self, page_id, name):
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
            #'type': 'attachment',
            'filename': name,
            })

        if rsp['size'] != 0:
            attachment = rsp['results'][0]
            attachment_id = attachment['id']

        return attachment_id, attachment

    def getAttachments(self, page_id):
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
        search_fields['limit'] = 1000;

        rsp = self.rest_client.get(url, search_fields)
        idx = 0
        while rsp['size'] > 0:
            for result in rsp['results']:
                attachment_info[result['id']] = result['title']

            if rsp['size'] != rsp['limit']:
                break

            idx += int(rsp['limit'])
            sub_search_fields = dict(search_fields)
            sub_search_fields['start'] = idx;
            rsp = self.rest_client.get(url, sub_search_fields)

        return attachment_info

    def getPage(self, page_name):
        """
        get page information with the provided page name

        Performs an API call to acquire known information about a specific page.
        This call can returns both the page identifier (for convenience) and the
        page object. If the page cannot be found, the returned tuple will
        return ``None`` entries.

        Args:
            page_name: the page name

        Returns:
            the page id and page object
        """
        page = None
        page_id = None

        rsp = self.rest_client.get('content', {
            'type': 'page',
            'spaceKey': self.space_name,
            'title': page_name,
            'status': 'current',
            'expand': 'version'
            })

        if rsp['size'] != 0:
            page = rsp['results'][0]
            page_id = page['id']

        return page_id, page

    def storeAttachment(self, page_id, name, data, mimetype, hash, force=False):
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
            hash: the hash of the attachment
            force (optional): force publishing if exists (defaults to False)

        Returns:
            the attachment identifier
        """
        HASH_KEY = 'SCB_KEY'
        uploaded_attachment_id = None

        _, attachment = self.getAttachment(page_id, name)

        # check if attachment (of same hash) is already published to this page
        comment = None
        if attachment and 'metadata' in attachment:
            metadata = attachment['metadata']
            if 'comment' in metadata:
                comment = metadata['comment']

        if not force and comment:
            parts = comment.split(HASH_KEY + ':')
            if len(parts) > 1:
                tracked_hash = parts[1]
                if hash == tracked_hash:
                    ConfluenceLogger.verbose('attachment ({}) is already '
                        'published to document with same hash'.format(name))
                    return attachment['id']

        # publish attachment
        try:
            data = {
                'comment': '{}:{}'.format(HASH_KEY, hash),
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
        except ConfluencePermissionError:
            raise ConfluencePermissionError(
                """Publish user does not have permission to add an """
                """attachment to the configured space."""
            )

        return uploaded_attachment_id

    def storePage(self, page_name, data, parent_id=None):
        uploaded_page_id = None

        if self.config.confluence_adv_trace_data:
            ConfluenceLogger.trace('data', data)

        _, page = self.getPage(page_name)

        try:
            if not page:
                newPage = {
                    'type': 'page',
                    'title': page_name,
                    'body': {
                        'storage': {
                            'representation': 'storage',
                            'value': data
                        }
                    },
                    'space': {
                        'key': self.space_name
                    }
                }

                if parent_id:
                    newPage['ancestors'] = [{'id': parent_id}]

                rsp = self.rest_client.post('content', newPage)

                if 'id' not in rsp:
                    api_err = ('Confluence reports a successful page ' +
                              'creation; however, provided no ' +
                              'identifier.\n\n')
                    try:
                        api_err += 'DATA: {}'.format(json.dumps(
                            rsp, indent=2))
                    except TypeError:
                        api_err += 'DATA: <not-or-invalid-json>'
                    raise ConfluenceBadApiError(api_err)

                uploaded_page_id = rsp['id']
            else:
                last_version = int(page['version']['number'])
                updatePage = {
                    'id': page['id'],
                    'type': 'page',
                    'title': page_name,
                    'body': {
                        'storage': {
                            'representation': 'storage',
                            'value': data
                        }
                    },
                    'space': {
                        'key': self.space_name
                    },
                    'version': {
                        'number': last_version + 1
                    }
                }

                if not self.notify:
                    updatePage['version']['minorEdit'] = True

                if parent_id:
                    updatePage['ancestors'] = [{'id': parent_id}]

                try:
                    self.rest_client.put('content', page['id'], updatePage)
                except ConfluenceBadApiError as ex:
                    # Confluence Cloud may (rarely) fail to complete a
                    # content request with an OptimisticLockException/
                    # StaleObjectStateException exception. It is suspected
                    # that this is just an instance timing/processing issue.
                    # If this is observed, wait a moment and retry the
                    # content request. If it happens again, the put request
                    # will fail as it normally would.
                    if str(ex).find('OptimisticLockException') == -1:
                        raise
                    ConfluenceLogger.warn(
                        'remote page updated failed; retrying...')
                    time.sleep(1)
                    self.rest_client.put('content', page['id'], updatePage)

                uploaded_page_id = page['id']
        except ConfluencePermissionError:
            raise ConfluencePermissionError(
                """Publish user does not have permission to add page """
                """content to the configured space."""
            )

        return uploaded_page_id

    def removeAttachment(self, id):
        """
        request to remove an attachment

        Makes a request to a Confluence instance to remove an existing
        attachment.

        Args:
            id: the attachment
        """
        try:
            self.rest_client.delete('content', id)
        except ConfluencePermissionError:
            raise ConfluencePermissionError(
                """Publish user does not have permission to delete """
                """from the configured space."""
            )

    def removePage(self, page_id):
        try:
            self.rest_client.delete('content', page_id)
        except ConfluencePermissionError:
            raise ConfluencePermissionError(
                """Publish user does not have permission to delete """
                """from the configured space."""
            )

    def updateSpaceHome(self, page_id):
        if not page_id:
            return

        page = self.rest_client.get('content/' + page_id, None)
        try:
            self.rest_client.put('space', self.space_name, {
                'key': self.space_name,
                'name': self.space_display_name,
                'homepage': page
            })
        except ConfluencePermissionError:
            raise ConfluencePermissionError(
                """Publish user does not have permission to update """
                """space's homepage."""
            )
