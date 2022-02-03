#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
# License: GPLv3 Copyright: 2019, Kovid Goyal <kovid at kovidgoyal.net>


# The class that all Interface Action plugin wrappers must inherit from
from calibre.customize import InterfaceActionBase


class noosfereutil(InterfaceActionBase):
    '''
    This class is a simple wrapper that provides information about the actual
    plugin class. The actual interface plugin class is called InterfacePlugin
    and is defined in the ui.py file, as specified in the actual_plugin field
    below.

    The reason for having two classes is that it allows the command line
    calibre utilities to run without needing to load the GUI libraries.
    '''
    name                = "noosfere utilités"
    description         = ("Utilités pour noosfere DB, permet de xchoisir et fixer"
                        "le nsfr_id avant de lancer la recherche de metadata. "
                        )#"Annule les champs tels que series remplis par erreur. "
                        #"Redistribue les informations liées aux editeurs")
    supported_platforms = ['windows', 'osx', 'linux']
    author              = 'Kovid Goyal'
    version             = (0, 5, 0)
    minimum_calibre_version = (5, 35, 0)

    #: This field defines the GUI plugin class that contains all the code
    #: that actually does something. Its format is module_path:class_name
    #: The specified class must be defined in the specified module.
    actual_plugin       = 'calibre_plugins.noosfere_util.ui:InterfacePlugin'
