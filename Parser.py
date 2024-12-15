# coding: utf-8

from Lexer import CoolLexer
from sly import Parser
import sys
import os
from Clases import *


class CoolParser(Parser):
    nombre_fichero = ''
    tokens = CoolLexer.tokens
    debugfile = "salida.out"
    errores = []

    precedence = (
        ('right', 'ASSIGN'),  # Esta operación es asociativa hacia la derecha. o sea que T1 <- T2 <- T3 se interpreta como T1 <- (T2 <- T3)
        ('nonassoc', 'LE', '<', '=', 'NOT'),  # Las 3 operaciones lógicas no son asociativas
        ("left", 'ISVOID', '/', '*', '+', '-'),
        ('nonassoc', '@'),
        ('nonassoc', '.')
    )

    # Regla principal que define el programa completo
    @_('class_list')
    def Programa(self, p):
        return Programa(clases=p.class_list)

    # Lista de clases
    @_('class_decl class_list')
    def class_list(self, p):
        return [p.class_decl] + p.class_list

    @_('class_decl')
    def class_list(self, p):
        return [p.class_decl]

    # Regla para clases
    @_('CLASS TYPEID "{" feature_list "}"')
    def class_decl(self, p):
        return Clase(nombre=p.TYPEID, padre=None, cuerpo=p.feature_list)

    @_('CLASS TYPEID INHERITS TYPEID "{" feature_list "}"')
    def class_decl(self, p):
        return Clase(nombre=p.TYPEID, padre=p.TYPEID1, cuerpo=p.feature_list)

    # Lista de características (features)
    @_('feature ";" feature_list')
    def feature_list(self, p):
        return [p.feature] + p.feature_list

    @_('feature ";"')
    def feature_list(self, p):
        return [p.feature]

    # Método
    @_('OBJECTID "(" formal_list ")" ":" TYPEID "{" expresion "}"')
    def feature(self, p):
        return Metodo(nombre=p.OBJECTID, tipo=p.TYPEID, formales=p.formal_list, cuerpo=p.expresion)

    @_('formal "," formal_list')
    def formal_list(self, p):
        return [p.formal] + p.formal_list

    @_('formal')
    def formal_list(self, p):
        return [p.formal]

    @_('OBJECTID ":" TYPEID')
    def formal(self, p):
        return Formal(nombre=p.OBJECTID, tipo=p.TYPEID)

    # Bloques de expresiones
    @_('"{" expresion_list "}"')
    def expresion(self, p):
        return Bloque(cuerpo=p.expresion_list)

    @_('expresion ";" expresion_list')
    def expresion_list(self, p):
        return [p.expresion] + p.expresion_list

    @_('expresion ";"')
    def expresion_list(self, p):
        return [p.expresion]

    # Operaciones y expresiones básicas
    @_('expresion "+" expresion',
       'expresion "-" expresion',
       'expresion "*" expresion',
       'expresion "/" expresion',
       'expresion "<" expresion',
       'expresion "=" expresion',
       'expresion LE expresion')
    def expresion(self, p):
        if p[1] == '+':
            return Suma(izquierda=p.expresion0, derecha=p.expresion1)
        elif p[1] == '-':
            return Resta(izquierda=p.expresion0, derecha=p.expresion1)
        elif p[1] == '*':
            return Multiplicacion(izquierda=p.expresion0, derecha=p.expresion1)
        elif p[1] == '/':
            return Division(izquierda=p.expresion0, derecha=p.expresion1)
        elif p[1] == '<':
            return Menor(izquierda=p.expresion0, derecha=p.expresion1)
        elif p[1] == '=':
            return Igual(izquierda=p.expresion0, derecha=p.expresion1)
        elif p[1] == 'LE':
            return LeIgual(izquierda=p.expresion0, derecha=p.expresion1)

    @_('ISVOID expresion')
    def expresion(self, p):
        return IsVoid(expr=p.expresion)

    @_('NOT expresion')
    def expresion(self, p):
        return Not(expr=p.expresion)

    @_('"~" expresion')
    def expresion(self, p):
        return Neg(expr=p.expresion)

    # Manejo de errores
    def error(self, p):
        if p:
            print(f"Error de sintaxis: token inesperado '{p.value}' en línea {p.lineno}")
            self.errores.append(f"Error de sintaxis: token inesperado '{p.value}' en línea {p.lineno}")
            self.errok()
        else:
            print("Error de sintaxis: fin inesperado del archivo")
            self.errores.append("Error de sintaxis: fin inesperado del archivo")