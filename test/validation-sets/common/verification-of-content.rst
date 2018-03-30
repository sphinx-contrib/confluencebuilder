verification of content
=======================

The following page tests a series of content containing characters which may
cause issues between documentation data, Confluence storage conversion and
Confluence data publishing.

.. consider this failed if any point has additional formatting

Handle strings to filter Confluence markup:

* With {braces} in them (macros).
* With caret^caret^ and tilde~tilde~ in them (super/subscript).
* With ??citations?? in them (citations).
* With -dashes- in them (deleted).
* With >greater-than> and <less-than< characters.
* With +pluses+ in them (inserted).
* With _underscores_ in them (emphasis).

.. consider this failed if any content is not an exact match of the source

Characters in a code block should be unaffected:

.. code-block:: xml

   <languages>
       <language name="c" />
       <language name="cpp" />
       <language name="c#" />
       <language name="xml">
           <option key="key" value="value" />
       </language>
   </languages>

.. consider this failed if any inlined content has additional formatting

Characters in inline literals should be unaffected:

    This is an ``??inline??`` ``+blocks+`` with ``*special*`` ``-characters-``.

.. consider this failed if Confluence renders "Letâ€™s see if..."

Let's see if this encoding on this page is improperly handled.
