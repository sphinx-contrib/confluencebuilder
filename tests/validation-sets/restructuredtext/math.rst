Math
====

.. attention::

    Support for math requires a LaTeX and dvipng/dvisvgm installation; unless
    Marketplace-installed LaTeX macros are available on the target instance.

.. only:: confluence_storage

    .. ifconfig:: confluence_editor == 'v2'

        .. attention::

            Limitations using the Fabric (``v2``) editor:

            - Confluence does not allow image offset alignments in a paragraph.
            - Confluence does not render gracefully SVG-generated images.

reStructuredText defines a `math directive`_. Example markup is as follows:

.. code-block:: none

    .. math::

        E = mc^2

Output
------

The area of a circle is :math:`A_\text{c} = (\pi/4) d^2`.

The mass–energy equivalence formula:

.. math::

    E = mc^2

Euler's identity is outline in :math:numref:`euler` below:

.. math:: e^{i\pi} + 1 = 0
    :label: euler


.. references ------------------------------------------------------------------

.. _math directive: https://docutils.sourceforge.io/docs/ref/rst/directives.html#math
