import json
import re
from unidecode import unidecode
with open('ocuaso.raw','r',encoding='utf-8') as f:
    entries = json.load(f)

def unicode_replace(text):
    uni = [
        ["…","..."],
        ["“","\""],
        ["”","\""],
        ["–","-"],
        [""," "],
        ["😀"," "],
        ["\t",""],
        ["»",""]
    ]
    for _, c in enumerate(uni):
        text = text.replace(c[0],c[1])
    return text

def line_break(s):
    s = unicode_replace(s)
    if '![' in s or '](' in s:
        return s
    words = [word.strip() for word in s.split(' ') if word.strip() ]
    lines = []
    line = ''
    for word in words:
        line += ' ' + word
        if len(line) >= 72:
            lines.append(line.strip())
            line = ''
    if len(line) > 0:
        if line.strip() == '#' or line.strip() == '##' or line.strip() == '###' or line.strip() == '####' or line.strip() == '#####' or line.strip() == '######':
            line = ''
        if line.strip():
            lines.append(line.strip())
    return '\n'.join(lines)

uniqued = set()

for entry in entries:
    entry['title'] = unicode_replace(entry['title'])
    lines = [ line_break(line) for line in entry['content'].strip().split('\n') if line.strip() ]
    if entry['title'].lower() in lines[0].lower():
        lines = lines[1:]
    i = 0
    while i < 5:
        description = lines[i]
        if '![' not in description and '](' in description:
            description = description.split('](')[0]
            description = description[1:]
            if description.strip():
                break
        if '![' not in description and '](' not in description:
            break
        i = i + 1
        if i >= len(lines):
            description = ''
            break
    description = description.replace('\n',' ')
    description = description.replace(':','')
    content = '\n\n'.join(lines)
    content = re.sub(r'\n{2,}','\n\n',content)
    node = unidecode(entry['title'])
    node = re.sub(r'[^a-zA-Z0-9]+',' ',node.strip())
    node = re.sub(r'\s+',' ',node.strip())
    node = node.replace(' ','-')
    node = node.lower()
    if node in uniqued:
        for i in range(1,4):
            if node + '-' + str(i) not in uniqued:
                node = node + '-' + str(i)
                uniqued.add(node)
                break
    else:
        uniqued.add(node)

    with open(('markdowns/%s.md' % node),'w',encoding='utf-8') as f:
        f.write("---\nid : {}\ntitle : {}\ndescription : {}\nlink : {}\n---\n\n{}".format(entry['id'], entry['title'],description, entry['url'], content))
