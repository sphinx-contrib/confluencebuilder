References
==========

This page provides example of references and related markup:

.. toctree::
    :hidden:

    references-ref

Basic
-----

A link can be built `in a paragraph`_. Links should also attempt to maintain
support for inline markup where possible. For example, |this example link|_
should be bolded.

.. _in a paragraph: http://www.example.com
.. _this example link: http://www.example.com
.. |this example link| replace:: **this example link**

Other examples of links include:

* https://www.example.com/subsection/another-page.html
* ftp://www.example.com
* mailto:someone@example.com
* someone@example.com

.. _example-hyperlink-references:

Targets
-------

`Hyperlink targets`_ (anchors) can be built. Clicking on this internal hyperlink
(targeta_) with being a user to an anchor above the following paragraph. A user
can also jump to the lower paragraph with either this first internal hyperlink
(targetb_) or this second internal hyperlink (targetc_). It is also possible to
:ref:`link<example-references-otherpage-label>` to targets on another page
(:ref:`example-references-otherpage-label`).

.. _targeta:

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus leo nunc,
commodo et risus ac, hendrerit aliquet est. Phasellus volutpat arcu at eros
tempus, sed sodales eros vehicula. Fusce dictum eros augue, eget iaculis ligula
sollicitudin nec. Sed dignissim quam leo, a imperdiet magna pharetra sed. In in
viverra libero. Maecenas mattis maximus condimentum. Integer ornare mauris nec
urna rutrum, eu iaculis augue molestie. Vivamus ultrices mattis quam id
condimentum. Phasellus tellus lacus, gravida sed porttitor ut, sodales at risus.
Phasellus mollis justo sed orci consectetur lacinia. Integer molestie lacinia
risus, et iaculis justo tristique ac. Nullam luctus ante sapien, in tristique
magna interdum ut. Vestibulum hendrerit tellus arcu, quis volutpat ligula auctor
nec. Maecenas sit amet justo orci.

.. _targetb:
.. _targetc:

Integer blandit interdum erat, sed interdum sapien varius et. Maecenas at tortor
quis velit mattis ultricies. Vivamus nisl leo, finibus ac tincidunt vitae,
pharetra quis orci. Maecenas lobortis neque ipsum, quis ultricies velit auctor
eu. Quisque pellentesque suscipit sodales. In sapien massa, tincidunt vel nisl
id, sodales bibendum dui. Pellentesque consectetur a risus sed aliquam.


.. references ------------------------------------------------------------------

.. _Hyperlink targets: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#hyperlink-targets
