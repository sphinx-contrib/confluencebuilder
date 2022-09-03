Enumerated list
===============

.. only:: confluence_storage

    .. attention::

        Only auto-enumerator lists (#) are supported. Using other types of
        enumerated lists will be handled as auto-enumerators.

.. only:: confluence_storage

    .. ifconfig:: confluence_editor == 'v2'

        .. attention::

            Limitations using the Fabric (``v2``) editor:

            - Enumerator lists do not support explicit styling.

reStructuredText supports defining `enumerated lists`_. Example markup is as
follows:

.. code-block:: none

    #. Curabitur tincidunt eros non auctor commodo.
    #. Fusce vestibulum erat id massa vehicula, a suscipit ligula vestibulum.
    #. Fusce quis nibh quis dui aliquet maximus ac vel felis.
    #. Duis vehicula sem non turpis eleifend imperdiet.

Output
------

An extended example of enumerated lists. Each list item should be tightly
compacted.

#. Curabitur tincidunt eros non auctor commodo.
#. Fusce vestibulum erat id massa vehicula, a suscipit ligula vestibulum.
#. Fusce quis nibh quis dui aliquet maximus ac vel felis.
#. Duis vehicula sem non turpis eleifend imperdiet.

An enumerated list can also contain multiple lines. There should be proper and
equal spacing between compact lists and equal spacing between lists containing
multiple blocks.

#. Fusce feugiat velit a semper scelerisque.

   Proin vitae justo sed lacus auctor bibendum a gravida enim.

   Nunc ut ex cursus, volutpat diam at, dictum felis.

   #. Nulla eget neque vitae magna semper malesuada commodo at nunc.

      Sed scelerisque nisl et tempor blandit.

      #. Donec tempor velit vel facilisis ullamcorper.

      #. Donec sodales augue id ante hendrerit, aliquet tempor tortor malesuada.

      Fusce commodo urna a ante vulputate, eu scelerisque tortor imperdiet.

   #. Aliquam varius dui vel congue convallis.

      Duis eget ligula sed leo accumsan vulputate vel a mi.

Enumerated lists can also be styled:

1. Sed in ante sed massa gravida rhoncus.

   a) Donec viverra nisi in magna vulputate blandit.
   b) Proin vulputate diam sit amet pharetra bibendum.

2. Morbi et massa eget nisi fermentum commodo.

   A) Curabitur porta purus at euismod lacinia.
   B) Etiam quis tortor ultrices, egestas est iaculis, ultricies libero.

3. Donec vitae lacus consectetur, vestibulum quam vitae, mattis nulla.

   1) Morbi eget enim fermentum, dictum eros non, pellentesque ante.
   2) Nam ut neque vulputate, vestibulum leo eget, consequat metus.

4. Nunc non nunc quis elit tempor cursus.

   I) Vivamus in metus sit amet libero dapibus dignissim sit amet vitae nibh.
   II) Morbi ut diam eget velit facilisis convallis ut ac nisl.

5. Aliquam vestibulum elit et pellentesque lacinia.

   i) Duis id justo consectetur, hendrerit dui et, viverra velit.
   ii) Aliquam dictum justo vitae scelerisque tempus.
   iii) Fusce et libero quis erat mattis porta.


.. references ------------------------------------------------------------------

.. _enumerated lists: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#enumerated-lists
