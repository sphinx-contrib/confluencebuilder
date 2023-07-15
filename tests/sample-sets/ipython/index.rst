IPython
=======

.. ipython::

    In [136]: x = 2

    In [137]: x**3
    Out[137]: 8

Another demonstration of multi-line input and output

.. ipython::
    :verbatim:

    In [106]: print(x)
    jdh

    In [109]: for i in range(10):
       .....:     print(i)
       .....:
       .....:
    0
    1
    2
    3
    4
    5
    6
    7
    8
    9

Likewise, you can set ``:doctest:`` or ``:verbatim:`` to apply these
settings to the entire block.  For example,

.. ipython::
    :verbatim:

    In [9]: cd mpl/examples/
    /home/jdhunter/mpl/examples

    In [10]: pwd
    Out[10]: '/home/jdhunter/mpl/examples'


    In [14]: cd mpl/examples/<TAB>
    mpl/examples/animation/        mpl/examples/misc/
    mpl/examples/api/              mpl/examples/mplot3d/
    mpl/examples/axes_grid/        mpl/examples/pylab_examples/
    mpl/examples/event_handling/   mpl/examples/widgets

    In [14]: cd mpl/examples/widgets/
    /home/msierig/mpl/examples/widgets

    In [15]: !wc *
       2    12    77 README.txt
      40    97   884 buttons.py
      26    90   712 check_buttons.py
      19    52   416 cursor.py
     180   404  4882 menu.py
      16    45   337 multicursor.py
      36   106   916 radio_buttons.py
      48   226  2082 rectangle_selector.py
      43   118  1063 slider_demo.py
      40   124  1088 span_selector.py
     450  1274 12457 total

You can also have function definitions included in the source.

.. ipython::

    In [3]: def square(x):
       ...:     """
       ...:     An overcomplicated square function as an example.
       ...:     """
       ...:     if x < 0:
       ...:         x = abs(x)
       ...:     y = x * x
       ...:     return y
       ...:

Then call it from a subsequent section.

.. ipython::

    In [4]: square(3)
    Out [4]: 9

    In [5]: square(-2)
    Out [5]: 4
