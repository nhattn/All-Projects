# -*- coding: utf-8 -*-

import re
from app import engine
from flask import jsonify, request

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
    tokens = [ token.strip() for token in sentence.split(' ') if token.strip() ]
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
    tokens = [ token.strip() for token in sentence.split(' ') if token.strip() ]
    tagged = [[], []]
    for token in tokens:
        tagged[0].append(token)
        tagged[1].append('N')
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

    if datatype == 'token':
        tokens = [ token.strip() for token in sentence.split(' ') if token.strip() ]
        return jsonify({
            'sentence': sentence,
            'tokenized': tokens
        })
    tokens = [ token.strip() for token in sentence.split(' ') if token.strip() ]
    tagged = [[], []]
    for token in tokens:
        tagged[0].append(token)
        tagged[1].append('N')
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
