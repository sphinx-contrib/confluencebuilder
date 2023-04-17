.. index:: Math; Math support

Math support
============

.. versionchanged:: 1.8 Support for using Confluence-supported LaTeX macros.
.. versionchanged:: 1.7 SVG-generated math images requires the
                         ``sphinx.ext.imgmath`` extension to be explicitly
                         registered to work.
.. versionchanged:: 1.4 Support both block and inlined math elements.
.. versionadded:: 1.2 Initial support for math.

Mathematical notation is supported when using the Confluence builder extension.
There are some limitations and special cases a user may wish to consider when
trying to get the most our of their documentation/environment.

The recommended approach for rendering math in Confluence is using Sphinx's
`sphinx.ext.imgmath`_ extension. This extension renders math via LaTeX and uses
either dvipng or dvisvgm to create PNG or SVG images which are published to
Confluence (which requires installing a LaTeX engine alongside the Sphinx
installation, such as a TeX suite/MiKTeX installation).

Math can be defined using the ``:math:`` role or the ``.. math::`` directive.
For example:

.. code-block:: rst

    The Pythagorean theorem formula is :math:`a^2 + b^2 = c^2`.

    The mass–energy equivalence formula:

    .. math::

        E = mc^2

The former case will generate math content in an inlined fashion, where the
latter will generate a math block. Math defined in this way is supported on
Sphinx's standard builders with the help of other Sphinx-provided math
extensions.

.. index:: Math; Recommended options

Recommended options for math
----------------------------

Ensure the `sphinx.ext.imgmath`_ extension is added to the documentation's
extension list:

.. code-block:: python

    extensions = [
        'sphinx.ext.imgmath',
        'sphinxcontrib.confluencebuilder',
    ]

If loading the `sphinx.ext.imgmath`_ extension conflicts with other builders,
the extension can be optionally included using an approach such as follows
(but may require additional changes depending on the environment):

.. code-block:: python

    import sys

    extensions = [
        'sphinxcontrib.confluencebuilder',
    ]

    if any('confluence' in arg for arg in sys.argv):
        extensions.append('sphinx.ext.imgmath')

The following are the recommended options to use:

.. code-block:: python

    imgmath_font_size = 14
    imgmath_image_format = 'svg'
    imgmath_use_preview = True

This configures the generated font size commonly observed on Confluence
instances, hints that images are generated into SVG images (for ideal image
scaling) and attempt to process the "depth" of an image to better align content
alongside text.

.. index:: Math; LaTeX macros

Support for LaTeX macros for math
---------------------------------

.. note::

    This section outlines how users can take advantage of LaTeX macros enabled
    on their Confluence instance. The Confluence builder extension only helps
    forward LaTeX-generated content directly into macros. How a LaTeX macro
    decides to handle/render LaTeX content is up to the provider supporting the
    macro.

.. note::

    Not all LaTeX macros support block and inline macros (normally, just the
    former).

.. note::

    Confluence builder will attempt to support numbered equations by adding
    a floating label alongside a rendered math block. The variety of LaTeX
    macros which exist and limitations in how LaTeX macros are structured in
    a page may prevent the ability to perfectly align these labels alongside
    the rendered math content.

A stock Confluence instance does not provided LaTeX support. This is the main
reason why the Confluence builder extension promotes the use of
`sphinx.ext.imgmath`_. However, if a user's Confluence instance supports a
marketplace add-on which provides LaTeX macro support, math content can instead
be injected into these macros instead.

To use a LaTeX macro, the ``confluence_latex_macro``
(:ref:`ref<confluence_latex_macro>`) configuration option can be used. This
option accepts either the name of a macro to use or a dictionary of macro
options to consider (the dictionary is for more complex configurations such as
when attempting to support block-specific and inlined-specific macros). For
example, to specify the macro to use for any LaTeX content, the following
can be used:

.. code-block:: python

    confluence_latex_macro = 'macro-name'

If an environment supports a macro which supports block and inlined content in
different macros, the following can be used:

.. code-block:: python

    confluence_latex_macro = {
        'block-macro': 'block-macro-name',
        'inline-macro': 'inline-macro-name',
        'inline-macro-param': 'inline-macro-parameter', # (optional)
    }

.. _guide_math_macro_names:

LaTeX macro names
~~~~~~~~~~~~~~~~~

What macro names to use will vary based off which macro types are installed
(if any). Please see the following table for reported macro names:

.. list-table::
    :header-rows: 1
    :widths: 40 60

    * - Marketplace Application

      - Configuration

    * - Content Formatting Macros for Confluence

      - .. code-block:: python

            confluence_latex_macro = 'latex-formatting'

    * - LaTeX for Confluence

      - .. code-block:: python

            confluence_latex_macro = 'orah-latex'

    * - LaTeX Math

      - .. code-block:: python

            confluence_latex_macro = {
                'block-macro': 'mathblock',
                'inline-macro': 'mathinline',
                'inline-macro-param': 'body',
            }

If a Confluence environment supports a different macro type, a user can
determine the name of the macro by:

1. Creating a new page on the Confluence instance
2. Adding a LaTeX macro on the page and saving
3. Selecting the page's option menu and selecting "View Storage format"
4. Look for the corresponding macro name inside an ``ac:name`` attribute (in
   this case, the macro's name is ``my-latex-macro``):

   .. code-block:: none

      <ac:structured-macro ac:name="my-latex-macro" ...>
        ...
      </ac:structured-macro>


.. references ------------------------------------------------------------------

.. _sphinx.ext.imgmath: https://www.sphinx-doc.org/en/master/usage/extensions/math.html#module-sphinx.ext.imgmath
