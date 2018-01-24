installing
==========

Atlassian Confluence Builder for Sphinx |version| depends on:

* Python_ 2.7 or 3.3+
* Requests_
* Sphinx_ 1.0 or later
* Confluence_ 4.0 or later

The recommended method of installation is using pip_.

.. code-block:: shell

    pip install --user sphinxcontrib-confluencebuilder

To verify the package has been installed, if desired, the following command can
be used:

.. code-block:: shell

    python -m sphinxcontrib.confluencebuilder --version

fresh quick-start
-----------------

The following provides a series of steps to assist in preparing a new
environment to use this package. This quick-start will aim to use the most
recent version of Python.

.. note::

   If the installation process fails with the following error "AttributeError:
   '_NamespacePath' object has no attribute 'sort'", try upgrading your
   setuptools module:

    .. code-block:: shell

        python -m pip install --upgrade setuptools

linux
~~~~~

While the use of Python_/pip_ is almost consistent between Linux distributions,
the following are a series of helpful steps to install this package under
specific distributions of Linux. From a terminal, invoke the following commands:

arch
++++

.. code-block:: shell

    $ sudo pacman -S python-pip
    $ pip install --user sphinxcontrib-confluencebuilder
    $ python -m sphinxcontrib.confluencebuilder --version
    sphinxcontrib.confluencebuilder <version>

centos
++++++

.. code-block:: shell

    $ sudo yum install epel-release
    $ sudo yum install python-pip
    $ pip install --user sphinxcontrib-confluencebuilder
    $ python -m sphinxcontrib.confluencebuilder --version
    sphinxcontrib.confluencebuilder <version>

fedora
++++++

.. code-block:: shell

    $ sudo dnf install python-pip
    $ pip install --user sphinxcontrib-confluencebuilder
    $ python -m sphinxcontrib.confluencebuilder --version
    sphinxcontrib.confluencebuilder <version>

ubuntu
++++++

.. code-block:: shell

    $ sudo apt-get install python-pip
    $ pip install --user sphinxcontrib-confluencebuilder
    $ python -m sphinxcontrib.confluencebuilder --version
    sphinxcontrib.confluencebuilder <version>

os x
~~~~

From a terminal, invoke the following commands:

.. code-block:: shell

    $ sudo easy_install pip
    $ pip install --user sphinxcontrib-confluencebuilder
    $ python -m sphinxcontrib.confluencebuilder --version
    sphinxcontrib.confluencebuilder <version>

windows
~~~~~~~

If not already installed, download the most recent version of Python_:

 | Python - Downloads
 | https://www.python.org/downloads/

When invoking the installer, it is recommended to select the option to "Add
Python to PATH"; however, users can explicitly invoked Python from an absolute
path. Open a Python command environment from the start-menu or, if Python was
added to the system path, open a Windows command prompt. Invoke the following:

.. code-block:: shell

    python -m pip install sphinxcontrib-confluencebuilder
    python -m sphinxcontrib.confluencebuilder --version

master
------

To install the bleeding edge sources, the following pip_ command can be used:

.. code-block:: shell

    pip install \
        git+https://github.com/tonybaloney/sphinxcontrib-confluencebuilder

.. _Confluence: https://www.atlassian.com/software/confluence
.. _Python: https://www.python.org/
.. _Requests: https://pypi.python.org/pypi/requests
.. _Sphinx: http://sphinx-doc.org/
.. _pip: https://pip.pypa.io/
