#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   RobertDing
#   E-mail  :   robertdingx@gmail.com
#   Date    :   15/05/05 15:01:54
#   Desc    :   构造语法树
#
from __future__ import absolute_import, division, with_statement


class ASTree(object):
    def child(self, i):
        raise NotImplementedError

    def num_children(self):
        raise NotImplementedError

    def location(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError


class ASTLeaf(ASTree):
    def __init__(self, token):
        self.token = token

    def num_children(self):
        return 0

    def to_string(self):
        return self.token.to_string()

    def location(self):
        return "at line " + self.token.line_number

    def __iter__(self):
        return None


class ASTList(ASTree):
    def __init__(self, astlist):
        self.astlist = astlist or []

    def child(self, i):
        return self.astlist[i]

    def num_children(self):
        return len(self.astlist)

    def __iter__(self):
        return self.astlist.__iter__

    def to_string(self):
        return ' '.join(t.to_string() for t in self.astlist)

    def location(self):
        for i in self.astlist:
            if i.location() is not None:
                return i.location()
        return None


class NumLiteral(ASTLeaf):
    def __init__(self, token):
        super(ASTLeaf, self).__init__(token)

    def value(self):
        return self.token.num


class Name(ASTLeaf):
    def __init__(self, token):
        super(ASTLeaf, self).__init__(token)

    def name(self):
        return self.token.to_string()


class BinaryExpr(ASTList):
    def __init__(self, astlist):
        super(ASTList, self).__init__(astlist)

    def left(self):
        return self.child(0)

    def right(self):
        return self.child(2)

    def operator(self):
        return self.child(1).token.to_string()


class PrimaryExpr(ASTList):
    def __init__(self, astlist):
        super(ASTList, self).__init__(astlist)

    def creat(self, astlist):
        return astlist[0] if len(astlist) == 1 else PrimaryExpr(astlist)


class NegtiveExpr(ASTList):
    def __init__(self, astlist):
        super(ASTList, self).__init__(astlist)

    def operand(self):
        return self.child(0)

    def to_string(self):
        return "-" + self.operand()


class BlockStmnt(ASTList):
    def __init__(self, astlist):
        super(ASTList, self).__init__(astlist)


class IfStmnt(ASTList):
    def __init__(self, astlist):
        super(ASTList, self).__init__(astlist)

    def condition(self):
        return self.child(0)

    def then_block(self):
        return self.child(1)

    def else_block(self):
        return self.child(2) if self.num_child() > 2 else None

    def to_string(self):
        return '(if ' + self.condition + ' ' + self.then_block() + ' '\
            + ' else ' + self.else_block() + ' )'


class WhileStmnt(ASTList):
    def __init__(self, astlist):
        super(ASTList, self).__init__(astlist)

    def condition(self):
        return self.child(0)

    def body(self):
        return self.child(1)

    def to_string(self):
        return '(while ' + self.condition() + ' ' + self.body() + ')'


class NoneStmnt(ASTList):
    def __init__(self, astlist):
        super(ASTList, self).__init__(astlist)


class StringLiteral(ASTLeaf):
    def __init__(self, token):
        super(ASTLeaf, self).__init__(token)

    def value(self):
        return self.token.to_string()
