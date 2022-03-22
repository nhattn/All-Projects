# -*- coding: utf-8 -*-

import re
from app import engine
from flask import jsonify, request
import os
from .tokenizer import Tokenizer
from .tagger import Tagger
from .vtrie import VTrie
import string

vtrie = VTrie()

try:
    with open(os.path.join(os.path.dirname(__file__), 'models', 'vocab.txt'), 'r', encoding='utf-8') as fin:
        word = fin.read().strip()
        if word:
            vtrie.add_word(word)
except:
    pass

tokenizer = Tokenizer(os.path.join(os.path.dirname(__file__), 'models', 'seggment-base.kernel'))
postagger = Tagger(os.path.join(os.path.dirname(__file__), 'models', 'tagger-base.kernel'))

def toolkit_raw_tokenize(sentence):
    features = vtrie.extract_words(sentence)
    for i, v in enumerate(features):
        tmp = v.split(' ')
        if tmp[0].lower() in ["ông","bà","anh","chị","em"]:
            v = ' '.join(tmp[1:])
            features[i] = v
    tokens = set([ token for token in features if ' ' in token ])
    tmp = [ word.replace('_',' ') for word in tokenizer.tokenize(sentence).split(' ') if '_' in word ]
    for token in tmp:
        v = token.split(' ')
        if v[0].lower() in ["ông","bà","anh","chị","em"]:
            token = ' '.join(v[1:])
        if token not in tokens:
            tokens.add(token)
    tokens = sorted(tokens,key=len, reverse=True)
    for token in tokens:
        sentence = sentence.replace(token, token.replace(' ','_'))
    for ch in string.punctuation:
        if ch == ' ' or ch == '_':
            continue
        sentence = sentence.replace(ch, ' '+ch+' ')
    sentence = re.sub(r'\s+',' ',sentence)
    return sentence

@engine.route("/")
def toolkit_homepage():
    return 'Hi there'

@engine.route('/api/tokenize', methods=['POST'])
def toolkit_tokenize():
    if request.content_type and "application/json" in request.content_type:
        data = request.get_json()
    else:
        data = request.form
    sentence = data.get('text', '').strip()
    if not sentence:
        return jsonify({
            'error':'Invalid data'
        })
    cleanup = data.get('clean',None)
    if cleanup:
        sentence = sentence.replace('_', ' ')
        sentence = sentence.replace('/B_W', ' ')
        sentence = sentence.replace('/I_W', ' ')
        sentence = re.sub(r'\s+',' ', sentence)
    #  Handle tokenizer sentence and response to client
    kernel = os.path.join(os.path.dirname(__file__),'models', 'seggment.kernel')
    if os.path.isfile(kernel):
        seggment = Tokenizer(kernel)
        tokenized = seggment.tokenize(sentence)
    else:
        tokenized = tokenizer.tokenize(sentence)
    tokens = [ token.strip() for token in tokenized.split(' ') if token.strip() ]
    return jsonify({
        'sentence': sentence,
        'tokenized': tokens
    })

@engine.route('/api/tagger', methods=['POST'])
def toolkit_tagger():
    if request.content_type and "application/json" in request.content_type:
        data = request.get_json()
    else:
        data = request.form
    sentence = data.get('text', '').strip()
    if not sentence:
        return jsonify({
            'error':'Invalid data'
        })
    cleanup = data.get('clean',None)
    if cleanup:
        sentence = sentence + ' '
        sentence = re.sub(r'/[A-Z]\s+',' ', sentence)
        sentence = re.sub(r'/[A-Z][a-z]\s+',' ', sentence)
        sentence = re.sub(r'\s+',' ', sentence)
    #  Handle tagger sentence and response to client
    kernel = os.path.join(os.path.dirname(__file__),'models', 'tagger.kernel')
    if os.path.isfile(kernel):
        tagger = Tagger(kernel)
        kernel = os.path.join(os.path.dirname(__file__),'models', 'seggment.kernel')
        if os.path.isfile(kernel):
            seggment = Tokenizer(kernel)
            tagged = tagger.postagging(seggment.tokenize(sentence))
        else:
            tagged = tagger.postagging(tokenizer.tokenize(sentence))
    else:
        tagged = postagger.postagging(tokenizer.tokenize(sentence))
    return jsonify({
        'sentence': sentence,
        'tagged': tagged
    })

@engine.route('/api/predict', methods=['POST'])
def toolkit_predict():
    if request.content_type and "application/json" in request.content_type:
        data = request.get_json()
    else:
        data = request.form
    sentence = data.get('text', '').strip()
    if not sentence:
        return jsonify({
            'error':'Invalid data'
        })
    cleanup = data.get('clean',None)
    datatype = data.get('type','token').strip().lower()
    if datatype not in ['token', 'tagger']:
        datatype = 'token'
    if cleanup:
        if datatype == 'token':
            sentence = sentence.replace('_', ' ')
            sentence = sentence.replace('/B_W', ' ')
            sentence = sentence.replace('/I_W', ' ')
        else:
            sentence = sentence + ' '
            sentence = re.sub(r'/[A-Z]\s+',' ', sentence)
            sentence = re.sub(r'/[A-Z][a-z]\s+',' ', sentence)
        sentence = re.sub(r'\s+',' ', sentence)

    tokenized = toolkit_raw_tokenize(sentence).strip()
    if datatype == 'token':
        tokens = [ token.strip() for token in tokenized.split(' ') if token.strip() ]
        return jsonify({
            'sentence': sentence,
            'tokenized': tokens
        })
    tokens = [ token.strip() for token in tokenized.split(' ') if token.strip() ]
    tagged = postagger.postagging(tokenized)
    return jsonify({
        'sentence': sentence,
        'tagged': tagged
    })

@engine.route('/api/save', methods=['POST'])
def toolkit_save():
    if request.content_type and "application/json" in request.content_type:
        data = request.get_json()
    else:
        data = request.form
    text = data.get('text', '').strip()
    if not text:
        return jsonify({
            'error':'Invalid data'
        })
    datatype = data.get('type','token').strip().lower()
    if datatype not in ['token', 'tagger']:
        datatype = 'token'
    if datatype == 'token':
        return jsonify({
            'tokenized':text
        })
    return jsonify({
        'tagged' : text
    })
