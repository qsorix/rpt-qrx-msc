.. Arete documentation master file, created by
   sphinx-quickstart on Sat Aug 21 11:15:23 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Bogus
======

--MAGIC-START-TAG--

Konfiguracja
===================

Configuration
--------------
.. module:: config.Configuration

.. autoclass:: config.Configuration.ConfiguredHost
   :members:

.. autoclass:: config.Configuration.ConfiguredTest
   :members:

.. autoclass:: config.Configuration.Configuration
   :members:

Model
------
.. module:: config.Model

..
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
.. module:: config.Laboratory

..
        #FIXME: schemat UML
          - Device
          - Interface (agregacja w Device)

.. autoclass:: config.Laboratory.Laboratory
   :members:

.. autoclass:: config.Laboratory.Device
   :members:
   :inherited-members:

.. autofunction:: config.Laboratory.create_laboratory
.. autofunction:: config.Laboratory.get_laboratory
.. autofunction:: config.Laboratory.add_device

Mapping
--------
.. module:: config.Mapping

..
        #FIXME: schemat UML ?

.. autoclass:: config.Mapping.Mapping
   :members:

.. autofunction:: config.Mapping.create_mapping
.. autofunction:: config.Mapping.get_mapping
.. autofunction:: config.Mapping.bind

Schedule
---------
.. automodule:: config.Schedule
   :members:

Global
-------
.. automodule:: config.Global
   :members:

Klasy wykonawcze
=================
.. automodule:: command.DriverPlugin
   :members:

.. automodule:: controller.ConnectionPlugin
   :members:

.. automodule:: controller.FrontendPlugin
   :members:

.. automodule:: common.Hooks
   :members:

--MAGIC-END-TAG--
