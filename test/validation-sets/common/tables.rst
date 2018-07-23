.. reStructuredText Tables documentation:
   http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#tables

   Confluence Wiki Markup - Tables
   https://confluence.atlassian.com/doc/confluence-storage-format-790796544.html#ConfluenceStorageFormat-Tables

tables
======

The following shows a series of table examples can that be formed.

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

Table-inside-table supported as well:

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

Complex tables without headers:

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

Contination lines work in simple tables as well:

=====  =====
col 1  col 2
=====  =====
1      Second column of row 1.
2      Second column of row 2.
       Second line of paragraph.
3      - Second column of row 3.

       - Second item in bullet
         list (row 3, column 2).
\      Row 4; column 1 will be empty.
=====  =====
