Math
====

.. attention::

    Support for math can require a LaTeX and dvipng/dvisvgm installation;
    unless HTML or Marketplace-installed LaTeX macros are available on the
    target instance. For more information, see the `math support guide`_.

.. only:: confluence_storage

    .. ifconfig:: confluence_editor == 'v2'

        .. attention::

            Limitations on Confluence Cloud:

            - Confluence Cloud does not allow image offset alignments in a paragraph.
            - Confluence Cloud does not render gracefully SVG-generated images.

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

Non-wrapped math example:

.. math::
   :nowrap:

   \begin{eqnarray}
      y    & = & ax^2 + bx + c \\
      f(x) & = & x^2 + 2xy + y^2
   \end{eqnarray}


.. references ------------------------------------------------------------------

.. _math directive: https://docutils.sourceforge.io/docs/ref/rst/directives.html#math
.. _math support guide: https://sphinxcontrib-confluencebuilder.readthedocs.io/guide-math/
