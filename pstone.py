#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   RobertDing
#   E-mail  :   robertdingx@gmail.com
#   Date    :   15/04/26 16:41:03
#   Desc    :   两周自制脚本语言 python 实现版本
#
from __future__ import absolute_import, division, with_statement

import re


class StoneException(BaseException):

    def __init__(self, message=""):
        super(StoneException, self).__init__()


class ParseException(BaseException):

    def __init__(self, token):
        super(ParseException, self).__init__()


class Token(object):
    EOF = object()

    def __init__(self, lineno):
        self.line_number = lineno

    def is_identifier(self):
        raise NotImplementedError()

    def is_number(self):
        raise NotImplementedError()

    def is_string(self):
        raise NotImplementedError()

    def to_string(self):
        raise NotImplementedError()


class NumToken(Token):

    def __init__(self, lineno, num):
        super(NumToken, self).__init__(lineno)
        self.num = num

    def is_number(self):
        return True

    def to_string(self):
        return str(self.num)


class IdToken(Token):

    def __init__(self, lineno, identify):
        super(IdToken, self).__init__(lineno)
        self.identify = identify

    def is_identifier(self):
        return True

    def to_string(self):
        if self.identify == self.EOF:
            return '\n'
        return self.identify


class StrToken(Token):

    def __init__(self, lineno, string):
        super(StrToken, self).__init__(lineno)
        self.string = string

    def is_string(self):
        return True

    def to_string(self):
        return self.string


class Lexer(object):
    regex_pat = r"\s*((#.*)|(\d+)|(\"(\\\"|\\\\|\\n|[^\"])*\")|([A-Z_a-z]\w*|==|<=|>=|&&|\|\||[^\w\s]?))?"
    matcher = re.compile(regex_pat)

    def __init__(self, reader):
        self.has_more = True
        self.reader = reader
        self.queue = []
        self.cur_line_no = 0

    def read(self):
        if self.fill_queue(0):
            return self.queue.pop(0)
        else:
            return Token.EOF

    def peek(self, i):
        if self.fill_queue(i):
            return self.pop(i)
        else:
            return False

    def fill_queue(self, i):
        while i >= len(self.queue):
            if self.has_more:
                self.readline()
            else:
                return False
        return True

    def readline(self):
        line = self.reader.readline()
        if not line:
            self.has_more = False
            return
        self.cur_line_no += 1
        pos = 0
        end_pos = len(line)
        while pos < end_pos:
            res = self.matcher.match(line, pos, end_pos)
            if res:
                self.add_token(self.cur_line_no, res)
                pos = res.end()
            else:
                raise ParseException
        # self.queue.append(IdToken(self.cur_line_no, Token.EOF))

    def add_token(self, lineno, matcher):
        """
        group 的排列顺序
        匹配到得字符串  注释 数字 匹配到的字符串 字符串 操作符
        """
        matched = matcher.group(1)
        if matched is not None:
            if matcher.group(2) is None:
                if matcher.group(3) is not None:
                    token = NumToken(lineno, int(matched))
                elif matcher.group(4) is not None:
                    token = StrToken(lineno, self.to_string_literal(matched))
                else:
                    token = IdToken(lineno, matched)
                self.queue.append(token)

    def to_string_literal(self, string):
        splash = False
        tostring = ''
        for i, c in enumerate(string):
            if c == '\\':
                splash = True
                continue
            if splash and c == 'n':
                c = '\n'
            splash = False
            tostring += c
        return tostring


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
