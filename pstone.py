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
        return str(self.identify)


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
                pos = res.endpos
            else:
                raise ParseException
        self.queue.append(IdToken(self.cur_line_no, Token.EOF))

    def add_token(self, lineno, matcher):
        """
        group 的排列顺序
        匹配到得字符串  空字符 数字 匹配到的字符串 字符串 操作符
        """
        matched = matcher.group(0)
        if matched is not None:
            if matcher.group(1) is None:
                if matcher.group(2) is not None:
                    token = NumToken(lineno, int(matched))
                elif matcher.group(3) is not None:
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
