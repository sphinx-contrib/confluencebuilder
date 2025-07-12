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

Reference in a list: `other values`_

#. Curabitur tincidunt eros non auctor commodo.
#. Fusce vestibulum erat id massa vehicula, a suscipit ligula vestibulum.

   .. _other values:

#. Fusce quis nibh quis dui aliquet maximus ac vel felis.
#. Duis vehicula sem non turpis eleifend imperdiet.

Integer aliquet purus elementum leo pulvinar elementum. Aenean id orci cursus,
viverra velit id, aliquam ipsum. Pellentesque nec magna ultricies, consequat
metus a, sollicitudin libero. Aenean placerat, nibh at fermentum rutrum, metus
nulla interdum mauris, sit amet sagittis diam elit vel elit. Vestibulum a
mattis metus, et condimentum metus. Praesent pharetra, nisi ullamcorper
tincidunt convallis, purus dolor placerat justo, at sodales elit nisl sed nisi.
Nam bibendum tempor elit a fermentum. Vivamus tellus massa, vulputate a dolor
eu, placerat pharetra justo. Pellentesque habitant morbi tristique senectus et
netus et malesuada fames ac turpis egestas. Nunc fringilla nibh id dictum
semper. Nam pharetra, tortor at porttitor sollicitudin, eros erat ultricies
ante, nec cursus dui risus nec velit.

Cras cursus in magna non ultrices. In nulla arcu, malesuada a blandit id,
pretium ac dui. Praesent porta sodales turpis, vitae efficitur libero finibus
sit amet. Nulla vitae molestie leo. Suspendisse nisl sapien, pulvinar ut
ultricies ac, placerat vel ipsum. Pellentesque in ex volutpat, tincidunt eros
sed, tristique nisi. Suspendisse sit amet dui justo. Maecenas convallis ligula
a vestibulum pulvinar. Phasellus magna magna, maximus eu elit lacinia,
venenatis ultrices libero.

Mauris lobortis fringilla vestibulum. Donec quis sagittis erat. Mauris bibendum
metus magna, sit amet pellentesque nibh mollis vitae. Maecenas interdum eget
mi ac consectetur. Pellentesque fermentum gravida nisi, quis accumsan leo
fringilla posuere. Proin sed luctus ipsum. Sed sit amet augue dui. Donec
lobortis porta sapien, sit amet faucibus ipsum iaculis at. Nunc vel enim vel
neque malesuada lacinia. Aliquam ante velit, interdum vitae purus eu, tristique
placerat augue. Etiam ut consequat neque. Praesent tempor metus in lorem
efficitur iaculis. Vivamus enim risus, molestie sed massa sit amet, iaculis
facilisis velit. Aenean ornare tincidunt vestibulum. Nulla bibendum nisi in
neque congue rutrum. 

.. references ------------------------------------------------------------------

.. _Hyperlink targets: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#hyperlink-targets
