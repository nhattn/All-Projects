# -*- coding: utf-8 -*-

from app import db

class Sentence(db.Model):
    __tablename__ = 'sentences'

    id = db.Column(db.Integer, primary_key=True)
    sentence = db.Column(db.String, nullable=False)
    cleaned = db.Column(db.String, nullable=True, default='')
    tokens = db.Column(db.String, nullable=True, default='')
    tagged = db.Column(db.String, nullable=True, default='')

    def __init__(self):
        pass

    def __repr__(self):
        return '<Sentence#{} [{}] />'.format(self.id, self.sentence)
