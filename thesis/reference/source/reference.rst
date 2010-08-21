.. Arete documentation master file, created by
   sphinx-quickstart on Sat Aug 21 11:15:23 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Arete's documentation!
=================================

Contents:

.. toctree::
   :maxdepth: 2

Master
=======

Configuration
--------------
.. autoclass:: config.Configuration.ConfiguredHost
   :members:

.. autoclass:: config.Configuration.ConfiguredTest
   :members:

.. autoclass:: config.Configuration.Configuration
   :members:

Model
------
.. autoclass:: config.Model.Host

.. automodule:: config.Model
   :members:
   :inherited-members:
   :undoc-members:

#FIXME: schemat UML
  - Host
  - Interface (agregacja w Host)
  - Link (Klasa powiązania na połączeniu Interface-Interface)

Laboratory
-----------

.. automodule:: config.Laboratory
   :members:
   :inherited-members:
   :undoc-members:

#FIXME: schemat UML
  - Device
  - Interface (agregacja w Device)

Mapping
--------

.. automodule:: config.Mapping
   :members:
   :inherited-members:
   :undoc-members:

#FIXME: schemat UML ?

Schedule
---------

.. automodule:: config.Schedule
   :members:
   :inherited-members:
   :undoc-members:

Global
-------

.. automodule:: config.Global
   :show-inheritance:
   :members:
   :undoc-members:


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

