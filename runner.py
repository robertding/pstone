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
import logging

import token
import basicParser

logging.basicConfig(level=logging.DEBUG)
parse_file = open('simple.ps', 'r')
lexer = token.Lexer(parse_file)


def lexer_runner():
    res = lexer.read()
    while not res.is_EOF():
        print("==> " + res.to_string())
        res = lexer.read()


def parser_runner():
    parser = basicParser.BasicParser()
    while not lexer.peek(0).is_EOF():
        ast = parser.parse(lexer)
        print("==>  " + str(ast))


def main():
    logging.debug("start")
    run = dict(lexer=lexer_runner,
               parser=parser_runner)
    run.get(sys.argv[1], sum)()

if __name__ == '__main__':
    main()
