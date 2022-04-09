# -*- coding: utf-8 -*-

import os
import sys
from tokenizer import Tokenizer

ABSPATH = os.path.dirname(__file__)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: %s <text>' % sys.argv[0])
        sys.exit(0)
    text = sys.argv[1].strip()
    if not text:
        print('Usage: %s <text>' % sys.argv[0])
        sys.exit(0)
    try:
        engine = Tokenizer(os.path.join(ABSPATH, 'models',"seggment.kernel"))
        tokens = engine.tokenize(text)
        print(tokens)
    except Exception as e:
        print('Error:', e)