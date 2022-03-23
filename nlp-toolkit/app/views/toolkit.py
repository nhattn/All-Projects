# -*- coding: utf-8 -*-

import re
from app import engine, db
from ..models.sentence import Sentence
from flask import jsonify, request, abort, render_template
import os
from .tokenizer import Tokenizer
from .tagger import Tagger
from .vtrie import VTrie
from .util import unicode_replace, normalize_text, tokenize, is_word
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
    sentence = unicode_replace(sentence)
    features = vtrie.extract_words(sentence)
    ignore_words = ["ông","bà","anh","chị","em","chú","bác","cô","dì"]
    for i, v in enumerate(features):
        tmp = v.split(' ')
        if tmp[0].lower() in ignore_words:
            v = ' '.join(tmp[1:])
            features[i] = v
    tokens = set([ token for token in features if ' ' in token ])
    tmp = [ word.replace('_',' ') for word in tokenizer.tokenize(sentence).split(' ') if '_' in word ]
    for token in tmp:
        v = token.split(' ')
        if v[0].lower() in ignore_words:
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
    keyword = request.args.get('q',None)
    query = Sentence.query.order_by(Sentence.id.desc())
    if keyword and keyword.strip():
        query = query.filter(Sentence.sentence.ilike('%{}%'.format(keyword.strip().lower())))
    query = query.paginate(1, 10, error_out=False)
    return render_template('home.html',sentences=query.items, keyword=keyword)

@engine.route("/sentence/<int:id>")
def toolkit_infomation(id=0):
    if id <= 0:
        abort(404)
    sent = Sentence.query.get(id)
    if not sent:
        abort(404)
    next_sent = Sentence.query.filter(Sentence.id > sent.id).order_by(Sentence.id.asc()).first()
    prev_sent = Sentence.query.filter(Sentence.id < sent.id).order_by(Sentence.id.desc()).first()
    return render_template('sentence.html', **{
        'sentence':sent.to_json(),
        'next':next_sent.to_json() if next_sent else None,
        'prev':prev_sent.to_json() if prev_sent else None
    })

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
    sentence = unicode_replace(sentence)
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
    if data.get('raw',None):
        return jsonify({
            'sentence': sentence,
            'tokenized': tokenized
        })
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
    sentence = unicode_replace(sentence)
    cleanup = data.get('clean',None)
    if cleanup:
        sentence = sentence + ' '
        sentence = normalize_text(sentence)
        sentence = re.sub(r'\s+',' ', sentence)
    #  Handle tagger sentence and response to client
    kernel = os.path.join(os.path.dirname(__file__),'models', 'tagger.kernel')
    if os.path.isfile(kernel):
        tagger = Tagger(kernel)
        if '_' not in sentence:
            kernel = os.path.join(os.path.dirname(__file__),'models', 'seggment.kernel')
            if os.path.isfile(kernel):
                seggment = Tokenizer(kernel)
                tagged = tagger.postagging(seggment.tokenize(sentence))
            else:
                tagged = tagger.postagging(tokenizer.tokenize(sentence))
        else:
            tagged = tagger.postagging(sentence)
    else:
        if '_' not in sentence:
            tagged = postagger.postagging(tokenizer.tokenize(sentence))
        else:
            tagged = postagger.postagging(sentence)
    if data.get('raw',None):
        tokens = []
        for i, token in enumerate(tagged[0]):
            tag = tagged[1][i]
            if tag == 'F':
                tag = token
            tokens.append(token + '/' + tag)
        tagged = ' '.join(tokens)
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
    sentence = unicode_replace(sentence)
    cleanup = data.get('clean',None)
    datatype = data.get('type','token').strip().lower()
    if datatype not in ['token', 'tagger']:
        datatype = 'token'
    if cleanup:
        sentence = normalize_text(sentence)
        sentence = re.sub(r'\s+',' ', sentence)

    tokenized = toolkit_raw_tokenize(sentence).strip()
    if datatype == 'token':
        if data.get('raw', None):
            return jsonify({
                'sentence': sentence,
                'tokenized': tokenized
            })
        tokens = [ token.strip() for token in tokenized.split(' ') if token.strip() ]
        return jsonify({
            'sentence': sentence,
            'tokenized': tokens
        })
    tokens = [ token.strip() for token in tokenized.split(' ') if token.strip() ]
    tagged = postagger.postagging(tokenized)
    if data.get('raw',None):
        tokens = []
        for i, token in enumerate(tagged[0]):
            tag = tagged[1][i]
            if tag == 'F':
                tag = token
            tokens.append(token + '/' + tag)
        tagged = ' '.join(tokens)
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
    text = unicode_replace(text)
    id_ = data.get('id','').strip()
    if not id_:
        sent = Sentence.query.filter(Sentence.sentence == text).first()
        if bool(sent):
            return jsonify(sent.to_json())
        sent = Sentence()
        sent.sentence = text
        text = normalize_text(text+' ').replace('_',' ').strip()
        tokens = tokenize(text.lower())
        tokens = [ tok for tok in tokens if is_word( tok ) ]
        sent.cleaned = ' '.join(tokens)
        db.session.add(sent)
        try:
            db.session.commit()
            return jsonify(sent.to_json())
        except:
            db.session.rollback()
            return jsonify({
                'error': 'Save failed'
            })
    sent = Sentence.query.get(id_)
    if not sent:
        return jsonify({
            'error': 'Sentence is not exists'
        })
    datatype = data.get('type','token').strip().lower()
    if datatype not in ['token', 'tagger']:
        datatype = 'token'
    if datatype == 'token':
        sent.tokens = text
    else:
        sent.tagged = text
    db.session.add(sent)
    try:
        db.session.commit()
        return jsonify(sent.to_json())
    except:
        db.session.rollback()
        return jsonify(sent.to_json())

@engine.route('/api/sentence/<int:id>', methods=['GET'])
def toolkit_sentence(id=0):
    if id <= 0:
        return jsonify({
            'error': 'Sentence is not exists'
        })
    sent = Sentence.query.get(id)
    if not sent:
        return jsonify({
            'error': 'Sentence is not exists'
        })
    return jsonify(sent.to_json())

@engine.route('/api/neighbor', methods=['GET'])
def toolkit_neighbor():
    id = request.args.get('id', -1)
    next_sent = Sentence.query.filter(Sentence.id > id).order_by(Sentence.id.asc()).first()
    prev_sent = Sentence.query.filter(Sentence.id < id).order_by(Sentence.id.desc()).first()
    return jsonify({
        'next' : next_sent.to_json() if next_sent else None,
        'prev' : prev_sent.to_json() if prev_sent else None
    })

@engine.route('/api/vocab', methods=['POST'])
def toolkit_vocab():
    if request.content_type and "application/json" in request.content_type:
        data = request.get_json()
    else:
        data = request.form
    vocab = data.get('vocab', '').replace('_',' ').strip()
    if not vocab:
        return jsonify({
            'error':'Invalid data'
        })
    vocab = unicode_replace(vocab)
    if ' ' not in vocab:
        return jsonify({
            'error':'Vocabulary is not 2 or 3 gram'
        })
    vocabs = set()
    with open(os.path.join(os.path.dirname(__file__), 'models', 'vocab.txt'), 'r', encoding='utf-8') as fin:
        word = fin.read().strip()
        if word and word not in vocabs:
            vocabs.add(word)
    total = len(vocabs)
    vocab = vocab.lower()
    if vocab not in vocabs:
        total = total + 1
        with open(os.path.join(os.path.dirname(__file__), 'models', 'vocab.txt'), 'a', encoding='utf-8') as fout:
            fout.write(vocab + "\n")
        tmp = vocab.split(' ')
        if len(tmp) == 2:
            tokenizer.bi_grams.add(vocab)
        elif len(tmp) == 3:
            tokenizer.tri_grams.add(vocab)
    return jsonify({
        'vocabs': total,
        'vocab' : vocab
    })
