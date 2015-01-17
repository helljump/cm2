# -*- coding: UTF-8 -*-

import yaml
import json
import codecs
import sys
    
data = yaml.load(open(sys.argv[1]))
outdata = {}
for k,v in data.iteritems():
    if type(k)==tuple:
        outdata["%s..%s" % (k[0], k[1])] = v
    else:
        outdata["%s" % k] = v
json.dump(outdata, codecs.open(sys.argv[2],"wt","utf-8","replace"), ensure_ascii=False, indent=2)
