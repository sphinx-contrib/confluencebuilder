.. Cross-referencing arbitrary locations documentation:
   http://www.sphinx-doc.org/en/stable/markup/inline.html#cross-referencing-arbitrary-locations

   Limitations: Cross-referencing figures do not work since figures are not yet
   supported.

cross-referencing arbitrary locations
=====================================

| The following shows an example of Sphinx markup to perform cross-referencing
  with arbitrary locations. Jump to either sub-section:
  :ref:`example-cral-ss1-label`, :ref:`example-cral-ss2-label`,
  :ref:`example-cral-ss3-label`, :ref:`example-cral-ss4-label`
  :ref:`example-cral-ss5-label`

.. _example-cral-ss1-label:

sub-section 1
-------------

| Lorem ipsum dolor sit amet, consectetur adipiscing elit. Cras consequat erat
  ornare elit convallis convallis. Sed venenatis porttitor tortor non faucibus.
  Morbi ultrices, enim in venenatis ultricies, sem lacus tincidunt sem, porta
  commodo nulla tellus et leo. Cras lorem sapien, maximus vitae dui vitae,
  varius sodales leo. Class aptent taciti sociosqu ad litora torquent per
  conubia nostra, per inceptos himenaeos. Nullam a lobortis ipsum, tristique
  porta tortor. Nulla bibendum dui eu elit lobortis pellentesque. Curabitur ac
  nisl at libero dapibus pretium eu a diam. Proin vel mauris nec massa volutpat
  dapibus. Morbi commodo fermentum gravida. Ut porttitor sollicitudin orci eget
  fringilla. Quisque consectetur, mi ut ornare sodales, nibh urna lacinia orci,
  eget placerat nisi turpis vel nunc. Nulla posuere urna ut condimentum viverra.

.. _example-cral-ss2-label:

sub-section 2
-------------

| Cras nec nisl quam. Fusce sagittis molestie risus eu sollicitudin. Praesent
  euismod ultricies consectetur. Nulla porttitor, velit eu porta pretium, libero
  diam pellentesque lectus, in fringilla nisi lectus sit amet risus. Donec
  lacinia ullamcorper tincidunt. Suspendisse eget leo at purus sollicitudin
  ultrices ac vel metus. Nulla quis augue at est tristique faucibus. Ut ante
  elit, ullamcorper a quam in, faucibus tincidunt mauris. Cras ac nisl et lectus
  mollis ultrices quis ac felis.

.. _example-cral-ss3-label:

sub-section 3
-------------

| Curabitur posuere lobortis congue. Curabitur lobortis sed velit ac vulputate.
  Donec vitae faucibus dui, at elementum justo. Curabitur molestie dui purus, in
  mattis magna auctor vel. Proin euismod posuere mi at elementum. Proin congue
  rutrum ipsum tincidunt porta. Class aptent taciti sociosqu ad litora torquent
  per conubia nostra, per inceptos himenaeos. Cras posuere vitae justo nec
  tincidunt. Suspendisse potenti.

.. _example-cral-ss4-label:

sub-section 4
-------------

| Cras mollis ullamcorper augue, id luctus arcu. Phasellus blandit metus
  sollicitudin ullamcorper viverra. Integer vel eros consequat, feugiat augue
  at, fringilla odio. Vivamus ac scelerisque magna, id aliquet orci. Cras
  maximus lectus massa, at porta eros tempus eget. Pellentesque vitae fermentum
  nunc. Vestibulum venenatis finibus eros, quis posuere lorem fermentum id.
  Donec sit amet magna pellentesque, dictum massa sed, tristique ipsum.

.. _example-cral-ss5-label:

sub-section 5
-------------

| Proin quis porta sem. Donec quis euismod mi. Curabitur volutpat, dolor nec
  pretium dignissim, ex turpis efficitur nulla, ac laoreet neque libero et
  purus. Sed at commodo nisl. Suspendisse nec molestie enim. In diam nibh, porta
  non nisi eu, vulputate dictum dolor. Integer faucibus sapien nec metus
  dignissim pretium a in felis. Maecenas a nibh mollis, tristique erat vitae,
  accumsan diam.

cross-referencing with label
============================

Cross-referencing can also apply a custom label to the references. For example:

| :ref:`First Section <example-cral-ss1-label>`,
  :ref:`2nd<example-cral-ss2-label>`, :ref:`3rd<example-cral-ss3-label>`,
  :ref:`we have a forth section <example-cral-ss4-label>`, and our
  :ref:`last section <example-cral-ss5-label>`.

cross-referencing to another document
=====================================

| Let's :ref:`jump<example-cral-otherpage-label>` to the other document section
  here: :ref:`example-cral-otherpage-label`.
