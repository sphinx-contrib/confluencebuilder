blockdiag
=========

.. blockdiag::

   diagram {
     A -> B -> C;
          B -> D;
   }

----

.. actdiag::

   actdiag {
     A -> B -> C -> D;

     lane {
       A; B;
     }
     lane {
       C; D;
     }
   }

----

.. nwdiag::

   nwdiag {
     network {
       web01; web02;
     }
     network {
       web01; web02; db01;
     }
   }

----

.. seqdiag::

   seqdiag {
     browser => webserver => database;
   }

----

.. rackdiag::

   rackdiag {
    // define height of rack
    16U;

    // define rack items
    1: UPS [2U];
    3: DB Server
    4: Web Server
    5: Web Server
    6: Web Server
    7: Load Balancer
    8: L3 Switch
   }

----

.. packetdiag::

   packetdiag {
      colwidth = 32
      node_height = 72

      0-15: Source Port
      16-31: Destination Port
      32-63: Sequence Number
      64-95: Acknowledgment Number
      96-99: Data Offset
      100-105: Reserved
      106: URG [rotate = 270]
      107: ACK [rotate = 270]
      108: PSH [rotate = 270]
      109: RST [rotate = 270]
      110: SYN [rotate = 270]
      111: FIN [rotate = 270]
      112-127: Window
      128-143: Checksum
      144-159: Urgent Pointer
      160-191: (Options and Padding)
      192-223: data [colheight = 3]
   }

----

.. blockdiag::
   :desctable:

   blockdiag {
      A -> B -> C;
      A [description = "browsers in each client"];
      B [description = "web server"];
      C [description = "database server"];
   }
