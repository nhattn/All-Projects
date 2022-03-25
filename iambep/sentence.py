import json
import re
from pyvi import ViTokenizer, ViPosTagger
with open('iambep.raw','r',encoding='utf-8') as f:
    entries = json.load(f)
sentences = set()
fout = open('sentences.txt','w',encoding='utf-8')
ftok = open('tokeninzed.txt','w',encoding='utf-8')
ftag = open('tagged.txt','w',encoding='utf-8')
for entry in entries:
    lines = [ line.strip() for line in entry['content'].strip().split('\n') if line.strip() and '](' not in line and '...' not in line ]
    for line in lines:
        for sentence in re.split(r'\.\s+', line):
            if '#' in sentence or '://' in sentence:
                continue
            if 'From BeP' in sentence:
                continue
            if sentence not in sentences:
                if sentence[-1:] == '.':
                    sentence = sentence[:-1]
                sentences.add(sentence)
                fout.write(sentence+"\n")
                tokeninzed = ViTokenizer.tokenize(sentence)
                ftok.write(tokeninzed+"\n")
                result = ViPosTagger.postagging(tokeninzed)
                tagged = []
                for i, token in enumerate(result[0]):
                    tagged.append(token+'/'+result[1][i])
                ftag.write(' '.join(tagged)+"\n")                
print(sentences)
fout.close()
ftok.close()
ftag.close()
