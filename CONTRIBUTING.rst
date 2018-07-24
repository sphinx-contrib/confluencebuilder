contributing
============

Contributions to this extension are welcome and much appreciated.

.. contents::
   :depth: 2

.. sectnum::

reporting issues
----------------

Bugs, enhancements and more can be reported to this extension's GitHub
`issue tracker`_. It is recommended to search for a related issue before
attempting to submit a new issue.

When reporting a bug, it is recommended to include at least the following:

- sphinxcontrib-confluencebuilder's extension version
- Python version
- Sphinx verison

Additional logs from a ``sphinx-build`` attempt can be helpful as well (if
applicable).

submitting changes
------------------

Contributions can be provided as `pull requests`_ to this extension's GitHub
project.

Do:

- (required) sign your work (`Developer’s Certificate of Origin`_). This is
  confirmed with the inclusion of ``Signed-off-by`` in submitted commit
  messages.
- ensure builds pass. When a pull request is submitted, a continues integration
  test will be invoked. A developer can invoke ``tox`` at the root of the
  checked out repository to validate changes before submitting a pull request.
- keep a narrow scope for proposed changes. Submitting multiple feature changes
  in a single pull request is not always helpful. Use multiple commits to
  separate changes over stacking all changes in a single commit (for example,
  related implementation and documentation changes can be submitted in a single
  pull request, but are best presented in their own individual commits).
- (optional) add unit tests (if applicable). Adding unit tests to validate new
  changes helps build confidence for the new modifications and helps prevent
  future changes from breaking the new feature/fix.
- (optional) ensure ``AUTHORS`` is updated. Contributors of this extension are
  populated in the ``AUTHORS`` document. A pull request does not require to
  include new authors to be added, authors will be added by a maintainer in a
  future commit. If a contributor does not wish to add themselves to the
  ``AUTHORS`` document, they may opt-out be explicitly indicating in a pull
  request or issue.

Do not:

- ignore documentation. If a new change introduces, for example, a new
  configuration entry or markup support has changed with a request, do not
  forget to update respective documentation as well.
- update ``CHANGES.rst``. Change log information is managed by this extension's
  maintainers.

While maintainers will help strive to review, merge changes and provide support
(when possible), the process may take some time. Please be patient and happy
coding.

.. _Developer’s Certificate of Origin: https://developercertificate.org/
.. _issue tracker: https://github.com/tonybaloney/sphinxcontrib-confluencebuilder/issues
.. _pull requests: https://github.com/tonybaloney/sphinxcontrib-confluencebuilder/pulls
