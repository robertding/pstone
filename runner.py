#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   RobertDing
#   E-mail  :   robertdingx@gmail.com
#   Date    :   15/04/29 17:32:52
#   Desc    :   测试分词
#
from __future__ import absolute_import, division, with_statement

import sys

import pstone


def main():
    parse_file = open(sys.argv[1], 'r')
    parse = pstone.Lexer(parse_file)
    res = parse.read()
    while res is not pstone.Token.EOF:
        print("==> " + res.to_string())
        res = parse.read()

if __name__ == '__main__':
    main()
