#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   RobertDing
#   E-mail  :   robertdingx@gmail.com
#   Date    :   15/05/05 20:38:14
#   Desc    :   pstone 语法分析器
#
from __future__ import absolute_import, division, with_statement

import logging

import ast
import parser

from token import Token


rule = parser.Parser.rule


class BasicParser(object):
    reserved = []
    operators = dict()
    expr0 = rule()
    primary = rule(ast.PrimaryExpr)\
        .or_(rule().sep('(').ast(expr0).sep(')'),
             rule().number(ast.NumLiteral),
             rule().identifier(ast.Name, reserved),
             rule().string(ast.StringLiteral))
    factor = rule().or_(rule(ast.NegtiveExpr).sep('-').ast(primary), primary)
    expr = expr0.expression(ast.BinaryExpr, factor, operators)

    statement0 = rule()
    block = rule(ast.BlockStmnt)\
        .sep('{').option(statement0)\
        .repeat(rule().sep(';', Token.EOL).option(statement0))\
        .sep('}')

    simple = rule(ast.PrimaryExpr).ast(expr)
    statement = statement0.or_(
        rule(ast.IfStmnt).sep('if').ast(expr).ast(block)
        .option(rule().sep('else').ast(block)),
        rule(ast.WhileStmnt).sep('while').ast(expr).ast(block),
        simple)
    program = rule().or_(statement, rule(ast.NoneStmnt)).sep(";", Token.EOL)

    op_LEFT = True
    op_RIGTH = False

    def __init__(self):
        self.reserved.extend([';', '}', Token.EOL])

        self.operators.update([
            ('=', parser.Precedence(1, self.op_RIGTH)),
            ('==', parser.Precedence(2, self.op_LEFT)),
            ('>', parser.Precedence(2, self.op_LEFT)),
            ('<', parser.Precedence(2, self.op_LEFT)),
            ('+', parser.Precedence(3, self.op_LEFT)),
            ('-', parser.Precedence(3, self.op_LEFT)),
            ('*', parser.Precedence(4, self.op_LEFT)),
            ('/', parser.Precedence(4, self.op_LEFT)),
            ('%', parser.Precedence(4, self.op_LEFT))])

    def parse(self, lexer):
        logging.debug("basic Parser begin")
        return self.program.parse(lexer)
