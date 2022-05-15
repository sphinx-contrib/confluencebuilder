.. https://docutils.sourceforge.io/docs/ref/rst/directives.html#figure

figure
------

.. external image (default align; no caption)

.. figure:: https://www.example.com/image.png
    :alt: alt text

.. external image (default align)

.. figure:: https://www.example.org/image.png

    caption 2

    legend 2

.. external image (left align)

.. figure:: https://www.example.com/image.png
    :align: left
    :alt: alt text

    caption 3

    legend 3

.. internal image (center align)

.. figure:: ../../../assets/image02.png
    :align: center

    caption 4

    legend 4

.. internal image (right align)

.. figure:: ../../../assets/image02.png
    :align: right

    caption 5

    legend 5
