# coding: utf-8
# coding: utf-8
from sly import Lexer
import os
import re
import sys



class CoolLexer(Lexer):
    tokens = {OBJECTID, INT_CONST, BOOL_CONST, TYPEID,
              ELSE, IF, FI, THEN, NOT, IN, CASE, ESAC, CLASS,
              INHERITS, ISVOID, LET, LOOP, NEW, OF,
              POOL, THEN, WHILE, NUMBER, STR_CONST, LE, DARROW, ASSIGN}
    #ignore = '\t '
    literals = {'(', '*', ')', ';', '{', '}', '=', ':', '.', ',', '~', '-', '/', '<', '@', '+'}
    # Ejemplo
    ELSE = r'\b[eE][lL][sS][eE]\b'
    KeysValues  = {'NOT', 'IN', 'CASE', 'CLASS', 'ESAC', 'FI', 'IF', 'INHERITS', 'ISVOID', 'LET', 'LOOP', 'NEW', 'OF',
                'POOL', 'THEN', 'WHILE'}
    

    CARACTERES_CONTROL = [bytes.fromhex(i+hex(j)[-1]).decode('ascii')
                          for i in ['0', '1']
                          for j in range(16)] + [bytes.fromhex(hex(127)[-2:]).decode("ascii")]
    
    # Ejercicio 1, definimos las expresiones regulares para los tokens
    
    
    @_(r'\d+') #\d significa cualquier dígito entre 0 y 9, el + indica que se puede repetir 1 o más veces
    def INT_CONST(self, t):
        return t
    
    @_(r'"([^"]*)"')
    def STR_CONST(self, t):
        t.value = t.value.replace('\t', '\\t')
        t.value = t.value.replace('\n', '\\n') 
        return t
    
    @_(r'(t[rR][uU][eE]\b)|(f[aA][lL][sS][eE]\b)') #Indica que empezar por minúscula y luego todas las variantes, al final tiene que haber un espacio, indicado por \b
    def BOOL_CONST(self, t):
        if t.value.lower() == 'true':
            t.value = True
        else:
            t.value = False
        return t

    @_(r'<=') #Indica que tiene que ser <= para tokenizarlo como LE
    def LE(self, t):
        return t
    
    @_(r'=>') #Indica que tiene que ser => para tokenizarlo como DARROW
    def DARROW(self,t):
        return t
    
    @_(r'<-|->') #Indica que tiene que ser <- para tokenizarlo como ASSIGN
    def ASSIGN(self,t):
        return t
    
    #Los OBJECTID o identificadores empiezan por minúscula
    @_(r'[a-z][a-zA-Z0-9_]*')
    def OBJECTID(self, t):  # También tiene que leer palabras conectadas por barra baja
        if t.value.upper() in self.KeysValues:
            t.type = t.value.upper()
        return t
    
    #Los TYPEID o indicadores de tipos empiezan por mayúscula
    @_(r'[A-Z][a-zA-Z0-9_]*') #Cualquiero conjunto [] de A-Z seguido de cualquiero conjunto de [] a-zA-Z0-9 o con guión bajo _
    def TYPEID(self, t):
        if t.value.upper() in self.KeysValues:
            t.type = t.value.upper()
        return t
    
    @_(r'\(\*((.|\n)*?)\*\)|--(.*)') #Indica que tiene que ser * seguido de cualquier carácter distinto de *
    def multilinecomment(self, t):
        self.lineno += t.value.count('\n')
    
    @_(r'\t| |\v|\r|\f') #Para cualquier \t, \v, \r, \f significa que conlleva un espacio, por eso pasa
    def spaces(self, t):
        pass

    @_(r'\n+') #Indica que se puede repetir 1 o más veces el \n 
    def newline(self, t):
        self.lineno += t.value.count('\n')

    


    def error(self, t): #Esta es la función de error por defecto de sly
        self.index += 1
    @_('_|\*\)|\!|\#|\$|\%|\^|\&|\>|\?|\`|\[|\[|\]|\||\\\\|EOF') #Secuencia de caracteres no permitidos
    def ERROR(self, t):
        if t.value == '_':
            t.value = '"_"'
        if t.value == '!':
            t.value = '"!"'
        if t.value == '#':
            t.value = '"#"'
        if t.value == '$':
            t.value = '"$"'
        if t.value == '%':
            t.value = '"%"'
        if t.value == '^':
            t.value = '"^"'
        if t.value == '&':
            t.value = '"&"'
        if t.value == '>':
            t.value = '">"'
        if t.value == '?':
            t.value = '"?"'
        if t.value == '`':
            t.value = '"`"'
        if t.value == '[':
            t.value = '"["'
        if t.value == ']':
            t.value = '"]"'
        if t.value == '|':
            t.value = '"|"'
        if t.value == '\\':
            t.value = '"\\\\"'
        elif t.value == '*)':
            t.value = '"Unmatched *)"'
        return t    
    
    def salida(self, texto):
        lexer = CoolLexer()
        list_strings = []
        for token in lexer.tokenize(texto):
            result = f'#{token.lineno} {token.type} '
            if token.type == 'OBJECTID':
                result += f"{token.value}"
            elif token.type == 'BOOL_CONST':
                result += "true" if token.value else "false"
            elif token.type == 'TYPEID':
                result += f"{str(token.value)}"
            elif token.type in self.literals:
                result = f'#{token.lineno} \'{token.type}\' '
            elif token.type == 'STR_CONST':
                result += token.value
            elif token.type == 'INT_CONST':
                result += str(token.value)
            elif token.type == 'ERROR':
                result = f'#{token.lineno} {token.type} {token.value}'
            else:
                result = f'#{token.lineno} {token.type}'
            list_strings.append(result)
        return list_strings
