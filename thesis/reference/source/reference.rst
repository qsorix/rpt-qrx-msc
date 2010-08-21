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
#FIXME: schemat UML
  - Host
  - Interface (agregacja w Host)
  - Link (Klasa powiązania na połączeniu Interface-Interface)

.. autoclass:: config.Model.Model
   :members:

.. autoclass:: config.Model.Host
   :members:
   :inherited-members:

   .. method:: host[key]

      Zwróć wartość atrybutu `key`.

      Zwróci ``None`` jeśli podany atrybut nie został określony.

.. autoclass:: config.Model.Link
   :members:
   :inherited-members:

.. autofunction:: config.Model.create_model
.. autofunction:: config.Model.get_model
.. autofunction:: config.Model.add_host
.. autofunction:: config.Model.add_link

Laboratory
-----------
#FIXME: schemat UML
  - Device
  - Interface (agregacja w Device)


.. automodule:: config.Laboratory
   :members:
   :inherited-members:
   :undoc-members:

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

