:orphan:

.. http://docutils.sourceforge.net/docs/ref/rst/directives.html#figure

figure
------

.. external image (default align; no caption)

.. figure:: https://www.example.com/image.png
   :alt: alt text

.. external image (default align)

.. figure:: https://www.example.com/image.png
   :alt: alt text

   caption

   legend

.. external image (left align)

.. figure:: https://www.example.com/image.png
   :align: left
   :alt: alt text

   caption

   legend

.. internal image

.. figure:: ../assets/image02.png
   :align: center

   caption

   legend

.. internal image shared with other pages (see figure); asset stored on master

.. figure:: ../assets/image03.png
   :align: right

   caption

   legend
