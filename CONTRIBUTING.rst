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

Code of Conduct
===============

Our Pledge
----------

In the interest of fostering an open and welcoming environment, we as
contributors and maintainers pledge to making participation in our project and
our community a harassment-free experience for everyone, regardless of age, body
size, disability, ethnicity, gender identity and expression, level of experience,
nationality, personal appearance, race, religion, or sexual identity and
orientation.

Our Standards
-------------

Examples of behavior that contributes to creating a positive environment
include:

* Using welcoming and inclusive language
* Being respectful of differing viewpoints and experiences
* Gracefully accepting constructive criticism
* Focusing on what is best for the community
* Showing empathy towards other community members

Examples of unacceptable behavior by participants include:

* The use of sexualized language or imagery and unwelcome sexual attention or advances
* Trolling, insulting/derogatory comments, and personal or political attacks
* Public or private harassment
* Publishing others' private information, such as a physical or electronic address, without explicit permission
* Other conduct which could reasonably be considered inappropriate in a professional setting

Our Responsibilities
--------------------

Project maintainers are responsible for clarifying the standards of acceptable
behavior and are expected to take appropriate and fair corrective action in
response to any instances of unacceptable behavior.

Project maintainers have the right and responsibility to remove, edit, or
reject comments, commits, code, wiki edits, issues, and other contributions
that are not aligned to this Code of Conduct, or to ban temporarily or
permanently any contributor for other behaviors that they deem inappropriate,
threatening, offensive, or harmful.

Scope
-----

This Code of Conduct applies both within project spaces and in public spaces
when an individual is representing the project or its community. Examples of
representing a project or community include using an official project e-mail
address, posting via an official social media account, or acting as an appointed
representative at an online or offline event. Representation of a project may be
further defined and clarified by project maintainers.

Enforcement
-----------

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported by contacting the project team at @tonybaloney. All
complaints will be reviewed and investigated and will result in a response that
is deemed necessary and appropriate to the circumstances. The project team is
obligated to maintain confidentiality with regard to the reporter of an incident.
Further details of specific enforcement policies may be posted separately.

Project maintainers who do not follow or enforce the Code of Conduct in good
faith may face temporary or permanent repercussions as determined by other
members of the project's leadership.

Attribution
-----------

This Code of Conduct is adapted from the `Contributor Covenant`_, version 1.4.

.. _Contributor Covenant: http://contributor-covenant.org/version/1/4/
.. _Developer’s Certificate of Origin: https://developercertificate.org/
.. _issue tracker: https://github.com/tonybaloney/sphinxcontrib-confluencebuilder/issues
.. _pull requests: https://github.com/tonybaloney/sphinxcontrib-confluencebuilder/pulls
