lists
=====

The follow shows a series of lists related markup defined in reStructuredText
and handled by the Sphinx engine.

.. contents::
   :depth: 1
   :local:

bullet lists
------------

The following is an example of `bullet lists`_. Each list item should be tightly
compacted.

- Lorem ipsum dolor sit amet, consectetur adipiscing elit.
- Vestibulum vitae erat a nunc hendrerit sodales.
- Maecenas at est in justo ullamcorper malesuada non et nisi.

  - Ut vitae sapien interdum erat molestie fringilla.
  - Sed sodales erat sit amet suscipit tempus.
  - Donec placerat sem nec urna dapibus, id malesuada magna blandit.
  - Aenean eu purus vel eros convallis blandit.
  - Aliquam sed lacus id elit ultrices auctor vitae et libero.

- Fusce aliquam lorem sit amet ante tristique, sed dapibus ex dictum.

  - Maecenas fermentum nisl vitae arcu cursus pulvinar.
  - Integer molestie lectus ut erat finibus, a sagittis ligula blandit.
  - Praesent quis nisi nec diam dictum vehicula id quis lorem.
  - Vivamus aliquam est ac ex vehicula, vitae vestibulum orci aliquet.

    - Integer commodo massa nec elit porta, suscipit viverra eros molestie.
    - Nulla rutrum turpis nec mauris vestibulum placerat.

  - Proin egestas augue eu nisi aliquet, a consequat sem venenatis.
  - Nunc tempor velit et varius convallis.

- Ut auctor eros at turpis venenatis bibendum.
- Nunc faucibus nisi vitae tortor porttitor, sit scelerisque lectus sagittis.
- Curabitur lobortis augue vitae bibendum sodales.
- Etiam venenatis orci eu ante suscipit lobortis ut vel lacus.

  - Ut fringilla diam luctus, vehicula felis et, lacinia leo.
  - Quisque et est scelerisque, porta libero quis, porttitor massa.
  - Suspendisse a massa rhoncus, efficitur ex sit amet, hendrerit tortor.

A bullet list can also contain multiple lines. There should be proper and equal
spacing between compact lists and equal spacing between lists containing
multiple blocks.

- Proin sed lorem non ligula varius porta.

  Morbi eleifend nibh sit amet nibh ultricies, eu egestas orci iaculis.

  Aliquam eget nibh blandit, malesuada urna vehicula, mollis neque.

  - Quisque molestie lorem sit amet mi tempus lobortis.

    Vivamus eget risus vehicula, pretium lectus eget, congue augue.

    - Morbi dignissim ipsum non felis molestie convallis.

  - Aliquam malesuada sapien at ligula posuere pulvinar.

    - In in sem nec sem tempus aliquet.
    - Proin eget dolor quis mi congue vulputate.
    - Cras ultricies enim pretium turpis convallis malesuada.

    Morbi id libero ut neque bibendum pellentesque vel in quam.

  - Praesent elementum tortor nec ultrices sodales.

    Quisque dictum leo sit amet dolor tincidunt, a convallis tellus laoreet.

This paragraph is not part of the list.

enumerated lists
----------------

Here is an example of `enumerated lists`_. Each list item should be tightly
compacted.

#. Curabitur tincidunt eros non auctor commodo.
#. Fusce vestibulum erat id massa vehicula, a suscipit ligula vestibulum.
#. Fusce quis nibh quis dui aliquet maximus ac vel felis.
#. Duis vehicula sem non turpis eleifend imperdiet.

An enumerated list can also contain multiple lines. There should be proper and
equal spacing between compact lists and equal spacing between lists containing
multiple blocks.

#. Fusce feugiat velit a semper scelerisque.

   Proin vitae justo sed lacus auctor bibendum a gravida enim.

   Nunc ut ex cursus, volutpat diam at, dictum felis.

   #. Nulla eget neque vitae magna semper malesuada commodo at nunc.

      Sed scelerisque nisl et tempor blandit.

      #. Donec tempor velit vel facilisis ullamcorper.

      #. Donec sodales augue id ante hendrerit, aliquet tempor tortor malesuada.

      Fusce commodo urna a ante vulputate, eu scelerisque tortor imperdiet.

   #. Aliquam varius dui vel congue convallis.

      Duis eget ligula sed leo accumsan vulputate vel a mi.

Enumerated lists can also be styled:

1. Sed in ante sed massa gravida rhoncus.

   a) Donec viverra nisi in magna vulputate blandit.
   b) Proin vulputate diam sit amet pharetra bibendum.

2. Morbi et massa eget nisi fermentum commodo.

   A) Curabitur porta purus at euismod lacinia.
   B) Etiam quis tortor ultrices, egestas est iaculis, ultricies libero.

3. Donec vitae lacus consectetur, vestibulum quam vitae, mattis nulla.

   1) Morbi eget enim fermentum, dictum eros non, pellentesque ante.
   2) Nam ut neque vulputate, vestibulum leo eget, consequat metus.

4. Nunc non nunc quis elit tempor cursus.

   I) Vivamus in metus sit amet libero dapibus dignissim sit amet vitae nibh.
   II) Morbi ut diam eget velit facilisis convallis ut ac nisl.

5. Aliquam vestibulum elit et pellentesque lacinia.

   i) Duis id justo consectetur, hendrerit dui et, viverra velit.
   ii) Aliquam dictum justo vitae scelerisque tempus.
   iii) Fusce et libero quis erat mattis porta.


definition lists
----------------

The following is an example of `definition lists`_. A user should be able to
easily see a term entry and an associated description for the term. Classifiers
may also exist for a term and should be presented along side it.

term 1
   Lorem ipsum dolor sit amet, consectetur adipiscing elit.

term 2
   Maecenas at leo eget metus cursus tempor.

   Pellentesque egestas orci id purus facilisis, eu vestibulum dolor feugiat.

term 3 : classifier
   Nunc ac quam lacinia, viverra orci vel, varius dui.

term 4 : classifier one : classifier two
   Vivamus vel dolor eget mauris mollis dictum.

glossary
--------

Sphinx defines `glossary markup`_ which is like a definition list; however, a
glossary provides referenceable terms.

.. glossary::

   glossary-item-01
      Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam nec velit
      mauris. Ut eget enim at turpis semper finibus vel eget lorem. Mauris
      metus ligula, scelerisque eget accumsan non, maximus in massa. In eget
      ullamcorper lectus, quis dignissim quam. Nulla viverra, purus in gravida
      dapibus, ex ipsum elementum felis, eget euismod massa nunc ut leo. Nam
      feugiat orci tortor, ac lacinia eros dignissim vel. Cras bibendum
      efficitur velit bibendum ultrices. Quisque id nisi magna. Ut porta
      mauris velit, ut varius ligula rutrum sit amet. Praesent sagittis
      egestas ex, consectetur porta felis egestas ac. Quisque vitae eros felis.

   glossary-item-02
      Cras vehicula rutrum nibh. Nullam mollis consequat fermentum. Praesent
      dapibus, neque sed ultrices elementum, orci dolor sollicitudin enim, id
      volutpat dolor ligula eu urna. Fusce eu venenatis est. Morbi rutrum mi
      nisl, quis mattis est congue vitae. Duis at dui sit amet ex pulvinar
      eleifend quis sed quam. Mauris nibh nisi, convallis at enim vel,
      tincidunt porta augue. Nam sed tellus nec justo mollis sodales sed in
      nunc. Aenean eu vestibulum nulla. Ut efficitur accumsan dolor ut
      laoreet. Proin rutrum condimentum purus at ultrices. Fusce convallis felis
      id ex viverra imperdiet. Nullam eget ipsum ipsum. Vestibulum eu nibh
      dictum, pellentesque nibh ac, aliquet purus.

   glossary-item-03a
   glossary-item-03b
      Pellentesque dictum ornare arcu a interdum. Mauris pellentesque commodo
      lobortis. Quisque non lorem felis. Integer quis bibendum purus. Maecenas
      cursus, odio nec ultricies vulputate, orci urna vulputate neque, vel
      placerat sapien nisl vitae nibh. Ut aliquam mauris cursus varius
      hendrerit. Donec justo odio, viverra a mi eu, egestas sollicitudin est.

glossary and referencing
########################

Example of referencing glossary entries:

 * :term:`glossary-item-01`
 * :term:`glossary-item-03b`

list table
----------

The following is an example of a `list table`_:

.. list-table:: name1
   :header-rows: 1

   * - Treat
     - Quantity
     - Description
   * - Albatross
     - 2.99
     - On a stick!
   * - Crunchy Frog
     - 1.49
     - If we took the bones out, it wouldn't be crunchy, now would it?
   * - Gannet Ripple
     - 1.99
     - On a stick!

Another example of a list table with multiple header rows:

.. list-table:: name2
   :header-rows: 2

   * - key1
     - value1
     - description1
   * - key2
     - value2
     - description2
   * - 1
     - 2
     - 3
   * - 4
     - 5
     - 6
   * - 7
     - 8
     - 9

option lists
------------

The following is an example of an `option lists`_ for a (Linux) ``ping``
command:

-a         Audible ping.

-A         Adaptive ping. Interpacket interval adapts to round-trip time, so
           that effectively not more than one (or more, if preload is set)
           unanswered probes present in the network. Minimal interval is 200msec
           for not super-user. On networks with low rtt this mode is essentially
           equivalent to flood mode.

-b         Allow pinging a broadcast address.

-B         Do not allow ping to change source address of probes. The address is
           bound to one selected when ping starts.

-c count   Stop after sending count ECHO_REQUEST packets. With *deadline*
           option, ping waits for count ECHO_REPLY packets, until the timeout
           expires.

-i interval
           Wait interval seconds between sending each packet. The default is to
           wait for one second between each packet normally, or not to wait in
           flood mode. Only super-user may set interval to values less 0.2
           seconds.

-L         Suppress loopback of multicast packets. This flag only applies if the
           ping destination is a multicast address.

-n         Numeric output only. No attempt will be made to lookup symbolic names
           for host addresses.

-Q tos     Set Quality of Service-related bits in ICMP datagrams. *tos* can be
           either decimal or hex number. Traditionally (RFC1349), these have
           been interpreted as:

           - 0 for reserved (currently being redefined as congestion control)
           - 1-4 for Type of Service
           - 5-7 for Precedence

           Possible settings for Type of Service are:

           - minimal cost: 0x02
           - reliability: 0x04
           - throughput: 0x08
           - low delay: 0x10

           Multiple TOS bits should not be set simultaneously. Possible settings
           for special Precedence range from priority (0x20) to net control
           (0xe0). You must be root (CAP_NET_ADMIN capability) to use Critical
           or higher precedence value. You cannot set bit 0x01 (reserved) unless
           ECN has been enabled in the kernel. In RFC2474, these fields has been
           redefined as 8-bit Differentiated Services (DS), consisting of: bits
           0-1 of separate data (ECN will be used, here), and bits 2-7 of
           Differentiated Services Codepoint (DSCP).

-q         Quiet output. Nothing is displayed except the summary lines at
           startup time and when finished.

-t ttl     Set the IP Time to Live.

-T option  Set special IP timestamp options. timestamp option may be either
           *tsonly* (only timestamps), *tsandaddr* (timestamps and addresses) or
           *tsprespec host1 [host2 [host3 [host4]]]* (timestamp prespecified
           hops).

-v         Verbose output.

-V         Show version and exit.

-W timeout
           Time to wait for a response, in seconds. The option affects only
           timeout in absence of any responses, otherwise ping waits for two
           RTTs.

production list
---------------

The following is an example of a `production list`_:

.. productionlist::
   try_stmt: try1_stmt | try2_stmt
   try1_stmt: "try" ":" `suite`
            : ("except" [`expression` ["," `target`]] ":" `suite`)+
            : ["else" ":" `suite`]
            : ["finally" ":" `suite`]
   try2_stmt: "try" ":" `suite`
            : "finally" ":" `suite`

.. _bullet lists: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#bullet-lists
.. _definition lists: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#definition-lists
.. _enumerated lists: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#enumerated-lists
.. _glossary markup: http://www.sphinx-doc.org/en/stable/markup/para.html#glossary
.. _list table: http://docutils.sourceforge.net/docs/ref/rst/directives.html#list-table
.. _option lists: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#option-lists
.. _production list: http://www.sphinx-doc.org/en/stable/markup/para.html#directive-productionlist
