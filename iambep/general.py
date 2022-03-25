import json
import re
with open('iambep.raw','r',encoding='utf-8') as f:
    entries = json.load(f)

def get_note(s):
    tmp = s.split('post/')[1]
    tmp = tmp.split('/')[0]
    return tmp

def line_break(s):
    if '![' in s:
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
        lines.append(line.strip())
    return '\n'.join(lines)

for entry in entries:
    node = get_note(entry['link'])
    lines = [ line_break(line) for line in entry['content'].strip().split('\n') if line.strip() ]
    description = lines[0]
    if '![' in description:
        description = lines[1]
    content = '\n\n'.join(lines)
    content = re.sub(r'\n{2,}','\n\n',content)
    with open(('%s.md' % node),'w',encoding='utf-8') as f:
        f.write("---\nid:{}\ndescription:{}\nlink:{}\n---\n\n{}".format(entry['id'],description, entry['link'], content))
