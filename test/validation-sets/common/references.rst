references and related
======================

This page provides example of references and related markup:

.. contents::
   :local:

generic references
------------------

The most common method reference with Sphinx is a "`phrase-reference`_";
consider the example of `this phrase being a link`_. Phrase-reference links can
be on `two lines`_ or `various lines`_ -- all which should appear as several
inline links within a single paragraph.

.. _this phrase being a link: http://www.example.com

.. _two lines: https://
   www.example.com

.. _various lines:
   http://www.example.com
   /home
   /index

Hyperlinks should also attempt to maintain support for inline markup where
possible. For example, |this example link|_ should be bolded.

.. _this example link: http://www.example.com

.. |this example link| replace:: **this example link**

hyperlinks
----------

`Hyperlinks`_ are handled automatically. A document can define a link using with
various protocols, such as http://www.example.com,
https://www.example.com/subsection/another-page.html or even
ftp://www.example.com.

Emails links can be formed as well using the mailto prefix such as
mailto:someone@example.com or without the prefix (someone@example.com).

hyperlink references
--------------------

`Hyperlink references`_ are another method to form hyperlinks in a document. A
document can define `in-line links <http://www.example.com/custom>`_ to specific
URIs. Documents can also link to pages anonymously; for example, using
`link a`__ and `link b`__. All reStructuredText hyperlink types should render
appropriately in Confluence.

__ http://www.example.com/static/doc-a.txt
__ http://www.example.com/static/doc-b.txt

.. _example-hyperlink-references:

hyperlink targets
-----------------

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

citations
---------

A page can have multiple `citations`_ [CIT2001]_, and it does not matter on the
order which they are used [CIT2003]_. Adding a series of lorem ipsum to help
increase spacing to help visualize citation references:

Lorem ipsum dolor sit amet, consectetur adipiscing elit. In pulvinar ante id
tellus sollicitudin vehicula. Sed viverra, risus eu feugiat fermentum, mi enim
tincidunt magna, id tristique sapien leo nec mauris. Nullam lobortis velit
turpis, at pharetra nulla suscipit quis. Phasellus hendrerit ultricies quam, et
egestas tellus. Sed vitae posuere odio, eget semper sem. Ut a mattis orci,
blandit porta massa. Vivamus et arcu non est gravida dignissim [CIT2004]_. Sed
ut bibendum tellus. Donec ullamcorper facilisis odio, non facilisis leo
scelerisque non. Ut auctor ante a lectus egestas porta. Quisque bibendum euismod
massa, ac tempor velit. Class aptent taciti sociosqu ad litora torquent per
conubia nostra, per inceptos himenaeos. Mauris tincidunt eget mauris in
facilisis. Nam a consectetur nisi. Cras orci dolor, porta sit amet porttitor
nec, rutrum mollis velit. Mauris nec neque convallis, convallis erat ac,
tristique diam.

Integer molestie odio eget sapien vulputate placerat. Nullam bibendum facilisis
diam, at varius orci pellentesque eu. Vestibulum auctor elit sed sagittis
pretium. Donec volutpat arcu nec mi semper pulvinar et sit amet tellus. Nam
tempor vitae dolor non iaculis. Ut porttitor, tortor non vehicula luctus, metus
magna aliquam nulla, vitae finibus arcu nulla a metus. Etiam in libero non velit
vehicula maximus eget vel ex. Donec in ligula dignissim, mattis elit id,
venenatis enim.

Wherever the citations are defined within a document, Confluence table will be
built [CIT2002]_.

.. [CIT2001] This is an example citation.
.. [CIT2002] It's true, a does not matter the order of citation's used, the \
   respective citation point will be referenced.
.. [CIT2003] Another citation example.
.. [CIT2004] The last citation example.

footnotes
---------

There are various types of `footnote`_ methods styles that can be applied. A
document can reference the first footnote [#note]_ using a label; and it render
as "[1]". A document can also refer to the footnote again [#note]_ and it should
again be seen as "[1]". A document can also use its label form, note_, to refer
to the footnote (i.e. as an internal hyperlink reference).

.. [#note] This is the footnote labeled "note".
.. [#] This is the footnote labeled "note".

You can also reference footnotes after the fact either explicitly [#note]_ or
anonymously [#]_.

A standard way to use footnotes is in an incremental fashion. The first [#]_ and
second [#]_ footnotes should be "[3]" and "[5]" (anonymous auto-numbered).
Adding an additional line of test to help space our the footnote examples to
help visually see footnote references in play. The next anonymous auto-numbered
footnotes, [#]_ and [#]_, will actually be "[6]" and "[7]". A document can also
manually override the footnote number [4]_ (a value of "[4]"). Adding a series
of lorem ipsum to help increase spacing to help visualize footnote references:

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse eget mattis
purus, vitae dapibus ipsum. Quisque non nulla magna. Cras euismod nec ligula et
accumsan. Suspendisse ullamcorper nisi aliquet tellus tempus consectetur. Fusce
quis dolor auctor, vehicula nulla eu, sollicitudin mi. Duis auctor metus sit
amet metus rutrum, et malesuada quam dignissim. Nullam lobortis urna a tempor
mollis. In sagittis leo ut euismod tincidunt. Quisque nunc sapien, blandit sed
est et, rutrum cursus ipsum. Suspendisse aliquet lacus sit amet elit dignissim,
vitae lobortis erat pellentesque. Morbi sollicitudin tempor nibh et semper.
Curabitur sed lectus gravida, tincidunt arcu sit amet, congue velit. Interdum et
malesuada fames ac ante ipsum primis in faucibus.

.. [4] This is footnote 4.
.. [#] This is footnote 3.
.. [#] This is footnote 5.
.. [#] This is footnote 6.
.. [#] This is footnote 7.

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer ut elit sapien.
Morbi tristique hendrerit pretium. Duis non lacus vitae ex interdum commodo at
ut diam. Curabitur suscipit odio sit amet lorem luctus, non molestie mauris
luctus. Vivamus vulputate, arcu non cursus tempus, ipsum elit scelerisque massa,
vitae faucibus tortor elit ac enim. Ut quis nulla at justo mollis sodales.
Maecenas malesuada molestie sapien non dapibus.

Pellentesque tempus sed ligula facilisis placerat. Fusce nec aliquam augue.
Vestibulum consectetur augue libero, blandit cursus neque varius eu. Phasellus
accumsan augue et convallis venenatis. Pellentesque habitant morbi tristique
senectus et netus et malesuada fames ac turpis egestas. Curabitur vulputate
feugiat tortor, eget viverra eros viverra sodales. Ut arcu lacus, cursus nec
libero sed, convallis tincidunt est. Donec ut risus in elit tempor sagittis sed
et neque. Aliquam feugiat ut justo id pellentesque. Quisque sit amet tortor
tellus. Pellentesque habitant morbi tristique senectus et netus et malesuada
fames ac turpis egestas.

Ut porttitor id ipsum ac venenatis. Donec eu finibus leo. Duis a nulla
consequat, feugiat dui eu, imperdiet mi. Morbi vitae molestie odio, in feugiat
enim. Morbi consectetur velit quam. Nulla fermentum auctor ligula at dignissim.
Quisque in ultrices dui. Maecenas ornare maximus nisl a tempus. Pellentesque
tempor lacus vitae auctor tempus. Quisque interdum ex nec lorem imperdiet
fringilla.

Quisque sed ultricies dolor. Aenean ut commodo purus. Nam commodo lorem ut nunc
venenatis luctus. Phasellus imperdiet odio nec magna porttitor tincidunt. Morbi
sit amet nisi risus. Praesent mi est, imperdiet at porta id, viverra et quam.
Integer et dictum nibh. Fusce pretium non eros vitae rutrum. Mauris quis
consectetur tellus. Suspendisse iaculis in orci ut lacinia. Suspendisse in
tristique ex, sit amet faucibus dui. Sed iaculis pretium dui, eu egestas risus
ullamcorper sit amet. Cras aliquam consectetur sodales. Sed elit nulla,
consequat in venenatis at, gravida non magna. Sed felis elit, vehicula ac
aliquam eget, congue quis magna. Phasellus tincidunt tincidunt ante.

Long gap to easily observed anchor usage...

.. raw:: confluence

   <div style="height: 1000px">&nbsp;</div>

End of gap.

Cras quis est placerat, vehicula est at, malesuada nisl. Quisque eu mollis ex,
vitae vehicula metus. Nullam non eros sem. Nam tempor libero sagittis est
dignissim condimentum. Nunc laoreet, lorem ut ultricies fringilla, ex tortor
mattis massa, ac tincidunt risus felis eget odio. Nullam lectus tellus, mollis
et hendrerit sed, euismod ac sem. Etiam auctor sem enim, at tincidunt libero
sodales vel.

.. _Hyperlink references: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#hyperlink-references
.. _Hyperlink targets: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#hyperlink-targets
.. _Hyperlinks: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#standalone-hyperlinks
.. _citations: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#citations
.. _footnote: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#footnotes
.. _phrase-reference: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#reference-names
