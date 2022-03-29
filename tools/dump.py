#!/usr/bin/env python3

import re
import sqlite3
import pickle

def clean_text(text):
    text = re.sub(r'<\/p>','\n\n', text)
    text = re.sub(r'<[^>]+>',' ',text)
    text = re.sub(r'!\[.*?\]\(.*?\)',' ',text)
    text = re.sub(r'\[.*?\]\(.*?\)',' ',text)
    text = re.sub(r' {2,}',' ',text)
    return text.strip()

def unicode_replace(text):
    uni = [
        ["…","..."],
        ["“","\""],
        ["”","\""],
        ["‘","'"],
        ["’","'"],
        ["–","-"],
        [""," "],
        ["ð","đ"],
        ["&amp;","&"],
        ["&quot;","\""],
        [" quot ","\""]
    ]
    for _, c in enumerate(uni):
        text = text.replace(c[0],c[1])
    return text

try:
    conn = sqlite3.connect('data/entries.db')
    cur = conn.cursor()
    records = 100
    page = 1
    data = []
    while True:
        start = ( page - 1 ) * records
        qry = cur.execute("SELECT title, excerpt, content FROM entries ORDER BY id ASC LIMIT {}, {}".format(start, records)).fetchall()
        if len(qry) == 0:
            break
        for row in qry:
            content = clean_text(row[2])
            content = '\n\n'.join([line.strip().strip('*') for line in unicode_replace(content).split('\n') if line.strip() ])
            text = "%s\n\n%s\n\n%s" % (row[0], row[1], content)
            base_text = unicode_replace(text).strip()
            data.append(base_text)
        page = page + 1
    cur.close()
    conn.close()
    print(len(data))
    with open('tmp/data.pkl','wb') as fout:
        pickle.dump(data, fout, protocol=pickle.HIGHEST_PROTOCOL)
except Exception as e:
    print(e)
