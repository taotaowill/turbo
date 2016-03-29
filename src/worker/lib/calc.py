# encoding: utf-8
"""
@file turbo lib for calc
@author wanghaitao01
@date 2016/03/29
"""
import turbo


@turbo.service(version="0.0.1")
def add(a, b):
    """Add method"""
    return a + b


@turbo.service(version="0.0.1")
def sub(a, b):
    """Sub method"""
    return a - b
