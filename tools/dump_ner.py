#!/usr/bin/env python3

import pickle
import re
import sys
from pyvi import ViTokenizer, ViPosTagger

def repl_name(m):
    return ' [name %s.] ' % m.group(1)

def repl_back(m):
    return '%s' % m.group(1)

def repl_special(m):
    return '%s. ' % m.group(1)

patterns = "\s+(([A-Z])\.([A-Z])\.([A-Z])\.([A-Z])|([A-Z])\.([A-Z])\.([A-Z])|([A-Z])\.([A-Z])|([A-Z]))\.[\s$]"

with open('tmp/data.pkl','rb') as fin:
    data = pickle.load(fin)

sentences = set()
tokx = ViTokenizer
tagx = ViPosTagger

for i, row in enumerate(data):
    content = re.sub(patterns, repl_name, row,re.DOTALL)
    for line in content.split('\n'):
        line = line.strip()
        if not line or len(line) == 1:
            continue
        if line[-1:] != '.':
            line += '[END_PARAGRAPH]'
        line = re.sub(r'([\!\?])\s+',repl_special, line, re.DOTALL)
        sents = [ re.sub(r'\[name (.*?)\]',repl_back,sent.strip()+'.') for sent in re.split(r'\.\s+', line) if sent.strip() ]
        for sent in sents:
            if sent[-2:] == '..':
                sent = sent[:-1]
            sent = sent.strip()
            sent = sent.replace('[END_PARAGRAPH].','')
            sent = re.sub(r'([\!\?])\.', repl_special, sent, re.DOTALL)
            if not sent or len(sent) <= 2:
                continue
            if sent not in sentences:
                sentences.add(sent)
    #print(content)

fout = open('tmp/ner.txt','w', encoding='utf-8')
trans = {'P': 'B-NP', 'Nc': 'B-NP', 'N': 'I-NP', 'Np': 'I-NP', 'M': 'B-NP', 'L': 'B-NP', 'Ny': 'B-NP', 'Ns': 'B-NP', 'NNPY': 'B-NP', 'Nu': 'B-NP', 'Nb': 'B-NPb', 'V': 'B-VP', 'A': 'B-AP', 'E': 'B-PP', 'F': 'O', 'R': 'O', 'C': 'O', 'T': 'O'}
for sent in sentences:
    print(sent)
    pos_tag = tagx.postagging(tokx.tokenize(sent))
    last_b = ''
    for i, tok in enumerate(pos_tag[0]):
        t_tag = 'O'
        if pos_tag[1][i] in trans:
            t_tag = trans[pos_tag[1][i]]
        if pos_tag[1][i] == 'Np':
            if i - 1 >= 0 and pos_tag[1][i - 1] == 'N':
                t_tag = 'I-NP'
        n_tag = 'O'
        if pos_tag[1][i] == 'Np':
            if i - 1 >= 0 and pos_tag[1][i - 1] == 'Np':
                n_tag = 'I-PER'
            else:
                n_tag = 'B-PER'
        if t_tag == 'I-NP' and n_tag == 'B-PER':
            n_tag = 'I-PER'
        if last_b == '' or last_b == 'O':
            if n_tag == 'I-PER':
                n_tag = 'B-PER'
        fout.write("%s\t%s\t%s\t%s\n" % (tok, pos_tag[1][i], t_tag,n_tag))
    fout.write("\n")
fout.close()
