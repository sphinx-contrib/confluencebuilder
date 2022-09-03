Glossary
========

Sphinx defines a `glossary`_. Glossary operate like a definition list;
however, a glossary provides referenceable terms. Example markup is as
follows:

.. code-block:: none

    .. glossary::

        glossary-item-01
            Lorem ipsum dolor sit amet, consectetur adipiscing elit.

        glossary-item-02
            Cras vehicula rutrum nibh.

        glossary-item-03a
        glossary-item-03b
            Pellentesque dictum ornare arcu a interdum.

Output
------

.. glossary::

    glossary-item-01
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam nec velit
        mauris. Ut eget enim at turpis semper finibus vel eget lorem. Mauris
        metus ligula, scelerisque eget accumsan non, maximus in massa. In eget
        ullamcorper lectus, quis dignissim quam. Nulla viverra, purus in gravida
        dapibus, ex ipsum elementum felis, eget euismod massa nunc ut leo. Nam
        feugiat orci tortor, ac lacinia eros dignissim vel. Cras bibendum
        efficitur velit bibendum ultrices. Quisque id nisi magna. Ut porta
        mauris velit, ut varius ligula rutrum sit amet. Praesent sagittis
        egestas ex, consectetur porta felis egestas ac. Quisque vitae eros
        felis.

    glossary-item-02
        Cras vehicula rutrum nibh. Nullam mollis consequat fermentum. Praesent
        dapibus, neque sed ultrices elementum, orci dolor sollicitudin enim, id
        volutpat dolor ligula eu urna. Fusce eu venenatis est. Morbi rutrum mi
        nisl, quis mattis est congue vitae. Duis at dui sit amet ex pulvinar
        eleifend quis sed quam. Mauris nibh nisi, convallis at enim vel,
        tincidunt porta augue. Nam sed tellus nec justo mollis sodales sed in
        nunc. Aenean eu vestibulum nulla. Ut efficitur accumsan dolor ut
        laoreet. Proin rutrum condimentum purus at ultrices. Fusce convallis
        felis id ex viverra imperdiet. Nullam eget ipsum ipsum. Vestibulum eu
        nibh dictum, pellentesque nibh ac, aliquet purus.

    glossary-item-03a
    glossary-item-03b
        Pellentesque dictum ornare arcu a interdum. Mauris pellentesque commodo
        lobortis. Quisque non lorem felis. Integer quis bibendum purus. Maecenas
        cursus, odio nec ultricies vulputate, orci urna vulputate neque, vel
        placerat sapien nisl vitae nibh. Ut aliquam mauris cursus varius
        hendrerit. Donec justo odio, viverra a mi eu, egestas sollicitudin est.

Glossary and referencing
########################

Documentation may define a reference to a specific glossary entry:

.. code-block:: none

    :term:`glossary-item-01`

For example:

* :term:`glossary-item-01`
* :term:`glossary-item-03b`


.. references ------------------------------------------------------------------

.. _glossary: https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#directive-glossary
