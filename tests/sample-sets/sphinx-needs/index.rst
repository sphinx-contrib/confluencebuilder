needs
=====

.. req:: A more complex and highlighted requirement
   :id: EX_REQ_2
   :status: open
   :tags: awesome, nice, great
   :links: EX_REQ_1
   :layout: complete
   :style: red_border

   More columns for better data structure and a red border.

.. req:: A focused requirement
   :id: EX_REQ_3
   :status: open
   :style: red
   :layout: focus_r

   This also a requirement, but we focus on content here.
   All meta-data is hidden.

.. req:: A custom requirement with picture
   :author: daniel
   :id: EX_REQ_4
   :tags: example
   :status: open
   :layout: example
   :style: yellow, blue_border

   This example uses the value from **author** to reference an image.
   See :ref:`layouts_styles` for the complete explanation.

   :status: open
   :tags: requirement; test; awesome

   This is my **first** requirement!!

   .. note:: You can use any rst code inside it :)

.. spec:: Specification of a requirement
   :id: OWN_ID_123
   :links: R_F4722

   Outgoing links of this spec: :need_outgoing:`OWN_ID_123`.

.. impl:: Implementation for specification
   :id: IMPL_01
   :links: OWN_ID_123

   Incoming links of this spec: :need_incoming:`IMPL_01`.

.. test:: Test for XY
   :status: implemented
   :tags: test; user_interface; python27
   :links: OWN_ID_123; IMPL_01

   This test checks :need:`IMPL_01` for :need:`OWN_ID_123` inside a
   Python 2.7 environment.

As :need:`IMPL_01` shows, the linked :need:`OWN_ID_123` is realisable.
