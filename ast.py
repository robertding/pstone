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


def ASTLeaf(ASTree):
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


def ASTList(ASTree):
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


def NumLiteral(ASTLeaf):
    def __init__(self, token):
        super(ASTLeaf, self).__init__(token)

    def value(self):
        return self.token.num


def Name(ASTLeaf):
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
