
import re

ID = r'(?P<ID>[a-zA-Z_][a-zA-Z0-9_]*)'
NUMBER = r'(?P<NUMBER>\d+)'
SPACE = r'(?P<SPACE>\s+)'

patterns = [ID, NUMBER, SPACE]

# Expresión regular general
pat = re.compile('|'.join(patterns))
def tokenize(text):
    index = 0
    while index < len(text):
        m = pat.match(text,index)
        if m:
            lastgroup = m.lastgroup
            group = m.group()   
            if lastgroup != 'SPACE':
                yield (lastgroup, group)

            index = m.end()
        else:
            print('Unknown Character %r' % text[index])
            index +=1

# Ejemplo de uso
text = '123 abc ! 234 cde 456'
print('Tokenizing:', tokenize(text))
for tok in tokenize(text):
    print(tok)
