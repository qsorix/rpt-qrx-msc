#!/usr/bin/env python
# coding=utf-8

import Model
import Laboratory
import Mapping
import Schedule
import Resources
import Utils
import AreteMaster.common.Exceptions as Exceptions
import uuid
import traceback

class ConfiguredHost:
    """ Konfiguracja dotycząca hosta występującego w teście.

    Każdy obiekt odpowiada jednemu hostowi ze zdefiniowanego modelu. Nie
    powinieneś modyfikować udostępnianych wartości. Wyjątkiem jest sytuacja, w
    której tworzysz wtyczkę generującą komendy i obiekt tej klasy jest
    argumentem metod wtyczki.

    Zależnie od stadium przetwarzania, nie wszystkie atrybuty będą wypełnione.

    .. attribute:: model

       Host (:class:`~config.Model.Host`), któremu ten obiekt odpowiada.

    .. attribute:: device

       Urządzenie (:class:`~config.Laboratory.Device`), które zostało odwzorowane
       dla tego hosta.

    .. attribute:: schedule

       Plan testu (:class:`~config.Schedule.HostSchedule`) przypisany do hosta.

    .. attribute:: resources

       Lista zasobów używanych na hoście.

    .. attribute:: commands

       Komendy (:class:`~command.Generator.HostCommands`) utworzone dla hosta.

    """
    def __init__(self):
        self.model = None
        self.device = None
        self.schedule = None
        self.resources = []
        self.commands = None

class ConfiguredTest:
    """ Pełna konfiguracja testu.

    Obiekt gromadzi całą wiedzę o teście odczytaną z plików konfiguracyjnych
    oraz komendy wygenerowane przez uruchomione wtyczki.

    Zależnie od stadium przetwarzania, nie wszystkie atrybuty będą wypełnione.

    .. attribute:: hosts
       
       Słownik obiektów typu :class:`~config.Configuration.ConfiguredHost`
       czyli wszystkich hostów występujących w teście. Kluczami są nazwy hostów
       z modelu.

    .. attribute:: resources

       Słownik zdefiniowanych zasobów (:class:`~config.Resources.Resource`).
       Kluczami są nazwy podane przy tworzeniu zasobu.

    .. attribute:: end_policy

       Wartość określająca sposób, w jaki powinien zakończyć się test.
       Framework przekazuje ją z konfiguracji do wszystkich występujących w
       teście :class:`frontendów <Fronted>`.

    .. attribute:: triggers

       Słownik zdefiniowanych triggerów (:class:`~config.Schedule.Trigger`).
       Kluczami są nazwy podane przy tworzeniu triggerów.

    .. attribute:: model

       Referencja do struktury modelu.

    .. attribute:: laboratory

       Referencja do struktury laboratorium.

    .. attribute:: schedule

       Referencja do struktury planu.

    .. attribute:: mapping

       Referencja do struktury mapowania.

    """

    def __init__(self):
        """ Stwórz nowy test przypisując mu unikalny identyfikator. """
        self.test_uuid = uuid.uuid4()


    def sanity_check(self):
        """ Sprawdź poprawność konfiguracji.

        Sprawdzane są tylko podstawowe typy błędów jak np. brak wymaganego
        mapowania urządzeń. Metoda ma wyeliminować część błędów przed
        uruchomieniem testu, nie gwarantuje jednak, że konfiguracja pozwala
        poprawnie wykonać test.

        """
        for (name, host) in self.hosts.items():
            if name != host.model['name']:
                raise Exceptions.SanityError("Key name is different than element's name")

            if not host.model.bound():
                raise Exceptions.SanityError("Model host '%s' is not bound" % host.model['name'])

            device = host.device

            obligatory_attributes = ['connection', 'frontend']

            for attr in obligatory_attributes:
                if attr not in device.attributes():
                    raise Exceptions.SanityError("Device '%s' doesn't specify '%s' attribute" % (device['name'], attr))

            for (iname, interface) in host.model.interfaces().items():
                if iname != interface['name']:
                    raise Exceptions.SanityError("Key's name is different than element's name")

                if not interface.bound():
                    raise Exceptions.SanityError("Interface '%s' of model host '%s' is not bound" % (iname, name))

        if not Schedule.get_schedule().test_end_policy():
            raise Exceptions.SanityError("Test end policy not specified. Use test_end_policy(<policy>) in your configuration.")

class Configuration:
    """ Odczytywanie konfiguracji.

    Klasa implementuje metody pozwalające odczytać konfigurację definiowana w plikach.

    """
    def __init__(self):
        self._configured_test = []

    def read(self, files, cmdline_mappings = []):
        """ Wczytaj konfigurację z plików.

        .. attribute:: files
        
           Lista plików z konfiguracją. Zostaną one przetworzone w zadanej kolejności.

        .. attribute:: cmdline_mappings

           Lista mapowań zdefiniowanych w linii polecenia programu. Mapowania
           są postaci ``host:device`` lub ``host.interface:device.interface``.

       """

        globals = {}
        globals.update(Model.public_functions)
        globals.update(Laboratory.public_functions)
        globals.update(Mapping.public_functions)
        globals.update(Schedule.public_functions)
        globals.update(Resources.public_functions)
        locals  = {}

        for file in files:
            try:
                execfile(file, globals, locals)
            except Exception as e:
                raise Exceptions.ConfigurationError(e, traceback=traceback.format_exc())

        self._command_line_mappings(cmdline_mappings)

        self._sanity_check()

        self._combine_hosts()

        return self.configured_test()

    def configured_test(self):
        """ Zwróć odczytaną konfigurację. """
        return self._configured_test


    def _command_line_mappings(self, mappings):
        if not mappings: return

        #try:
        Mapping.create_mapping('command-line')
        for m in mappings:
            (model, device) = m.split(':')
            Mapping.bind(model, device)

        #except Exception as e:
            #raise e
            #raise Exceptions.ConfigurationError(e, "Could not parse command line mappings {0!r}".format(mappings));

    def _sanity_check(self):
        if not Model.get_model():
            raise Exceptions.SanityError("No model defined. You need to create a model. Did you forget to use 'create_model(name)' in your configuration?")

        if not Laboratory.get_laboratory():
            raise Exceptions.SanityError("No laboratory defined. You need to create a laboratory. Did you forget to use 'create_laboratory(name)' in your configuration?")

        if not Mapping.get_mapping():
            raise Exceptions.SanityError("No mapping defined. You need to create a mapping. Did you forget to use 'create_mapping(name)' in your configuration?")

        if not Schedule.get_schedule():
            raise Exceptions.SanityError("No schedule defined. You need to create a schedule. Did you forget to use 'create_schedule(name)' in your configuration?")
    
    def _combine_hosts(self):
        ct = ConfiguredTest()
        ct.resources = Resources.resources.resources()
        ct.hosts = {}
        ct.end_policy = Schedule.get_schedule().test_end_policy()
        ct.setup_phase_delay = Schedule.get_schedule().setup_phase_delay()
        ct.triggers = Schedule.get_schedule().triggers()

        for h in Model.get_model().hosts():
            host = ConfiguredHost()
            host.model = h
            host.device = h.bound()
            host.schedule = Schedule.get_schedule().host_schedule(h['name'])

            resources = set(h.needed_resources())
            for event in host.schedule:
                resources.update(event.command().needed_resources())

            def resolve_resource(r):
                if isinstance(r, str):
                    return Utils.resolve_resource_name(r)
                return r

            host.resources = set(map(resolve_resource, resources))

            ct.hosts[h['name']] = host

        ct.sanity_check()

        ct.model = Model.get_model()
        ct.laboratory = Laboratory.get_laboratory()
        ct.schedule = Schedule.get_schedule()
        ct.mapping = Mapping.get_mapping()

        self._configured_test = ct

