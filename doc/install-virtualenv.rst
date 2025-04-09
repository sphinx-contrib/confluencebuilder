:orphan:

Installing (virtualenv)
=======================

For users wishing to use virtualenv_ for their environments, the following
outlines the recommended commands to invoke for various environments. For users
who do not desire to use virtualenv, please see :doc:`install` instead.

Linux (virtualenv)
------------------

While the use of Python_/pip_ is almost consistent between Linux distributions,
the following are a series of helpful steps to install this package under
specific distributions of Linux. From a terminal, invoke the following commands:

Arch (virtualenv)
~~~~~~~~~~~~~~~~~

.. code-block:: shell-session

    $ sudo pacman -Sy
    $ sudo pacman -S python-pip
    $ sudo pacman -S python-virtualenv
    $ virtualenv sphinx-venv
    $ source sphinx-venv/bin/activate
    $ pip install sphinxcontrib-confluencebuilder
    $ python -m sphinxcontrib.confluencebuilder --version
    sphinxcontrib.confluencebuilder <version>

Fedora (virtualenv)
~~~~~~~~~~~~~~~~~~~

.. code-block:: shell-session

    $ sudo dnf install python-pip
    $ sudo dnf install python-virtualenv
    $ virtualenv sphinx-venv
    $ source sphinx-venv/bin/activate
    $ pip install sphinxcontrib-confluencebuilder
    $ python -m sphinxcontrib.confluencebuilder --version
    sphinxcontrib.confluencebuilder <version>

Ubuntu (virtualenv)
~~~~~~~~~~~~~~~~~~~

.. code-block:: shell-session

    $ sudo apt-get update
    $ sudo apt-get install python-pip
    $ sudo dnf install python-virtualenv
    $ virtualenv sphinx-venv
    $ source sphinx-venv/bin/activate
    $ pip install sphinxcontrib-confluencebuilder
    $ python -m sphinxcontrib.confluencebuilder --version
    sphinxcontrib.confluencebuilder <version>

.. raw:: latex

    \newpage

OS X (virtualenv)
-----------------

From a terminal, invoke the following commands:

.. code-block:: shell-session

    $ sudo easy_install pip
    $ pip install virtualenv
    $ virtualenv sphinx-venv
    $ source sphinx-venv/bin/activate
    $ pip install sphinxcontrib-confluencebuilder
    $ python -m sphinxcontrib.confluencebuilder --version
    sphinxcontrib.confluencebuilder <version>

Windows (virtualenv)
--------------------

If not already installed, download the most recent version of Python_:

    | Python — Downloads
    | https://www.python.org/downloads/

When invoking the installer, it is recommended to select the option to "Add
Python to PATH"; however, users can explicitly invoked Python from an absolute
path. The remainder of these steps will assume Python is available in the path.

Open a Windows command prompt as an administrator. Invoke the following to
install ``virtualenv``:

.. code-block:: doscon

    > pip install virtualenv

The command prompt started as an administrator can be closed.

Open a Windows command prompt (administrator mode is not required). Invoke the
following:

.. code-block:: doscon

    > virtualenv sphinx-venv
    > (or: python -m virtualenv sphinx-venv)
    > sphinx-venv\Scripts\activate.bat
    > python -m pip install sphinxcontrib-confluencebuilder
    > python -m sphinxcontrib.confluencebuilder --version
    sphinxcontrib.confluencebuilder <version>

.. references ------------------------------------------------------------------

.. _Python: https://www.python.org/
.. _pip: https://pip.pypa.io/
.. _virtualenv: https://virtualenv.pypa.io/
