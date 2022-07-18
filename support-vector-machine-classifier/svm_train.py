#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import string
import pickle
import random
import time
import numpy as np
from vinlp import word_tokenize
from vinlp import is_token
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: %s <filename>' % sys.argv[0])
        sys.exit(1)

    filepath = sys.argv[1].strip()
    if not os.path.isfile(filepath):
        print('File not exitsts')
        sys.exit(1)

    try:

        count = {}
        vocab = {}
        label_vocab = {}
        
        fin = open(filepath,'r', encoding='utf-8',errors='ignore')
        lines = []
        
        for line in fin:
            line = line.strip()
            if not line:
                continue
            words = [word for word in line.split(' ') if word.strip()]
            key = words[0]
            words = word_tokenize(" ".join(words[1:])).split(' ')
            lines.append([key, words])
            count[key] = count.get(key, 0) + 1
            if key not in label_vocab:
                label_vocab[key] = {}
            for word in words:
                if word in string.punctuation:
                    continue
                label_vocab[key][word] = label_vocab[key].get(word, 0) + 1
                if word not in vocab:
                    vocab[word] = set()
                vocab[word].add(key)
        
        fin.close()

        for key in count:
            print(key, count[key])

        total_label = len(count)
        words_count = {}
        for word in vocab:
            if len(list(vocab[word])) == total_label:
                words_count[word] = min([label_vocab[x][word] for x in label_vocab])
        
        sorted_count = sorted(words_count, key=words_count.get, reverse=True)

        stopword = set()
        for word in sorted_count:
            if words_count[word] < 500:
                continue
            print(word, words_count[word])
            stopword.add(word)

        for ch in string.punctuation:
          stopword.add(ch)

        stopword.add('..')
        stopword.add('...')
        stopword.add('....')

        test_percent = 0.2
        min_doc = count[min(count,key=count.get)]
        
        all_doc = {}
        
        text = []
        label = []

        for it in lines:
            it[1] = [word for word in it[1] if word not in stopword]
            if it[0] not in all_doc:
                all_doc[it[0]] = []
            all_doc[it[0]].append(' '.join(it[1]))

        del lines
        for key in all_doc:
            alist = all_doc[key]
            random.shuffle(alist)
            for val in alist[:min_doc]:
                tokens = [token for token in val.split(' ') if is_token(token)]
                if len(tokens) == 0:
                    continue
                label.append(key)
                text.append(" ".join(tokens))

        X_train, X_test, y_train, y_test = train_test_split(text, label, test_size=test_percent, random_state=42)

        label_encoder = LabelEncoder()
        label_encoder.fit(y_train)
        print(list(label_encoder.classes_), '\n')
        y_train = label_encoder.transform(y_train)
        y_test = label_encoder.transform(y_test)

        MODEL_PATH = "models"
        if not os.path.exists(MODEL_PATH):
            os.makedirs(MODEL_PATH)

        start_time = time.time()
        text_clf = Pipeline([
            ('vect', CountVectorizer(ngram_range=(1,1), max_df=0.8, max_features=None)),
            ('tfidf', TfidfTransformer()),
            ('clf', SVC(gamma='scale'))
        ])
        
        text_clf = text_clf.fit(X_train, y_train)
        train_time = time.time() - start_time
        print('Done training SVM in', train_time, 'seconds.')
        model_name = os.path.basename(filepath).split('.')[0]
        pickle.dump((text_clf, label_encoder, stopword), open(os.path.join(MODEL_PATH, "%s.pkl" % model_name), 'wb'))

        y_pred = text_clf.predict(X_test)
        print('SVM, Accuracy =', np.mean(y_pred == y_test))
        y_pred = text_clf.predict(X_test)
        print(classification_report(y_test, y_pred, target_names=list(label_encoder.classes_)))

    except Exception as e:
       print('Error', e)
       sys.exit(1)

    sys.exit(0)
