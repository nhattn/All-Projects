# -*- coding: utf-8 -*-

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

engine = Flask(__name__)

ABSPATH = os.path.dirname(os.path.dirname(__file__))
DATAPATH = os.path.join(ABSPATH,"database")

engine.config["JSON_AS_ASCII"] = False
engine.config["JSONIFY_PRETTYPRINT_REGULAR"] = False
engine.config["DEBUG"] = True
engine.config["ENV"] = "production"
engine.config["PORT"] = 7500
engine.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///{}".format(os.path.join(DATAPATH, "openai.db"))
engine.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
engine.config["SQLALCHEMY_ECHO"] = False

db = SQLAlchemy(engine,session_options={
    "autoflush": False
})

from .views import *
