# -*- coding: utf-8 -*-

from ..models.sentence import Sentence

def init_database(db):
    db.drop_all()
    db.create_all()
