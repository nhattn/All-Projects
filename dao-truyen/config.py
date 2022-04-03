# -*- coding: utf-8 -*-

import os
import sys

ABSPATH = os.path.dirname(__file__)
BOOK_DIRECTORY = os.path.join(ABSPATH, 'books')
EPUB_DIRECTORY = os.path.join(ABSPATH, 'epub')

if not os.path.isdir(BOOK_DIRECTORY):
    print('Create directory "%s" ...' % BOOK_DIRECTORY)
    try:
        os.makedirs(BOOK_DIRECTORY, exist_ok=True)
    except Exception as e:
        print(str(e))
        sys.exit(0)

if not os.path.isdir(EPUB_DIRECTORY):
    print('Create directory "%s" ...' % EPUB_DIRECTORY)
    try:
        os.makedirs(EPUB_DIRECTORY, exist_ok=True)
    except Exception as e:
        print(str(e))
        sys.exit(0)
