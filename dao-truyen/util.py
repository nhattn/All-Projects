# -*- coding: utf-8 -*-

import re
import os
import uuid
import json
import urllib.request as urllib
from PIL import Image
import config

def epub_uuid():
    return "story_" + str(uuid.uuid4())

def no_accent(s):
    s = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', s)
    s = re.sub(r'[ÀÁẠẢÃĂẰẮẶẲẴÂẦẤẬẨẪ]', 'A', s)
    s = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', s)
    s = re.sub(r'[ÈÉẸẺẼÊỀẾỆỂỄ]', 'E', s)
    s = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', s)
    s = re.sub(r'[ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ]', 'O', s)
    s = re.sub(r'[ìíịỉĩ]', 'i', s)
    s = re.sub(r'[ÌÍỊỈĨ]', 'I', s)
    s = re.sub(r'[ùúụủũưừứựửữ]', 'u', s)
    s = re.sub(r'[ƯỪỨỰỬỮÙÚỤỦŨ]', 'U', s)
    s = re.sub(r'[ỳýỵỷỹ]', 'y', s)
    s = re.sub(r'[ỲÝỴỶỸ]', 'Y', s)
    s = re.sub(r'[Đ]', 'D', s)
    s = re.sub(r'[đ]', 'd', s)
    return s

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

def line_break(s):
    words = [word.strip() for word in s.split(' ') if word.strip() ]
    lines = []
    line = ''
    for word in words:
        line += ' ' + word
        if len(line) >= 72:
            lines.append(line.strip())
            line = ''
    if len(line) > 0:
        lines.append(line.strip())
    return '\n'.join(lines)

def download_cover(url, folder, filename):
    try:
        #yield os.system('wget -q "%s" -O "books/%s/%s"' % (url, folder, filename))
        resource = urllib.urlopen(url)
        cover_file = os.path.join(config.BOOK_DIRECTORY, folder, filename)
        output = open(cover_file,"wb")
        output.write(resource.read())
        output.close()
        im = Image.open(cover_file)
        width, height = im.size
        new_width = 362
        radito = new_width / width
        new_height = int(radito * height)
        newsize = (new_width, new_height)
        im1 = im.resize(newsize)
        im1.save(cover_file)
        return filename
    except Exception as e:
        print(e)
        return ''

def story2folder(name):
    folder_name = no_accent(unicode_replace(name))
    folder_name = re.sub(r'\s+',' ', folder_name)
    folder_name = folder_name.strip().replace(' ','_')
    return folder_name

def save_metadata(filepath, metadata):
    try:
        with open(filepath,'w', encoding='utf-8') as fout:
            fout.write(json.dumps(metadata,indent=2,ensure_ascii=False))
        return True
    except:
        return False

def read_metadata(filepath):
    try:
        with open(filepath,'r', encoding='utf-8') as fin:
            metadata = json.load(fin)
        if isinstance(metadata, dict):
            return metadata
        return None
    except:
        return None

def jsonify(data):
    return json.dumps(data,indent=2,ensure_ascii=False)
