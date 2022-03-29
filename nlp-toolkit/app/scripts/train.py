# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
import pickle
from app import DATAPATH, ABSPATH
from ..views.tokenizer import Tokenizer, TOKEN_LABELS
from ..views.tagger import Tagger, TAGS
from sklearn_crfsuite import metrics

def train_seggment():
    try:
        db = sqlite3.connect(os.path.join(DATAPATH,"openai.db"))
        cur = db.cursor()
        qry = cur.execute("SELECT tokens FROM sentences").fetchall()
        train_data = []
        for row in qry:
            if row[0]:
                train_data.append(row[0])
        cur.close()
        db.close()
        rs, X_test, y_test = Tokenizer.train(train_data)
        if rs:
            print('best params:', rs.best_params_)
            print('best CV score:', rs.best_score_)
            with open(os.path.join(ABSPATH, 'app','views','models',"seggment.kernel"), 'wb') as fout:
                pickle.dump(rs.best_estimator_, fout)
            y_pred = rs.predict(X_test)
            metrics.flat_f1_score(y_test, y_pred, average='weighted', labels=TOKEN_LABELS)
            print(metrics.flat_classification_report(
                y_test, y_pred, labels=TOKEN_LABELS, digits=3
            ))
    except Exception as e:
        print(e)
        sys.exit(0)

def train_tagger():
    try:
        db = sqlite3.connect(os.path.join(DATAPATH,"openai.db"))
        cur = db.cursor()
        qry = cur.execute("SELECT tagged FROM sentences").fetchall()
        train_data = []
        for row in qry:
            if row[0]:
                train_data.append(row[0])
        cur.close()
        db.close()
        rs, X_test, y_test = Tagger.train(train_data)
        if rs:
            print('best params:', rs.best_params_)
            print('best CV score:', rs.best_score_)
            with open(os.path.join(ABSPATH, 'app','views','models',"tagger.kernel"), 'wb') as fout:
                pickle.dump(rs.best_estimator_, fout)
            y_pred = rs.predict(X_test)
            metrics.flat_f1_score(y_test, y_pred, average='weighted', labels=TAGS)
            print(metrics.flat_classification_report(
                y_test, y_pred, labels=TAGS, digits=3
            ))
    except Exception as e:
        print(e)
        sys.exit(0)
