#!/usr/bin/env python
# -*- coding: UTF-8 -*-

__author__ = "snöa"

from yapsy.PluginManager import IPlugin

Article = "Article"
Process = "Process"
Export = "Export"
Import = "Import"
Utilite = "Utilite"

class ICMPlugin(IPlugin):
    def configure(self):
        pass
    def run(self):
        pass

class IUtilitePlugin(ICMPlugin):
    pass
    
class IArticlePlugin(ICMPlugin):
    pass
    
class IProcessPlugin(ICMPlugin):
    pass
    
class IExportPlugin(ICMPlugin):
    pass

class IImportPlugin(ICMPlugin):
    pass

categories = {
    Article : IArticlePlugin,
    Process : IProcessPlugin,
    Export : IExportPlugin,
    Import : IImportPlugin,
    Utilite : IUtilitePlugin
}
