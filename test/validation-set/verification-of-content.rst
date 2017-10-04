:orphan:

verification of content
=======================

The following page tests a series of content containing characters which may
cause issues between documentation data, Confluence storage conversion and
Confluence data publishing.

Handle a string with {braces} in them.

Handle a string with >greater-than> and <less-than> characters.

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

.. consider this failed if Confluence renders "Letâ€™s see if..."

Let's see if this encoding on this page is improperly handled.
