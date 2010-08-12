#!/usr/bin/env python

from common import Exceptions

def resolve_name(name, model=False, laboratory=False):
    if not model and not laboratory:
        model = True
        laboratory = True

    if model:
        try:
            return resolve_interface_name(name, model=True)
        except Exceptions.ConfigurationError:
            pass

        try:
            return resolve_host_name(name)
        except Exceptions.ConfigurationError:
            if laboratory:
                pass
            else:
                raise

    if laboratory:
        try:
            return resolve_interface_name(name, laboratory=True)
        except Exceptions.ConfigurationError:
            pass

        return resolve_device_name(name)

    raise Exceptions.ConfigurationError("Name '%s' cannot be resolved to an object." % name)

def resolve_entity_name(name, type, container):
    base_error = "Name '%s' cannot be used as a %s reference." % (name, type)

    if not name:
        raise Exceptions.ConfigurationError(base_error)

    if name.count('.'):
        raise Exceptions.ConfigurationError(base_error + " You cannot use '.' charater")

    for e in container:
        if e['name']== name:
            return e

    raise Exceptions.ConfigurationError(base_error + " There is no %s named '%s'." % (type, name))

def resolve_host_name(name):
    from config.Model import get_model
    return resolve_entity_name(name, 'host', get_model().hosts())

def resolve_device_name(name):
    from config.Laboratory import get_laboratory
    return resolve_entity_name(name, 'device', get_laboratory().devices())

def resolve_interface_name(name, model=False, laboratory=False):
    if not model and not laboratory:
        model = True
        laboratory = True

    sections = name.split('.')
    base_error = "Name '%s' cannot be used as an interface reference." % name
    if not (len(sections) == 2 and sections[0] and sections[1]):
        raise Exceptions.ConfigurationError(base_error + " Use 'host.interface' format.")

    entity = None
    if model and not laboratory:
        entity = resolve_host_name(sections[0])

    if laboratory and not model:
        entity = resolve_device_name(sections[0])

    if model and laboratory:
        try:
            entity = resolve_host_name(sections[0])
        except Exceptions.ConfigurationError:
            try:
                entity = resolve_device_name(sections[0])
            except Exceptions.ConfigurationError:
                raise Exceptions.ConfigurationError(base_error + " There is no host, neither device named '%s'." % sections[0])

    interface = None

    try:
        interface = entity.interface(sections[1])
    except KeyError:
        raise Exceptions.ConfigurationError(base_error + " Object '%s' has no interface named '%s'." % (sections[0], sections[1]))

    return interface

