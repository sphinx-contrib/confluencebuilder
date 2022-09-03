Citations
#########

reStructuredText supports defining `citations`_. Example markup is as
follows:

.. code-block:: none

    A page can have multiple citations [CIT2001]_.

    .. [CIT2001] This is an example citation.

Output
------

A page can have multiple citations [CIT2001]_, and it does not matter on the
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


.. references ------------------------------------------------------------------

.. _citations: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#citations
