# -*- coding: utf-8 -*-
from __future__ import absolute_import
"""
Registers and loads Processor classes from settings.
"""
# Python imports
import logging
# Django imports
from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured
# Local imports
from . import exceptions
from . import saml2idp_metadata

# Setup logging
logger = logging.getLogger(__name__)

def get_processor(config):
    """
    Get an instance of the processor with config.

    """
    dottedpath = config['processor']

    try:
        dot = dottedpath.rindex('.')
    except ValueError:
        raise ImproperlyConfigured('%s isn\'t a processors module' % dottedpath)
    sp_module, sp_classname = dottedpath[:dot], dottedpath[dot+1:]
    try:
        mod = import_module(sp_module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing processors %s: "%s"' % (sp_module, e))
    try:
        sp_class = getattr(mod, sp_classname)
    except AttributeError:
        raise ImproperlyConfigured('processors module "%s" does not define a "%s" class' % (sp_module, sp_classname))

    instance = sp_class(config)
    return instance

def find_processor(request):
    """
    Returns the Processor instance that is willing to handle this request.
    """
    for name, sp_config in saml2idp_metadata.SAML2IDP_REMOTES.items():
        proc = get_processor(sp_config)
        try:
            if proc.can_handle(request):
                return proc
        except exceptions.CannotHandleAssertion as exc:
            # Log these, but keep looking.
            logger.debug('%s %s' % (proc, exc))

    raise exceptions.CannotHandleAssertion('None of the processors in SAML2IDP_REMOTES could handle this request.')