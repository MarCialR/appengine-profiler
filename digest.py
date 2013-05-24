#!/usr/bin/python

"""Process a log file (probably from dev_appserver) and extract summary profile info."""


import re
import sys

import base64
import pickle
import zlib


requests_bin_tag = 'Datastore API requests-bin:'


def dict_add(d, k, v):
    if k in d:
        d[k] += v
    else:
        d[k] = v

def dict_sum(x, b):
    """Sum up data from request b into dict x."""
    if 'kinds' not in x:
        x['kinds'] = {}
    kinds_dict = x['kinds']
    kind_dict = None
    kind = b.get('kind')
    if kind and isinstance(kind, list):
        assert len(kind) == 1
        kind = kind[0]
    if kind:
        kind = kind.keys()[0]
        kind_dict = kinds_dict.get(kind)
        if not kind_dict:
            kind_dict = {}
            kinds_dict[kind] = kind_dict
    if 'calls' not in x:
        x['calls'] = {}
    calls_dict = x['calls']
    call_dict = None
    call = b.get('call')
    if call:
        call_dict = calls_dict.get(call)
        if call_dict is None:
            call_dict = {}
            calls_dict[call] = call_dict
    for k,v in b.iteritems():
        if v is None:
            #print '%s = %r' % (k, v)
            continue
        #if k is kind:
        #    pass
        if not isinstance(v, (int, float, long)):
            #print '%s = %r' % (k, v)
            continue
        dict_add(x, k, v)
        if kind_dict is not None:
            dict_add(kind_dict, k, v)
        if call_dict is not None:
            dict_add(call_dict, k, v)
    k = 'count'
    v = 1
    dict_add(x, k, v)
    if kind_dict is not None:
        dict_add(kind_dict, k, v)
    if call_dict is not None:
        dict_add(call_dict, k, v)
    


def read(fname):
    f = open(fname, 'r')
    total = {}
    count = 0
    for line in f:
        if requests_bin_tag in line:
            a, b = line.split(requests_bin_tag, 1)
            b = b.strip()
            requests = pickle.loads(zlib.decompress(base64.b64decode(b)))
            for req in requests:
                count += 1
                dict_sum(total, req)
    print '%s requests' % (count,)
    return total


def main():
    for arg in sys.argv[1:]:
        total = read(arg)
        kinds = total.pop('kinds')
        calls = total.pop('calls')
        #print 'kinds=%s' % (kinds,)
        print 'kinds:'
        kindkeys = kinds.keys()
        kindkeys.sort()
        for k in kindkeys:
            v = kinds[k]
            print '\t%s: %s' % (k, v)
        #print 'calls=%s' % (calls,)
        print 'calls:'
        callkeys = calls.keys()
        callkeys.sort()
        for k in callkeys:
            v = calls[k]
            print '\t%s: %s' % (k, v)
        print 'total: %s' % (total,)

if __name__ == '__main__':
    main()
