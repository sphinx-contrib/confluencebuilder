tables
======

The following shows a series of `reStructuredText's tables`_ that can be formed.

grid tables
-----------

Complex grid-like "ASCII art" tables can be used to form tables in Confluence:

+------------------------+------------+----------+----------+
| Header row, column 1   | Header 2   | Header 3 | Header 4 |
| (header rows optional) |            |          |          |
+========================+============+==========+==========+
| body row 1, column 1   | column 2   | column 3 | column 4 |
+------------------------+------------+----------+----------+
| body row 2             | Cells may span columns.          |
+------------------------+------------+----------+----------+
| body row 3             | Cells may  | - Cells can contain |
+------------------------+ span rows. | - items such as     |
| body row 4             |            | - this list.        |
+------------------------+------------+----------+----------+

Table-inside-table are supported as well:

+---------+--------------------------------------------------------------------+
| Index   | Content                                                            |
+=========+====================================================================+
| First   | This cell contains another table:                                  |
|         |                                                                    |
|         | =====  =====  =======                                              |
|         |   A      B    A and B                                              |
|         | =====  =====  =======                                              |
|         | False  False  False                                                |
|         | True   False  False                                                |
|         | False  True   False                                                |
|         | True   True   True                                                 |
|         | =====  =====  =======                                              |
+---------+--------------------------------------------------------------------+
| Second  | This cell contains a table in another table.                       |
|         |                                                                    |
|         | +---------+------------------------------------------------------+ |
|         | | Index2  | More Content                                         | |
|         | +=========+======================================================+ |
|         | | idx-a   | =====  =====  =======                                | |
|         | |         |   A      B    A and B                                | |
|         | |         | =====  =====  =======                                | |
|         | |         | False  False  False                                  | |
|         | |         | True   False  False                                  | |
|         | |         | False  True   False                                  | |
|         | |         | True   True   True                                   | |
|         | |         | =====  =====  =======                                | |
|         | +---------+------------------------------------------------------+ |
|         | | idx-b   | =====  =====  =======                                | |
|         | |         | False  False  False                                  | |
|         | |         | True   False  False                                  | |
|         | |         | False  True   False                                  | |
|         | |         | True   True   True                                   | |
|         | |         | =====  =====  =======                                | |
|         | +---------+------------------------------------------------------+ |
+---------+--------------------------------------------------------------------+

Complex tables can be built with headers excluded:

+--------------+----------+-----------+-----------+
| row 1, col 1 | column 2 | column 3  | column 4  |
+--------------+----------+-----------+-----------+
| row 2, col 1 | column 2 | column 3  | column 4  |
+--------------+----------+-----------+-----------+
| row 3, col 1 | column 2 | column 3  | column 4  |
+--------------+----------+-----------+-----------+

simple tables
-------------

Simple tables are a common approach to represent data:

=====  =====  =======
  A      B    A and B
=====  =====  =======
False  False  False
True   False  False
False  True   False
True   True   True
=====  =====  =======

Simple table without headers:

=====  =====  =====
False  False  False
True   False  False
False  True   False
True   True   True
=====  =====  =====

Simple table with multiple headers:

=====  =====  =====
 A-1    B-1    C-1
 A-2    B-2    C-2
=====  =====  =====
False  False  False
True   False  False
False  True   False
True   True   True
=====  =====  =====

This simple table shows a series of additional markup being used within a table:

========  =====
Column 1  *Column*:sup:`2`
========  =====
1         Second column of row 1.
2         Second ``column`` of row 2.

          Second line of paragraph.
3         - Second column of row 3.

          - Second item in bullet
            list (row 3, column 2).
\         Row 4; column 1 will be empty.
========  =====

.. _reStructuredText's tables: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#tables
