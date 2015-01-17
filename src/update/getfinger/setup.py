# -*- coding: UTF-8 -*-

import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Console'

includes = ['encodings']
excludes = ['sip']

buildOptions = dict(
    includes=includes,
    excludes=excludes,
    optimize=2,
    copy_dependent_files=True,
    create_shared_zip=True,
    silent=True,
)

mainfile = Executable(
    'getfingerprint.py',
    base=base,
)

setup(
    name='cm2gfp',
    version='1.0.0.0',
    options=dict(build_exe=buildOptions),
    description='Content Monster 2 GFP',
    executables=[mainfile],
)
