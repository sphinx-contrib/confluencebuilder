# SPDX-License-Identifier: BSD-2-Clause
# Copyright Sphinx Confluence Builder Contributors (AUTHORS)
#
# This file provides a series of string hints reported by Confluence
# which may or may not permit the automatic retry of an API request to
# Confluence. For example, detecting if Confluence reports an interim
# transaction failure, the extension may retry the request again a few
# seconds later. This is to avoid having a user to retry publishing more
# than once to publish an entire documentation set.

# List of reported errors that this extension may retry a request.
#
# Note: some of these error scenarios may already be captured by the 5xx
# error check in this extension. Although, it was never tracked if the
# observed cases where Confluence reported the following errors if Confluence
# also reported an expected 5xx error code. On the safe side, will continue
# to check for these cases.
API_RETRY_ERRORS = [
    # Confluence Cloud may (rarely) fail to complete a content
    # request with an OptimisticLockException/
    # StaleObjectStateException exception. It is suspected that this
    # is just an instance timing/processing issue.
    'OptimisticLockException',

    # It has been observed that Confluence may report a rolled back
    # transaction after an attempt to delete one or more pages/attachments.
    'Transaction rolled back',

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

# List of reported errors that this extension will not retry a request.
API_NORETRY_ERRORS = [
    # CADA publish error; handled by `publisher.py`
    'CDATA block has embedded',

    # file type restricted; handled by `publisher.py`
    'file type is not allowed',
]
