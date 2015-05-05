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

import token
import basicParser


parse_file = open(sys.argv[1], 'r')
lexer = token.Lexer(parse_file)


def lexer_runner():
    res = lexer.read()
    while res is not token.Token.EOF:
        print("==> " + res.to_string())
        res = lexer.read()


def parser_runner():
    parser = basicParser.BasicParser()
    while lexer.peek(0) != token.Token.EOF:
        ast = parser.parse(lexer)
        print("==>  " + ast.to_string())


def main():
    run = dict(lexer=lexer_runner,
               parser=parser_runner)
    run.get(sys.argv.get(1), lambda x: x)()

if __name__ == '__main__':
    main()
