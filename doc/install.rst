Installing
==========

.. only:: html

    Atlassian Confluence Builder for Sphinx |version| depends on:

    * Python_ |supported_python_ver|
    * Requests_ |supported_requests_ver|
    * Sphinx_ |supported_sphinx_ver|
    * Confluence_ Cloud / Data Center |supported_confluence_ver|

The recommended method of installing or upgrading is using pip_:

.. code-block:: shell

    pip install -U sphinxcontrib-confluencebuilder
     (or)
    python -m pip install -U sphinxcontrib-confluencebuilder

To verify the package has been installed, the following command can be used:

.. code-block:: shell

    python -m sphinxcontrib.confluencebuilder --version

.. raw:: html

    <hr />

For new users, the following provides a series of steps to assist in preparing
a new environment to use this package. For users wishing to use virtualenv,
please see the instructions in :doc:`install-virtualenv`.

Linux
-----

While the use of Python_/pip_ is almost consistent between Linux distributions,
the following are a series of helpful steps to install this package under
specific distributions of Linux. From a terminal, invoke the following commands:

Arch
~~~~

.. code-block:: shell-session

    $ sudo pacman -Sy
    $ sudo pacman -S python-pip
    $ pip install sphinxcontrib-confluencebuilder
    $ python -m sphinxcontrib.confluencebuilder --version
    sphinxcontrib.confluencebuilder <version>

CentOS
~~~~~~

.. code-block:: shell-session

    $ sudo yum install epel-release
    $ sudo yum install python-pip
    $ pip install sphinxcontrib-confluencebuilder
    $ python -m sphinxcontrib.confluencebuilder --version
    sphinxcontrib.confluencebuilder <version>

Fedora
~~~~~~

.. code-block:: shell-session

    $ sudo dnf install python-pip
    $ pip install sphinxcontrib-confluencebuilder
    $ python -m sphinxcontrib.confluencebuilder --version
    sphinxcontrib.confluencebuilder <version>

Ubuntu
~~~~~~

.. code-block:: shell-session

    $ sudo apt-get update
    $ sudo apt-get install python-pip
    $ pip install sphinxcontrib-confluencebuilder
    $ python -m sphinxcontrib.confluencebuilder --version
    sphinxcontrib.confluencebuilder <version>

OS X
----

From a terminal, invoke the following commands:

.. code-block:: shell-session

    $ sudo easy_install pip
    $ pip install sphinxcontrib-confluencebuilder
    $ python -m sphinxcontrib.confluencebuilder --version
    sphinxcontrib.confluencebuilder <version>

Windows
-------

If not already installed, download the most recent version of Python_:

    | Python - Downloads
    | https://www.python.org/downloads/

When invoking the installer, it is recommended to select the option to "Add
Python to PATH"; however, users can explicitly invoked Python from an absolute
path. The remainder of these steps will assume Python is available in the path.

Open a Windows command prompt. Invoke the following:

.. code-block:: doscon

    > python -m pip install sphinxcontrib-confluencebuilder
    > python -m sphinxcontrib.confluencebuilder --version
    sphinxcontrib.confluencebuilder <version>

Development installation
------------------------

To install the bleeding edge sources, the following pip_ command can be used:

.. code-block:: shell

    pip install git+https://github.com/sphinx-contrib/confluencebuilder.git

.. pdf inclusion hack
.. only:: latex

    .. include:: install-virtualenv.rst
        :start-after: :orphan:

.. _Confluence: https://www.atlassian.com/software/confluence
.. _Python: https://www.python.org/
.. _Requests: https://pypi.python.org/pypi/requests
.. _Sphinx: https://www.sphinx-doc.org/
.. _pip: https://pip.pypa.io/
