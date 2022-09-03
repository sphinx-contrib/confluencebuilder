Option list
===========

reStructuredText supports building `option lists`_. Example markup is as
follows:

.. code-block:: none

    -a         Audible ping.

    -A         Adaptive ping. Interpacket interval adapts to round-trip time,
               so that effectively not more than one (or more, if preload
               is set) unanswered probes present in the network. Minimal
               interval is 200msec for not super-user. On networks with low
               rtt this mode is essentially equivalent to flood mode.

    -b         Allow pinging a broadcast address.

    ...

Output
------

An extended example of (Linux) ``ping`` command:

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


.. references ------------------------------------------------------------------

.. _option lists: https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html#option-lists
