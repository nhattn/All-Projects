# -*- coding: utf-8 -*-

from app import engine
from flask import jsonify, request

@engine.errorhandler(404)
def not_found(err):
    if request.path.startswith('/api'):
        return jsonify({
            'error':'Not Found'
        })
    return "404 Not Found", 404

@engine.errorhandler(400)
def bad_request(err):
    if request.path.startswith('/api'):
        return jsonify({
            'error':'Bad Request'
        })
    return "400 Bad Requested", 400

@engine.errorhandler(500)
def server_error(err):
    if request.path.startswith('/api'):
        return jsonify({
            'error':'Internal Server Error'
        })
    return "500 Internal Server Error", 500

@engine.errorhandler(405)
def not_allowed(err):
    if request.path.startswith('/api'):
        return jsonify({
            'error':'Method Not Allowed'
        })
    return "405 Method Not Allowed", 405

@engine.errorhandler(403)
def forbidden(err):
    if request.path.startswith('/api'):
        return jsonify({
            'error':'Forbidden'
        })
    return "403 Forbidden", 403
