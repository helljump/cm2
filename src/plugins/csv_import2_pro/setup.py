# -*- coding: UTF-8 -*-

import sys
from cx_Freeze import setup, Executable

setup(
    name = "yml2json",
    version = "0.1",
    description = "yml to json converter",
    executables = [Executable("yml2json.py")]
)

