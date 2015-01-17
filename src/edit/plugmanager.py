#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

from yapsy.PluginManager import PluginManager
import logging
import plugtypes
import os
import sys


log = logging.getLogger("yapsy").setLevel(logging.WARNING)


cwd = os.getcwd()
plugdir = os.path.join(cwd, "plugins")
userplug = os.path.expanduser('~/treeedit/plugins')
allplugs = [plugdir, userplug]
if not hasattr(sys, "frozen"):
    allplugs.append('d:/work/cm2/src/plugins')

pm = PluginManager(plugin_info_ext="cm-plugin")
ds = [row[0] for row in os.walk(plugdir)]
pm.setPluginPlaces(allplugs)
pm.setCategoriesFilter(plugtypes.categories)


def collect():
    pm.collectPlugins()


def getPlugins(plugtype):
    plugs = []
    for pluginInfo in pm.getPluginsOfCategory(plugtype):
        plug = pm.activatePluginByName(pluginInfo.name, pluginInfo.category)
        plugs.append((plug, pluginInfo.name, pluginInfo.description))
    return plugs


getExportPlugins = lambda t = plugtypes.Export: getPlugins(t)
getImportPlugins = lambda t = plugtypes.Import: getPlugins(t)
getArticlePlugins = lambda t = plugtypes.Article: getPlugins(t)
getProcessPlugins = lambda t = plugtypes.Process: getPlugins(t)
getUtilitePlugins = lambda t = plugtypes.Utilite: getPlugins(t)
