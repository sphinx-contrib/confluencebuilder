Svgbob
======

.. svgbob::
    :font-family: Arial
    :font-size: 12

    +-------+       +--------+
    | Hello |------>| World! |
    +-------+       +--------+

Hamming distance between two strings of equal length is the number of
positions at which the corresponding symbols are different. For instance,
Hamming distance for a 3-bit string can be computed visually using a
3-bit binary cube:

.. svgbob::
    :align: center

        110              111
           *-----------*
          /|          /|
         / |     011 / |
    010 *--+--------*  |
        |  | 100    |  |
        |  *--------+--* 101
        | /         | /
        |/          |/
    000 *-----------*  001

The minimum distance between any two vertices is the Hamming distance
between the two bit vectors (e.g. 100→011 has distance 3).
