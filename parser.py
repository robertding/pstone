#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   RobertDing
#   E-mail  :   robertdingx@gmail.com
#   Date    :   15/05/05 15:03:07
#   Desc    :   解析器组合子
#
from __future__ import absolute_import, division, with_statement

import logging


from ast import ASTLeaf
from ast import ASTList


class Parser(object):
    operators = dict()
    elements = []

    def __init__(self, parser, ast_class=None):
        if parser:
            self.elements = parser.elements
            self.ast_class = parser.ast_class
        else:
            self.reset(ast_class)

    def parse(self, lexer):
        logging.debug("Parser parse")
        res = []
        for e in self.elements:
            logging.debug("Parse elements e: {}".format(e))
            logging.debug("lexer left {}"
                          .format(map(lambda x: x.to_string(), lexer.queue)))
            e.parse(lexer, res)
        logging.debug("Parser parse finish")
        return res

    def match(self, lexer):
        if self.elements == []:
            return True
        else:
            ifmatch = self.elements[0].match(lexer)
            logging.debug("to match {}"
                          .format(map(lambda x: x.to_string(), lexer.queue)))
            logging.debug("parser {} match {}".
                          format(self.ast_class or self.elements[0], ifmatch))
            return ifmatch

    @staticmethod
    def rule(ast_class=None):
        return Parser(None, ast_class)

    def reset(self, ast_class=None):
        self.elements = []
        self.ast_class = ast_class
        return self

    def number(self, ast_class=None):
        self.elements.append(NumToken(ast_class))
        return self

    def string(self, ast_class=None):
        self.elements.append(StrToken(ast_class))
        return self

    def identifier(self, ast_class=None, reserved=None):
        self.elements.append(IdToken(ast_class, reserved))
        return self

    def token(self, pat):
        self.elements.append(Leaf(pat))
        return self

    def sep(self, *pats):
        self.elements.append(Skip(pats))
        return self

    def ast(self, pat):
        self.elements.append(Tree(pat))
        return self

    def or_(self, *parsers):
        self.elements.append(OrTree(parsers))
        return self

    def maybe(self, parser):
        p2 = Parser(parser)
        p2.reset()
        self.elements.append(OrTree([parser, p2]))
        return self

    def option(self, parser):
        self.elements.append(Repeat(parser, True))
        return self

    def repeat(self, parser):
        self.elements.append(Repeat(parser, False))
        return self

    def expression(self, ast_class, subexp, operators):
        self.elements.append(Expr(ast_class, subexp, operators))
        return self

    def insert_choices(self, parser):
        self.elements.append(Repeat(parser, True))
        e = self.elements.get(0)
        if isinstance(e, OrTree):
            e.insert(parser)
        else:
            p = Parser(self)
            self.reset()
            self.or_(parser, p)
        return self


class Element(object):
    def parse(self, lexer, res):
        raise NotImplementedError

    def match(self, lexer):
        raise NotImplementedError


class Tree(Element):
    def __init__(self, parser):
        self.parser = parser

    def parse(self, lexer, res):
        res.append(self.parser.parse(lexer))

    def match(self, lexer):
        return self.parser.match(lexer)


class OrTree(Element):
    def __init__(self, parser_list):
        self.plist = parser_list

    def parse(self, lexer, res):
        parser = self.choose(lexer)
        logging.debug("OrTree choose parser: {}".format(parser))
        if parser is None:
            raise BaseException
        else:
            res.append(parser.parse(lexer))

    def choose(self, lexer):
        for parser in self.plist:
            if parser.match(lexer):
                return parser
        return None

    def match(self, lexer):
        return self.choose(lexer) is not None

    def insert(self, parser):
        self.plist.insert(0, parser)


class Repeat(Element):
    def __init__(self, parser, only_once):
        self.parser = parser
        self.only_once = only_once

    def parse(self, lexer, res):
        while self.parser.match(lexer):
            astree = self.parser.parse(lexer)
            logging.debug("repeat match astree: {}".format(astree))
            if astree.__class__ != ASTList or astree.num_children() > 0:
                res.append(astree)
            if self.only_once:
                logging.debug("break")
                break

    def match(self, lexer):
        return self.parser.match(lexer)


class AToken(Element):
    def __init__(self, atype):
        if atype is None:
            atype = ASTLeaf
        self.ast_class = atype.__class__

    def parse(self, lexer, res):
        token = lexer.read()
        logging.debug("atoken read {}".format(token.to_string()))
        if self.test(token):
            res.append(self.ast_class(token))

    def match(self, lexer):
        return self.test(lexer.peek(0))

    def test(self):
        raise NotImplementedError


class IdToken(AToken):
    def __init__(self, atype, rdict):
        super(IdToken, self).__init__(atype)
        self.reserved = rdict or dict()

    def test(self, token):
        if token and token.is_identifier():
            if token.to_string() not in self.reserved:
                return True
        return False


class StrToken(AToken):
    def __init__(self, atype):
        super(StrToken, self).__init__(atype)

    def test(self, token):
        return token and token.is_string()


class NumToken(AToken):
    def __init__(self, atype):
        super(NumToken, self).__init__(atype)

    def test(self, token):
        return token and token.is_number()


class Leaf(Element):
    def __init__(self, pats):
        self.strtokens = pats

    def parse(self, lexer, res):
        logging.debug('Leaf parser: patterns {}'.format(self.strtokens))
        t = lexer.read()
        logging.debug("Leaf parser t: {}".format(t.to_string()))
        if t and t.is_identifier():
            for token in self.strtokens:
                if t.to_string() == token:
                    self.find(res, t)
                    return None
        if len(self.strtokens) > 0:
            raise BaseException

    def find(self, res, token):
        res.append(ASTLeaf(token))

    def match(self, lexer):
        t = lexer.peek(0)
        if t and t.is_identifier():
            for token in self.strtokens:
                if t.to_string() == token:
                    return True
        return False


class Skip(Leaf):
    def __init__(self, pats):
        super(Skip, self).__init__(pats)

    def find(self, res, token):
        return None


class Precedence(object):
    def __init__(self, v, a):
        self.value = v
        self.left_assoc = a


class Expr(Element):
    def __init__(self, ast_class, exp, operators_map):
        self.ops = operators_map
        self.factor = exp
        self.ast_class = ast_class

    def parse(self, lexer, res):
        right = self.factor.parse(lexer)
        prec = self.next_operator(lexer)
        while prec is not None:
            right = self.do_shift(lexer, right, prec.value)
            prec = self.next_operator(lexer)
        res.append(right)

    def do_shift(self, lexer, left, prec):
        astlist = [left]
        astlist.append(ASTLeaf(lexer.read()))
        right = self.factor.parse(lexer)
        pnext = self.next_operator(lexer)
        while pnext is not None and self.right_is_expr(prec, pnext):
            right = self.do_shift(lexer, right, pnext.value)
            pnext = self.next_operator(lexer)
        astlist.append(right)
        return astlist

    def next_operator(self, lexer):
        token = lexer.peek(0)
        if token.is_identifier():
            return self.ops.get(token.to_string(), None)
        else:
            return None

    def right_is_expr(self, prec, pnext):
        if pnext.left_assoc:
            return prec < pnext.value
        else:
            return prec <= pnext.value

    def match(self, lexer):
        return self.factor.match(lexer)
