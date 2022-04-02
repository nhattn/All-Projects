# -*- coding: utf-8 -*-

from app import engine

@engine.template_filter("word_break")
def the_word_break(s, length=72):
    if len(s) <= length:
        return s
    _length = len(s)
    words = s.split(' ')
    s = ''
    for word in words:
        word = word.strip()
        if not word:
            continue
        s += word + " "
        if len(s.strip()) >= length:
            if len(s) < _length:
                return s.strip() + "..."
    return s
