:orphan:

.. reStructuredText Body Elements documentation:
   http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#body-elements

   Confluence Wiki Markup
   https://confluence.atlassian.com/doc/confluence-wiki-markup-251003035.html#ConfluenceWikiMarkup-Lists

body elements
=============

| The follow shows a series of body elements markup defined in reStructuredText
  and handled by the Sphinx engine:

bullet lists
------------

Here is an example of bullet lists:

- | This is the first bullet list item. The blank line above the first list item
    is required; blank lines between list items (such as below this paragraph)
	are optional.

- | This paragraph in the second item in the list.

  | This is the second paragraph in the second item in the list. The blank line
    above this paragraph is required. The left edge of this paragraph lines up
	with the paragraph above, both indented relative to the bullet.

  This is the third paragraph in the second item in the list. The left edge of
  this paragraph lines up with the paragraph above, both indented relative to
  the bullet.

  - | This is a sublist. The bullet lines up with the left edge of the text
      blocks above. A sublist is a new list so requires a blank line above and
	  below.

- This is the third item of the main list.
- This is the forth item of the main list.

This paragraph is not part of the list.

enumerated lists
----------------

Here is an example of enumerated lists:

#. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#. Fusce vestibulum erat id massa vehicula, a suscipit ligula vestibulum.

Another list:

#. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#. Fusce quis nibh quis dui aliquet maximus ac vel felis.
#. Duis vehicula sem non turpis eleifend imperdiet.

#. Maecenas ultricies neque ac dui ultricies pretium.

#. Donec vitae metus hendrerit, placerat tellus suscipit, venenatis diam.

#. Nulla at erat et odio accumsan dignissim et quis neque.

And another list:

1. Lorem ipsum dolor sit amet, consectetur adipiscing elit.

   a) Donec viverra nisi in magna vulputate blandit.
   b) Proin vulputate diam sit amet pharetra bibendum.

2. Morbi et massa eget nisi fermentum commodo.

   a) Sed varius dui sed dui maximus aliquet.
   b) Fusce mollis risus ac finibus accumsan.

Note: Only auto-enumeration is supported in this extension.

transition
----------

A transition (or horizontal rule) can be used to seperate content.

----

This is my content.
