# -*- coding: utf-8 -*-

from app import engine
from flask import jsonify, request, render_template

@engine.errorhandler(404)
def not_found(err):
    if request.path.startswith('/api'):
        return jsonify({
            'error':'Not Found'
        })
    return render_template('error.html'), 404

@engine.errorhandler(400)
def bad_request(err):
    if request.path.startswith('/api'):
        return jsonify({
            'error':'Bad Request'
        })
    return render_template('error.html'), 400

@engine.errorhandler(500)
def server_error(err):
    if request.path.startswith('/api'):
        return jsonify({
            'error':'Internal Server Error'
        })
    return render_template('error.html'), 500

@engine.errorhandler(405)
def not_allowed(err):
    if request.path.startswith('/api'):
        return jsonify({
            'error':'Method Not Allowed'
        })
    return render_template('error.html'), 405

@engine.errorhandler(403)
def forbidden(err):
    if request.path.startswith('/api'):
        return jsonify({
            'error':'Forbidden'
        })
    return render_template('error.html'), 403
