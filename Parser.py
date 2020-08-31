#!/usr/bin/env python3

import json
import os
import tempfile

from parser import ParserInternal

__all__ = [ 'parse' ]

def parse(filename):
    assert(os.path.exists(filename))
    with open(filename, 'r') as f:
        return ParserInternal.do(f.read())

def test():
    ret = parse(os.path.join('parser', 'Student.test.java'))
    expect = {}
    assert(ret == expect)

if __name__ == "__main__":
    test()