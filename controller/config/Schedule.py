#!/usr/bin/env python
# coding=utf-8

from BaseMixins import NamedMixin

from Utils import resolve_host_name

class Command:
    """
    Komenda do wykonania w czasie testu.

    Klasa bazowa dla komend definiowanych przez użytkownika. Pozwala dodatkowo
    wygenerować testy poprawności, jak np. sprawdzenie wymaganych uprawnień, a
    także określić, że komenda wymaga dołączenia zasobów.

    .. method:: command()
    
       Zwróć napis z właściwą komendą do wykonania.

    .. method:: accept_transformation(transformation_function)

       Zastosuj na przechowywanej komendzie podaną funkcję i zapamiętaj
       zwrócony wynik. Interfejs ten jest używany do przeprowadzania operacji
       na wszystkich komendach w teście, jak np. podmianie występujących w nich
       parametrów.

    """

    def sanity_checks(self):
        """
        Zwróć listę dodatkowych poleceń sprawdzających poprawność.

        Można tutaj np. wykonać polecenie, które sprawdzi czy wymagany przez
        komendę program jest dostępny.

        Domyślna implementacja zwraca pustą listę.
        """
        return []

    def needed_resources(self):
        """
        Zwróć listę wymaganych przez komendę zasobów. Zasoby te zostaną
        dopisane do listy zasobów hosta, na którym docelowo wykonywana będzie
        komenda.

        Domyślna implementacja zwraca pustą listę.
        """
        return []

class RunPolicy:
    """
    Klasa bazowa dla strategii wykonania komend.

    Budując plan testu dla hosta określa się, w których momentach mają być
    uruchamiane polecenia. Służy do tego właśnie strategia wykonania komendy.

    Ponieważ strategii jest wiele, a zależnie od zastosowanego frontendu może
    być konieczne poinstruowanie go w inny sposób, zastosowany został wzorzec
    projektowy Visitor. Dla każdego obsługiwanego frontendu należy w tej klasie
    zaimplementować metodę:

    .. method:: schedule_for_frontend(self)

       Zwraca napis, który przesłanie zostany do kontrolowanego urządzenia.
       
    Gdzie `frontend` należy zastąpić odpowiednią nazwą.
    """
    pass

class Event(NamedMixin):
    """Zdarzenie łączy komendę `command` ze strategią wykonania `run_policy`.
    Zdarzenie posiada nazwę `name`.

    Jest to klasa pomocnicza stosowana w celu łatwiejszej organizacji danych.
    """
    def __init__(self, name, run_policy, command):
        self.rename(name)
        self._run_policy = run_policy
        self._command = command

    def run_policy(self):
        """Zwróć przechowywaną strategię wykonania."""
        return self._run_policy

    def command(self):
        """Zwróć przechowywaną komendę."""
        return self._command

class Schedule(NamedMixin):
    """Plan testu."""
    def __init__(self, name):
        self.rename(name)
        self._schedules = {}
        self._test_end_policy = None
        self._setup_phase_delay = 1.0 # 1 second default

    def set_test_end_policy(self, test_end_policy):
        self._test_end_policy = test_end_policy

    def test_end_policy(self):
        return self._test_end_policy

    def set_setup_phase_delay(self, setup_phase_delay):
        self._setup_phase_delay = setup_phase_delay

    def setup_phase_delay(self):
        return self._setup_phase_delay

    def host_schedule(self, host):
        """Zwróć plan dla danego hosta."""
        if isinstance(host, str):
            host = resolve_host_name(host)

        return self._schedules.setdefault(host['name'], HostSchedule())

    def append_schedule(self, host, schedule):
        """Dopisz komendy do planu dla danego hosta."""
        if isinstance(host, str):
            host = resolve_host_name(host)

        host_schedule = self.host_schedule(host['name'])

        for name, run_policy, command in schedule:
            e = Event(name, run_policy, command)
            host_schedule.append(e)

class HostSchedule(list):
    """
    Lista organizująca komendy przeznaczone dla hosta.
    """
    def schedule(self, name, run_policy, command):
        """
        Stwórz :class:`Event` i dodaj go do listy.
        """
        self.append(Event(name, run_policy, command))
        return self

_schedule = None

def create_schedule(name):
    """Stwórz plan testu o nazwie `name`.

    Obecna implementacja dopuszcza istnienie tylko jednego planu.
    """

    global _schedule
    if _schedule:
        raise Exceptions.ConfigurationError('You cannot create more than one schedule.')
    _schedule = Schedule(name)

def get_schedule(validate=True):
    """Zwróć plan testu.

    Funkcja rzuca wyjątek, jeśli plan nie został utworzony. Jeśli w argumencie
    `validate` przekazano ``False`` wyjątek nie będzie rzucony i funkcja zwróci None.

    """
    global _schedule
    if validate and _schedule is None:
        raise Exceptions.ConfigurationError('These is no schedule. Did you forget to call \'create_schedule(name)\'?')
    return _schedule

def append_schedule(*args, **kwargs):
    """Dopisz do planu kolejne zdarzenia.

    Patrz :meth:`Schedule.append_schedule`.
    """
    return get_schedule().append_schedule(*args, **kwargs)

def test_end_policy(end_policy, setup_phase_delay = None):
    get_schedule().set_test_end_policy(end_policy)
    if setup_phase_delay:
        get_schedule().set_setup_phase_delay(setup_phase_delay)

public_functions = {
    'create_schedule': create_schedule,
    'get_schedule': get_schedule,
    'append_schedule': append_schedule,
    'test_end_policy': test_end_policy
}
