# -*- coding: utf-8 -*-

import os
import sys
import pickle
from sklearn_crfsuite import metrics
from tokenizer import Tokenizer, TOKEN_LABELS

ABSPATH = os.path.dirname(__file__)

if __name__ == "__main__":
    train_data = []
    sentence = []
    with open(os.path.join(ABSPATH, 'dataset', 'gold-POS-tags-train.conll'),'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                train_data.append(" ".join(sentence))
                sentence = []
                continue
            word = line.split('\t')[0]
            sentence.append(word)

    with open(os.path.join(ABSPATH, 'dataset', 'gold-POS-tags-test.conll'),'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                train_data.append(" ".join(sentence))
                sentence = []
                continue
            word = line.split('\t')[0]
            sentence.append(word)

    rs, X_test, y_test = Tokenizer.train(train_data)
    if rs:
        print('best params:', rs.best_params_)
        print('best CV score:', rs.best_score_)
        with open(os.path.join(ABSPATH, 'models',"seggment.kernel"), 'wb') as fout:
            pickle.dump(rs.best_estimator_, fout)
        y_pred = rs.predict(X_test)
        metrics.flat_f1_score(y_test, y_pred, average='weighted', labels=TOKEN_LABELS)
        print(metrics.flat_classification_report(
            y_test, y_pred, labels=TOKEN_LABELS, digits=3
        ))