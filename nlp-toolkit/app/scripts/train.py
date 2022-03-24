# -*- coding: utf-8 -*-

import os
import sys
import sqlite3
from app import DATAPATH, ABSPATH
from ..views.tokenizer import Tokenizer
from ..views.tagger import Tagger

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
        rs, x_test, y_test = Tokenizer.train(train_data)
        if rs:
            print('best params:', rs.best_params_)
            print('best CV score:', rs.best_score_)
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
        rs, x_test, y_test = Tagger.train(train_data)
        if rs:
            print('best params:', rs.best_params_)
            print('best CV score:', rs.best_score_)
    except Exception as e:
        print(e)
        sys.exit(0)
