#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import pickle
from vinlp import word_tokenize
from vinlp import is_token

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: %s <model> <filename>' % sys.argv[0])
        sys.exit(1)

    model_path = sys.argv[1].strip()
    if not os.path.isfile(model_path):
        print('kernel is not found')
        sys.exit(1)

    filepath = sys.argv[2].strip()
    if not os.path.isfile(filepath):
        print('File not exitsts')
        sys.exit(1)

    try:

        kernel, encoder, stopword = pickle.load(open(model_path, 'rb'))

        lines = []
        fin = open(filepath, 'r', encoding='utf-8', errors='ignore')

        for line in fin:
            line = line.strip()
            if not line:
                continue
            tokens = word_tokenize(line).split(' ')
            tokens = [token for token in tokens if token not in stopword]
            tokens = [token for token in tokens if is_token(token)]
            if len(tokens) == 0:
                continue
            lines.append(" ".join(tokens).strip())

        fin.close()
    
        if len(lines) == 0:
            print('No data to testing')
            sys.exit(1)
    
        text = " ".join(lines).strip()
        label = kernel.predict([text])
        print('Predict label:', encoder.inverse_transform(label)
    
    except Exception as e:
        print('Error', e)
        sys.exit(1)

    sys.exit(0)
