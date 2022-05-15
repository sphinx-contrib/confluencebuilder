.. https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#tables

tables
------

.. spanning table

+----+----+----+----+
| 00 | 01 | 02 | 03 |
+====+====+====+====+
| 10 | 11 | 12 | 13 |
+----+----+----+----+
| 20 |    2[1-3]    |
+----+----+---------+
| 30 |    | - one   |
+----+ ZZ | - two   |
| 40 |    | - three |
+----+----+---------+

.. multi-header table

== == ==
a1 a2 a3
b1 b2 b3
== == ==
c1 c2 c3
d1 d2 d3
== == ==

.. nested table

+--------+--------+
| cell 1 | cell 2 |
+========+========+
| cell 3 | cell 4 |
|        |        |
|        | +-+-+  |
|        | |a|b|  |
|        | +=+=+  |
|        | |c|d|  |
|        | +-+-+  |
|        | |e|f|  |
|        | +-+-+  |
+--------+--------+
