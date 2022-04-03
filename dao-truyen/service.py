#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import signal
import json
import os
import re
from websocket import WebSocketServer, WebSocket
import config
from util import *

class StoryGate(WebSocket):
    def handle(self):
        msg = self.data.strip()
        if not msg:
            self.send_message(jsonify({"error":"Invalid data"}))
            return
        ch = msg[0].lower()
        if ch not in ["s","c"]:
            self.send_message(jsonify({"error":"Invalid data"}))
            return
        data = msg[1:].strip()
        if data[0] != '{' or data[-1:] != '}':
            self.send_message(jsonify({"error":"Invalid data"}))
            return
        try:
            recived = json.loads(data)
        except:
            self.send_message(jsonify({"error":"Invalid data"}))
            return
        try:
            if ch == "s":
                if "name" not in recived and 'story' not in recived:
                    self.send_message(jsonify({"error":"Invalid data"}))
                    return
                if 'story' in recived:
                    story = recived['story']
                    if not os.path.isdir(os.path.join(config.BOOK_DIRECTORY, story)):
                        self.send_message(jsonify({"error":"Story \"%s\" is not found" % story}))
                        return
                    metadata_file = os.path.join(config.BOOK_DIRECTORY, story,'metadata.json')
                    metadata = read_metadata(metadata_file)
                    if not metadata:
                        self.send_message(jsonify({"error":"Story \"%s\" could not load metadata" % story}))
                        return
                    if 'cover' in recived:
                        if '://' not in recived['cover']:
                            self.send_message(jsonify({"name":story,"error":"Cover \"%s\" is not valid" % recived['cover']}))
                            return
                        extention = recived['cover'].split('?')[0]
                        extention = extention.split('.')[-1:][0].lower()
                        cover_file = "cover.%s" % extention
                        cover_file = download_cover(recived['cover'], story, cover_file)
                        if cover_file.strip():
                            metadata['cover'] = cover_file
                            if save_metadata(metadata_file ,metadata):
                                self.send_message(jsonify({"name":story,"message":"Update cover to \"%s\" successfully" % cover_file}))
                                return
                        self.send_message(jsonify({"name":story,"message":"Cover \"%s\" is valid" % recived['cover']}))
                    elif 'author' in recived:
                        author = unicode_replace(recived['author']).strip()
                        if not author:
                            self.send_message(jsonify({"error":"Author is empty"}))
                            return
                        metadata['metadata']['dc:creator'] = author
                        metadata['metadata']['dc:publisher'] = author
                        metadata['metadata']['dc:description'] = "%s của %s" % (metadata['metadata']['dc:description'], author)                    
                        if save_metadata(metadata_file ,metadata):
                            self.send_message(jsonify({"name":story,"message":"Update author \"%s\" successfully" % author}))
                            return
                        self.send_message(jsonify({"name":story,"message":"Update author \"%s\" unsuccess" % author}))
                        return
                    elif 'categories' in recived:
                        categories = recived['categories']
                        if not isinstance(categories, list):
                            self.send_message(jsonify({"name":story,"message":"Categories is not valid"}))
                            return
                        metadata['metadata']['dc:description'] = "%s, thể loại: %s" % (metadata['metadata']['dc:description'], unicode_replace(', '.join(categories)))
                        if save_metadata(metadata_file % story ,metadata):
                            self.send_message(jsonify({"name":story,"message":"Update categoryies \"%s\" successfully" % unicode_replace(', '.join(categories))}))
                            return
                        self.send_message(jsonify({"name":story,"message":"Update categories \"%s\" unsuccess" % unicode_replace(', '.join(categories))}))
                        return
                    elif 'intro' in recived:
                        intro = unicode_replace(recived['intro']).strip()
                        action = intro[0:2]
                        intro = intro[2:]
                        intro_file = os.path.join(config.BOOK_DIRECTORY, story, 'intro.md')
                        if action == "b:":
                            with open(intro_file, 'w', encoding='utf-8') as fout:
                                fout.write(intro+"\n")
                            self.send_message(jsonify({"name":story,"message":"Create introduction file"}))
                            return
                        else:
                            with open(intro_file, 'a', encoding='utf-8') as fout:
                                if intro == 'newline':
                                    fout.write("\n")
                                else:
                                    fout.write(intro+"\n")
                            self.send_message(jsonify({"name":story,"message":"Append text introduction file"}))
                            if action == "c:":
                                if "intro.md" in metadata['chapters']:
                                    self.send_message(jsonify({"name":story,"message":"Add introduction successfully"}))
                                    return
                                metadata['chapters'].append("intro.md")
                                if save_metadata(metadata_file ,metadata):
                                    self.send_message(jsonify({"name":story,"message":"Add introduction successfully"}))
                                    return
                                self.send_message(json({"name":story,"message":"Add introduction successfully but not save metadata"}))
                        return
                    self.send_message(jsonify({"message":"hi there"}))
                    return

                name = story2folder(recived['name'])
                book_path = os.path.join(config.BOOK_DIRECTORY, name)
                try:
                    os.makedirs(book_path, exist_ok=True)
                except:
                    self.send_message(jsonify({"error":"Could not create story \"%s\"" % name}))
                    return
                if not os.path.isdir(book_path):
                    self.send_message(jsonify({"error":"Story \"%s\" not found" % name}))
                    return
                metadata_file = os.path.join(book_path, 'metadata.json')
                if not os.path.isfile(metadata_file):
                    metadata = {
                        "metadata" : {
                            "dc:title":unicode_replace(recived['name']),
                            "dc:creator":"",
                            "dc:language":"vi",
                            "dc:identifier":epub_uuid(),
                            "dc:source":"",
                            "meta":"",
                            "dc:date":"",
                            "dc:publisher":"",
                            "dc:contributor":"",
                            "dc:rights":"",
                            "dc:description":'Tác phẩm: %s' % unicode_replace(recived['name']),
                            "dc:subject":unicode_replace(recived['name'])
                        },
                        "cover": '',
                        "chapters":[]
                    }
                    if save_metadata(metadata_file ,metadata):
                        self.send_message(jsonify({"name":name}))
                        return
                    self.send_message(jsonify({"error":"Could not create story \"%s\"" % name}))
                else:
                    if read_metadata(metadata_file):
                        self.send_message(jsonify({"name":name}))
                        return
                    self.send_message(jsonify({"error":"Story \"%s\" valid" % name}))
            elif ch == "c":
                if "story" not in recived:
                    self.send_message(jsonify({"error":"Invalid data"}))
                    return
                story = recived['story']
                book_path = os.path.join(config.BOOK_DIRECTORY, story)
                if not os.path.isdir(book_path):
                    self.send_message(jsonify({"error":"Story \"%s\" is not found" % story}))
                    return
                metadata_file = os.path.join(book_path, 'metadata.json')
                metadata = read_metadata(metadata_file)
                if not metadata:
                    self.send_message(jsonify({"error":"Story \"%s\" could not load metadata" % story}))
                    return
                if 'content' not in recived:
                    self.send_message(jsonify({"name":story,"message":"Story \"%s\" no content" % story}))
                    return
                if 'chapter' not in recived or not recived['chapter'].strip().isdigit():
                    self.send_message(jsonify({"name":story,"message":"Story \"%s\" could not find chapter" % story}))
                    return
                chapter = recived['chapter'].strip()
                content = unicode_replace(recived['content']).strip()
                action = content[0:2]
                content = content[2:]
                chapter_filename = os.path.join(book_path, "chapter-%s.md" % chapter)
                if action == "b:":
                    with open(chapter_filename, 'w', encoding='utf-8') as fout:
                        fout.write(content+"\n")
                    self.send_message(jsonify({"name":story,"message":"Create \"chapter-%s.md\" file" % chapter}))
                    return
                else:
                    with open(chapter_filename, 'a', encoding='utf-8') as fout:
                        if content == 'newline':
                            fout.write("\n")
                        else:
                            fout.write(content+"\n")
                    self.send_message(jsonify({"name":story,"message":"Append text \"chapter-%s.md\" file" % chapter}))
                    if action == "c:":
                        filename = "chapter-%s.md" % chapter
                        if filename in metadata['chapters']:
                            self.send_message(jsonify({"name":story,"message":"Add content successfully"}))
                            return
                        metadata['chapters'].append(filename)
                        if save_metadata(metadata_file ,metadata):
                            self.send_message(jsonify({"name":story,"message":"Add content successfully"}))
                            return
                        self.send_message(jsonify({"name":story,"message":"Add content successfully but not save metadata"}))
                    return
        except Exception as e:
            self.send_message(jsonify({"error":str(e)}))
    def connected(self):
        print(self.address, 'connected')
    def handle_close(self):
        print(self.address, 'closed')

if __name__ == "__main__":
    print("Start server at http://127.0.0.1:9876\nHit Ctrl + C to stop application")
    server = WebSocketServer("", 9876, StoryGate)
    def signal_handler(signal, frame):
        print("Caught Ctrl+C, shutting down...")
        server.running = False
        sys.exit()
    signal.signal(signal.SIGINT, signal_handler)
    server.serve_forever()
