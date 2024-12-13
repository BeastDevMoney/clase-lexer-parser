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
        ('right', 'ASSIGN'), # Esta operación es asociatiava hacia la derecha. o sea que T1 <- T2 <- T3 se interpreta como T1 <- (T2 <- T3)
        ('nonassoc', 'LE','<','=','NOT'), #Las 3 oeraciones loigcas no son asoicativas
        ("left",'ISVOID', '/','*','+', '-'),
        ('nonassoc', '@'),
        ('nonassoc','.')
        )


    #Ejercicio 2, definimos la gramática admitida por Cool

    @_('OBJECTID ":" TYPEID ";"') #⟨Formal⟩ ::= OBJECTID : TYPEID
    def atributo(self, p):
        return Atributo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=NoExpr())
    
    
    
    #definimos la expresion de asignación de un objeto y una expresion. Cuya expresión puede ser representada de las siguientes formas:
    '''
    
    | ⟨Expresion⟩ + ⟨Expresion⟩
    | ⟨Expresion⟩ - ⟨Expresion⟩
    | ⟨Expresion⟩ * ⟨Expresion⟩
    | ⟨Expresion⟩ / ⟨Expresion⟩
    | ⟨Expresion⟩ < ⟨Expresion⟩
    | ⟨Expresion⟩ <= ⟨Expresion⟩ Este se escribe como LE, lower or iqual. Porque está reservado el símbolo <= 
    | ⟨Expresion⟩ = ⟨Expresion⟩
    | ( ⟨Expresion⟩ )
    | NOT ⟨Expresion⟩ Esto tiene su propia operacion NOT
    | ISVOID ⟨Expresion⟩
    | ~ ⟨Expresion⟩ Esto es equivalente a la clase NEG de Clases.py
    | ⟨Expresion⟩ @ TYPEID . OBJECTID ( )
    | ⟨Expresion⟩ @ TYPEID . OBJECTID ( (⟨Expresion⟩ ,)* ⟨Expresion⟩ )
    | [ ⟨Expresion⟩ .] OBJECTID ( (⟨Expresion⟩ ,)* ⟨Expresion⟩ )
    | [ ⟨Expresion⟩ .] OBJECTID ( )
    | IF ⟨Expresion⟩ THEN ⟨Expresion⟩ ELSE ⟨Expresion⟩ FI
    | WHILE ⟨Expresion⟩ LOOP ⟨Expresion⟩ POOL
    | LET OBJECTID : TYPEID [<- ⟨Expresion⟩] (, OBJECTID : TYPEID [<- ⟨Expresion⟩])* IN ⟨Expresion⟩
    | CASE ⟨Expresion⟩ OF (OBJECTID : TYPEID DARROW <Expresion>)+ ; ESAC
    | NEW TYPEID
    | { (⟨Expresion⟩ ;) + }
    | OBJECTID
    | INT_CONST
    | STR_CONST
    | BOOL_CONST
    '''
    #⟨Expresion⟩ ::= OBJECTID ASSIGN ⟨Expresion⟩
    @_('OBJECTID ":" TYPEID ASSIGN expresion ";"') 
    def atributo(self, p):
        return Atributo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expresion)
    
    @_('expresion "+" expresion',
       'expresion "-" expresion',
       'expresion "*" expresion',
       'expresion "/" expresion',
       'expresion "<" expresion',
       'expresion "=" expresion',
       'expresion LE expresion',
       '"(" expresion ")"',
       '"~" expresion')
    def expresion(self,p):
        #definimos formalmente las operaciones
        #Tener en cuenta que estamos definiendo las entradas de las clases importadas del archivo Clases.py
        if p[1] == '+':
            return Suma(izquierda=p.expresion0, derecha=p.expresion1, operando='+') #Se hace con izquierda expreison0 y derecha expresion1 por las reglas de precedencia: "left",'ISVOID', '/','*','+', '-'
        elif p[1] == '-':
            return Resta(izquierda=p.expresion0, derecha=p.expresion1, operando='-')
        elif p[1] == '*':
            return Multiplicacion(izquierda=p.expresion0, derecha=p.expresion1, operando='*')
        elif p[1] == '/':
            return Division(izquierda=p.expresion0, derecha=p.expresion1, operando='/')
        elif p[1] == '<':
            return Menor(izquierda=p.expresion0, derecha=p.expresion1, operando='<')
        elif p[1] == '=':
            return Igual(izquierda=p.expresion0, derecha=p.expresion1, operando='=')
        elif p[1] == 'LE':
            return LeIgual(izquierda=p.expresion0, derecha=p.expresion1, operando='LE')
        elif p[0] == '(' and p[2] == ')':
            pass #Signfica que de p, el primer elemnetosea el primer parentesis y el tercero sea el segundo parentesis y el segundo sea la expresion p[1] = expresion
        elif p[0] == '~':
            return Neg(expr=p.expresion, operador='~')
        
        