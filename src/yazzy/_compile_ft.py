#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#@author: snoa

import sys
sys.path.append('d:/work/cm2/src')
from yasyn2 import _loadCSV, save_py


fname, d1 = _loadCSV( u"fullthematik.csv" )
save_py( fname.replace(".csv",".py"), d1 )
