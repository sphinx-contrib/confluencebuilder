# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)

from enum import Flag
from enum import auto


class PublishDebug(Flag):
    """
    publishing debugging enumeration

    Defines a series of flags to track support debugging modes when enabling
    publishing-specific debugging in this extension. Provides an explicit
    list of supported options (that can be configuration checked), as well
    as provides an "all" state, allowing easy implementation handling of
    enabling specific debugging scenarios when all options are enabled.
    """

    # do not perform any logging
    none = auto()
    # logs warnings when confluence reports a deprecated api call
    deprecated = auto()
    # log raw requests/responses in stdout with header data
    headers = auto()
    # log urllib3-supported debug messages
    urllib3 = auto()
    # enable all logging
    all = headers | urllib3
    # enable all developer logging
    developer = deprecated | all
