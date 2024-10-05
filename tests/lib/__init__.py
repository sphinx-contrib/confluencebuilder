# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from contextlib import contextmanager
from contextlib import suppress
from copy import deepcopy
from pathlib import Path
from sphinx.application import Sphinx
from sphinx.util.console import color_terminal
from sphinx.util.console import nocolor
from sphinx.util.docutils import docutils_namespace
from sphinxcontrib.confluencebuilder import util
from sphinxcontrib.confluencebuilder.debug import PublishDebug
from threading import Event
from threading import Lock
from threading import Thread
import builtins
import http.server as http_server
import inspect
import json
import os
import shutil
import socketserver as server_socket
import ssl
import sys
import time


# full extension name
EXT_NAME = 'sphinxcontrib.confluencebuilder'


class ConfluenceInstanceServerUnhandledRequestError(Exception):
    pass


class ConfluenceInstanceServer(server_socket.ThreadingMixIn,
        server_socket.TCPServer):

    def __init__(self):
        """
        confluence instance server

        Helps spawn an TCP server on a random local port to help emulate a
        Confluence instance.

        Attributes:
            del_req: delete requests cached by handler
            del_rsp: delete responses to use in the handler
            get_req: get requests cached by handler
            get_rsp: get responses to use in the handler
            put_req: put requests cached by handler
            put_rsp: put responses to use in the handler
        """

        LOCAL_RANDOM_PORT = ('127.0.0.1', 0)
        server_socket.TCPServer.__init__(self,
            LOCAL_RANDOM_PORT, ConfluenceInstanceRequestHandler)

        self.mtx = Lock()
        self.del_req = []
        self.del_rsp = []
        self.get_req = []
        self.get_rsp = []
        self.put_req = []
        self.put_rsp = []

    def check_unhandled_requests(self):
        """
        check if there are any unhandled requests still cached

        Provides a helper call to allow a unit test to check if there are any
        handled requests that have not been pop'ed from the instance. Provides
        an easy way to verify that no unexpected requests have been made.

        Raises:
            ``Exception`` is raised if any unhandled requests are detected
        """

        with self.mtx:
            if self.del_req or self.get_req or self.put_req:
                msg = f'''unhandled requests detected

(get requests)
{self.get_req}

(put requests)
{self.put_req}

(del requests)
{self.del_req}'''
                raise ConfluenceInstanceServerUnhandledRequestError(msg)

    def pop_delete_request(self):
        """
        pop the cached delete request made to the mocked server

        Allows a unit test to pop the next available request path/headers that
        have been pushed into the mocked Confluence server. This allows a
        unit test to verify desired (or undesired) request values.

        Returns:
            the next delete request; ``None`` if no request was made
        """

        try:
            with self.mtx:
                return self.del_req.pop(0)
        except IndexError:
            return None

    def pop_get_request(self):
        """
        pop the cached get request made to the mocked server

        Allows a unit test to pop the next available request path/headers that
        have been pushed into the mocked Confluence server. This allows a
        unit test to verify desired (or undesired) request values.

        Returns:
            the next get request; ``None`` if no request was made
        """

        try:
            with self.mtx:
                return self.get_req.pop(0)
        except IndexError:
            return None

    def pop_put_request(self):
        """
        pop the cached put request made to the mocked server

        Allows a unit test to pop the next available request path/headers that
        have been pushed into the mocked Confluence server. This allows a
        unit test to verify desired (or undesired) request values.

        Returns:
            the next put request; ``None`` if no request was made
        """

        try:
            with self.mtx:
                return self.put_req.pop(0)
        except IndexError:
            return None

    def register_delete_rsp(self, code):
        """
        register a delete response

        Registers a response the instance should return when a DELETE request
        is being served.

        Args:
            code: the response code
        """

        with self.mtx:
            self.del_rsp.append(code)

    def register_get_rsp(self, code, data):
        """
        register a get response

        Registers a response the instance should return when a GET request is
        being served.

        Args:
            code: the response code
            data: the data
        """

        if data:
            if isinstance(data, dict):
                data = json.dumps(data)

            data = data.encode('utf-8')

        with self.mtx:
            self.get_rsp.append((code, data))

    def register_put_rsp(self, code, data):
        """
        register a put response

        Registers a response the instance should return when a PUT request is
        being served.

        Args:
            code: the response code
            data: the data
        """

        if data:
            if isinstance(data, dict):
                data = json.dumps(data)

            data = data.encode('utf-8')

        with self.mtx:
            self.put_rsp.append((code, data))

    def reset(self):
        """
        reset any pending requests/responses expected

        Provides a call for a tester to reset expected requests or responses
        for a given instance.
        """

        with self.mtx:
            self.del_req = []
            self.del_rsp = []
            self.get_req = []
            self.get_rsp = []
            self.put_req = []
            self.put_rsp = []


class ConfluenceInstanceRequestHandler(http_server.SimpleHTTPRequestHandler):
    """
    confluence instance request handler

    Provides the handler implementation when a z instance
    wishes to serve an HTTP request. This handler will pull responses (if any)
    populated into the server instance. If no responses are provided, the
    default response will be a 500 error with no data.
    """

    def do_DELETE(self):
        """
        serve a delete request

        This method is called when a DELETE request is being processed by this
        handler.
        """

        with self.server.mtx:
            self.server.del_req.append((self.path, dict(self.headers)))

            try:
                code = self.server.del_rsp.pop(0)
            except IndexError:
                code = 500

        self.send_response(code)
        self.end_headers()

    def do_GET(self):
        """
        serve a get request

        This method is called when a GET request is being processed by this
        handler.
        """

        with self.server.mtx:
            self.server.get_req.append((self.path, dict(self.headers)))

            try:
                code, data = self.server.get_rsp.pop(0)
            except IndexError:
                code = 500
                data = None

        self.send_response(code)
        self.end_headers()
        if data:
            self.wfile.write(data)

    def do_PUT(self):
        """
        serve a put request

        This method is called when a PUT request is being processed by this
        handler.
        """

        with self.server.mtx:
            self.server.put_req.append((self.path, dict(self.headers)))

            try:
                code, data = self.server.put_rsp.pop(0)
            except IndexError:
                code = 500
                data = None

        length = int(self.headers.get('content-length'))
        self.rfile.read(length)

        self.send_response(code)
        self.end_headers()
        if data:
            self.wfile.write(data)


class MockedConfig(dict):
    """
    mocked sphinx configuration

    Provides a class to mock a Sphinx configuration for testing, to support both
    dictionary key and attribute calls.
    """

    def __getattr__(self, name):
        if name in self:
            return self[name]

        return None

    def __setattr__(self, name, value):
        self[name] = value

    def clone(self):
        cloned = MockedConfig()

        for key, value in self.items():
            if value is None or callable(value):
                cloned[key] = value
            else:
                cloned[key] = deepcopy(value)

        return cloned


@contextmanager
def autocleanup_publisher(ptype):
    """
    creates a confluence publisher that cleanups after a context

    The following create a provided publisher instance and yeild it to the
    running context. The publisher can be used to connect to an instance
    and perform other capabilities provided by the class. When the context
    is left, the publisher will be cleaned up to ensure any pending
    session state can been disconnected.

    Yields:
        the publisher
    """

    try:
        publisher = ptype()
        yield publisher

    finally:
        publisher.disconnect()


def enable_sphinx_info(verbosity=None):
    """
    enable verbosity for features handled by this utility class

    When invoked, this utility class will attempt to prepare or invoke
    requests in a verbose manner.

    Args:
        verbosity (optional): configure verbosity on the sphinx application
    """
    os.environ['SPHINX_STATUS'] = '1'
    if verbosity:
        os.environ['SPHINX_VERBOSITY'] = str(verbosity)


def fetch_cert_files():
    """
    find certificate files for unit testing

    Returns a tuple of a key file and certificate file used to create a
    unit testing "secure" HTTP server. Dummy pem files are included in the
    testing asserts folder, which this call can return the paths to these
    files.

    Returns:
        2-tuple of a key file and certificate file
    """

    lib_dir = Path(__file__).parent.resolve()
    test_dir = lib_dir.parent
    httpd_dir = test_dir / 'unit-tests' / 'assets' / 'httpd'
    keyfile = httpd_dir / 'test-notprivate-key-pem'
    certfile = httpd_dir / 'test-cert-pem'
    return keyfile, certfile


@contextmanager
def mock_confluence_instance(config=None, ignore_requests=False, secure=None):
    """
    spawns a mocked confluence instance which publishing attempts to be checked

    The following spawns a mocked Confluence instance, which will create an
    local HTTP server to serve API requests from a publisher instance.

    Args:
        config (optional): the configuration to populate a publisher url on
        ignore_requests (optional): whether or not requests made to the server
                                     should be ignored (default: ``False``)
        secure (optional): start a "secure" instance

    Yields:
        the http(s) daemon
    """

    serve_thread = None

    try:
        # spawn a mocked server instance
        daemon = ConfluenceInstanceServer()

        if secure:
            keyfile, certfile = fetch_cert_files()

            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.load_cert_chain(certfile, keyfile=keyfile)

            daemon.socket = context.wrap_socket(daemon.socket, server_side=True)

        host, port = daemon.server_address
        if config:
            scheme = 'https://' if secure else 'http://'
            config.confluence_server_url = f'{scheme}{host}:{port}/'

        # start accepting requests
        if not ignore_requests:
            sync = Event()

            def serve_forever(daemon, sync):
                sync.set()
                daemon.serve_forever()

            serve_thread = Thread(target=serve_forever, args=(daemon, sync))
            serve_thread.start()

            # wait for the serving thread to be running
            sync.wait()

            # yeild context for a moment to help ensure the daemon is serving
            time.sleep(0.1)

        yield daemon

    finally:
        if serve_thread:
            daemon.shutdown()
            serve_thread.join()

        daemon.server_close()


@contextmanager
def mock_getpass(mock):
    def _(prompt='Password: ', stream=sys.stdout):
        stream.write(prompt)
        stream.write('(mocked input> ')
        stream.write(mock)
        stream.write('\n')
        return mock

    try:
        original = util.getpass2
        try:
            util.getpass2 = _
            yield
        finally:
            util.getpass2 = original
    finally:
        pass


@contextmanager
def mock_input(mock):
    def _(prompt=''):
        print(prompt + '(mocked input> ' + mock)
        return mock

    try:
        original = builtins.input
        try:
            builtins.input = _
            yield
        finally:
            builtins.input = original
    finally:
        pass


def prepare_conf():
    """
    prepare minimal sphinx configuration for sphinx application

    Prepares a minimum number of required configuration values into a
    dictionary for unit tests to extend. This dictionary can be passed into
    a Sphinx application instance.
    """

    config = MockedConfig()
    config['extensions'] = [
        EXT_NAME,
        # include any forced-injected extensions (config support)
        'sphinx.ext.imgmath',
    ]
    config['confluence_publish'] = False

    return config


def prepare_conf_publisher():
    """
    prepare minimal sphinx configuration for sphinx application (publisher)

    Prepares a minimum number of required configuration values into a
    dictionary for unit tests to extend. This dictionary can be passed into
    a Sphinx application instance. This call focuses on configuration options
    for publisher-specific tests.

    Returns:
        the configuration
    """

    config = prepare_conf()

    # always enable debug prints from urllib3
    config.confluence_publish_debug = PublishDebug.urllib3

    # define a timeout to ensure publishing tests do not block
    config.confluence_timeout = 5

    return config


def prepare_dirs(container=None, postfix=None):
    """
    return the output directory base for all unit tests

    This utility method is used to provide other tests the location to store
    output files. This method will ensure the output directory is removed
    before returning.

    Args:
        container (optional): the output container name to use
        postfix (optional): postfix to add to the container directory

    Returns:
        the output directory
    """
    if not container:
        frame = inspect.currentframe()
        while frame and not frame.f_code.co_name.startswith('test_'):
            frame = frame.f_back
        container = frame.f_code.co_name if frame else 'unknown'

    lib_dir = Path(__file__).parent.resolve()
    test_dir = lib_dir.parent
    base_dir = test_dir.parent
    output_dir = base_dir / 'output'

    # attempt to nest under a tox environment folder, to help prevent
    # issues running in parallel mode
    suboutput_dir = os.getenv('TOX_ENV_NAME')
    if suboutput_dir:
        output_dir = output_dir / suboutput_dir

    container_dir = output_dir / container
    if postfix:
        container_dir = container_dir.parent / (container_dir.name + postfix)

    shutil.rmtree(container_dir, ignore_errors=True)

    return container_dir


@contextmanager
def prepare_sphinx(src_dir, config=None, out_dir=None, extra_config=None,
        builder=None, relax=False):
    """
    prepare a sphinx application instance

    Return a prepared Sphinx application instance [1] ready for execution.

    [1]: https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py

    Args:
        src_dir: document sources
        config (optional): configuration to use
        out_dir (optional): output for generated documents
        extra_config (optional): additional configuration data to apply
        builder (optional): the builder to use
        relax (optional): do not generate warnings as errors
    """

    # Enable coloring of warning and other messages. Note that this can
    # cause sys.stderr to be mocked which is why we pass the new value
    # explicitly on the call to Sphinx() below.
    if 'MSYSTEM' not in os.environ and not color_terminal():
        nocolor()

    conf = dict(config) if config else {}
    if extra_config:
        conf.update(extra_config)
    conf_dir = str(src_dir) if config is None else None
    warnerr = not relax

    sts = None
    if 'SPHINX_STATUS' in os.environ:
        sts = sys.stdout

    verbosity = 0
    if 'SPHINX_VERBOSITY' in os.environ:
        with suppress(ValueError):
            verbosity = int(os.environ['SPHINX_VERBOSITY'])

    # default to using this extension's builder
    if not builder:
        builder = 'confluence'

    if not out_dir:
        out_dir = prepare_dirs()

    doctrees_dir = out_dir / '.doctrees'

    sphinx_args = {
        'confoverrides': conf,     # load provided configuration (volatile)
        'status': sts,             # status output
        'warning': sys.stderr,     # warnings output
        'warningiserror': warnerr, # treat warnings as errors
        'verbosity': verbosity,    # verbosity
    }

    with docutils_namespace():
        app = Sphinx(
            str(src_dir),      # output for document sources
            conf_dir,          # configuration directory
            str(out_dir),      # output for generated documents
            str(doctrees_dir), # output for doctree files
            builder,           # builder to execute
            **sphinx_args)     # verbosity

        yield app


def prepare_sphinx_filenames(src_dir, filenames, configs=None):
    """
    prepare explicit filenames for a sphinx application instance

    A Sphinx engine allows accepting a list of filenames it will process;
    however, these filenames need to be set to full paths. This is not always
    convenient for testing, so this utility allows generating a filename list
    with the source directory prefixed for each entry.

    In addition, when passing a documentation set to process, Sphinx requires
    that the documentation set has an existing root document. In some testing
    datasets, they may not have one that exists. If this is detected, this
    helper will adjust the configuration to adjust the root document to a
    provided filename, which should prevent issues when the Sphinx application
    prepares an environment. This is only performed when configurations are
    provided in to this call. Multiple configuration entries can be provided,
    and only the last configuration entry (must exist and) will be updated in
    the event when a change is needed.

    Args:
        src_dir: document sources
        filenames: the documents to process relative to src_dir (no extensions)
        configs (optional): list of configurations to check for root doc issue

    Returns:
        the updated file name list
    """
    files = [str(src_dir / (fname + '.rst')) for fname in filenames]

    if configs:
        root_doc = 'index'
        for config in configs:
            if config and 'root_doc' in config:
                root_doc = config['root_doc']
                break

        if root_doc not in filenames:
            configs[-1]['root_doc'] = filenames[0]  # update last config

    return files


def build_sphinx(src_dir, config=None, out_dir=None, extra_config=None,
        builder=None, relax=False, filenames=None, force=True):
    """
    prepare a sphinx application instance

    Creates, invokes and cleans up a Sphinx application instance [1].

    [1]: https://github.com/sphinx-doc/sphinx/blob/master/sphinx/application.py

    Args:
        src_dir: document sources
        config (optional): configuration to use
        out_dir (optional): output for generated documents
        extra_config (optional): additional configuration data to apply
        builder (optional): the builder to use
        relax (optional): do not generate warnings as errors
        filenames (optional): specific documents to process
        force (optional): whether to force process each document

    Returns:
        the output directory
    """

    if not out_dir:
        out_dir = prepare_dirs()

    files = []
    force_all = force

    if filenames:
        # force-all not supported when using explicit filenames
        force_all = False

        # sphinx application requires full paths for explicit filenames
        extra_config = dict(extra_config) if extra_config else {}
        files = prepare_sphinx_filenames(src_dir, filenames,
            configs=(config, extra_config))

    with prepare_sphinx(
            src_dir, config=config, out_dir=out_dir, extra_config=extra_config,
            builder=builder, relax=relax) as app:
        app.build(force_all=force_all, filenames=files)

    return out_dir
