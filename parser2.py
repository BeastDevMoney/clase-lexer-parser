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
        ('right', 'ASSIGN'),
        ('left', 'NOT'),
        ('nonassoc', 'LE', '<', '='),
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('left', 'ISVOID'),
        ('left', '~'),
        ('left', '@'),
        ('left', '.')
    )

    # Programa como conjunto de clases

    @_('clases')
    def Programa(self, p):
        return Programa(secuencia=p.clases)

    @_('clase', 'clases clase')
    def clases(self, p):

        if len(p) == 2:
            return p.clases + [p.clase]
        else:
            return [p.clase]

    # Heredamos tipos y construimos clases con las caracteristicas

    @_('CLASS TYPEID herencia "{" caracteristicas "}" ";"')
    def clase(self, p):
        return Clase(nombre=p.TYPEID, padre=p.herencia, nombre_fichero=self.nombre_fichero,
                     caracteristicas=p.caracteristicas)

    @_('INHERITS TYPEID', )
    def herencia(self, p):
        return p.TYPEID

    @_('')
    def herencia(self, p):
        return 'Object'

    # Caracteristicas como conjunto de atributos y metodos

    @_('caracteristicas caracteristica')
    def caracteristicas(self, p):
        return p[0] + [p[1]]

    @_(" ")
    def caracteristicas(self, p):
        return []

    @_('atributo')
    def caracteristica(self, p):
        return p[0]

    @_('metodo')
    def caracteristica(self, p):
        return p[0]

    # Definicion de atributo

    @_('OBJECTID ":" TYPEID ";"')
    def atributo(self, p):
        return Atributo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=NoExpr())

    # Definicion de metodo

    @_("OBJECTID '(' formales ')' ':' TYPEID '{' expresion '}' ';'")
    def metodo(self, p):
        return Metodo(nombre=p.OBJECTID, formales=p.formales, tipo=p.TYPEID, cuerpo=p.expresion)

    # Definicion de formal y creacion de lista de formales

    @_("formal")
    def formales(self, p):
        return [p.formal]

    @_("formales ',' formal")
    def formales(self, p):
        return p.formales + [p.formal]

    @_(" ")
    def formales(self, p):
        return []

    @_("OBJECTID ':' TYPEID")
    def formal(self, p):
        return Formal(nombre_variable=p.OBJECTID, tipo=p.TYPEID)

    # Asignacion de expresiones

    @_('OBJECTID ASSIGN expresion')
    def expresion(self, p):
        return Asignacion(nombre=p.OBJECTID, cuerpo=p.expresion)

    # Operaciones binarias

    @_('expresion "+" expresion')
    def expresion(self, p):
        return Suma(izquierda=p[0], derecha=p[2], operando='+')

    @_('expresion "-" expresion')
    def expresion(self, p):
        return Resta(izquierda=p[0], derecha=p[2], operando='-')

    @_('expresion "*" expresion')
    def expresion(self, p):
        return Multiplicacion(izquierda=p[0], derecha=p[2], operando='*')

    @_('expresion "/" expresion')
    def expresion(self, p):
        return Division(izquierda=p[0], derecha=p[2], operando='/')

    @_('expresion "<" expresion')
    def expresion(self, p):
        return Menor(izquierda=p[0], derecha=p[2], operando='<')

    @_('expresion LE expresion')
    def expresion(self, p):
        return LeIgual(izquierda=p[0], derecha=p[2], operando='<=')

    @_('expresion "=" expresion')
    def expresion(self, p):
        return Igual(izquierda=p[0], derecha=p[2], operando='=')

    # Operaciones unarias

    @_('"(" expresion ")"')
    def expresion(self, p):
        return p.expresion

    @_('NOT expresion')
    def expresion(self, p):
        return Not(expr=p.expresion)

    @_('ISVOID expresion')
    def expresion(self, p):
        return EsNulo(expr=p.expresion)

    @_('"~" expresion')
    def expresion(self, p):
        return Neg(expr=p.expresion)

    # Metodos estaticos (@)

    @_('expresion "@" TYPEID "." OBJECTID "(" ")"')
    def expresion(self, p):
        return LlamadaMetodoEstatico(cuerpo=p.expresion, clase=p.TYPEID,  nombre_metodo=p.OBJECTID,argumentos=[])

    @_('expresion "@" TYPEID "." OBJECTID "(" expresiones expresion ")"')
    def expresion(self, p):
        return LlamadaMetodoEstatico(cuerpo=p.expresion0, clase=p.TYPEID, nombre_metodo=p.OBJECTID,
                                     argumentos=p.expresiones + [p.expresion1])

    @_('expresiones expresionmas ')
    def expresiones(self, p):
        return p.expresiones + [p.expresionmas]

    @_(" ")
    def expresiones(self, p):
        return []

    @_('expresion ","')
    def expresionmas(self, p):
        return p.expresion

    # Metodos normales (.)

    @_('expresion "." OBJECTID "(" expresiones expresion ")"')
    def expresion(self, p):
        return LlamadaMetodo(nombre_metodo=p.OBJECTID, argumentos=p.expresiones + [p.expresion1], cuerpo=p.expresion0)

    @_('OBJECTID "(" expresiones expresion ")"')
    def expresion(self, p):
        return LlamadaMetodo(nombre_metodo=p.OBJECTID, argumentos=p.expresiones + [p.expresion],
                             cuerpo=Objeto(nombre='self'))

    @_('OBJECTID "(" ")"')
    def expresion(self, p):
        return LlamadaMetodo(nombre_metodo=p.OBJECTID, cuerpo=Objeto(nombre='self'))

    @_('expresion "." OBJECTID "(" ")"')
    def expresion(self, p):
        return LlamadaMetodo(nombre_metodo=p.OBJECTID, argumentos=[], cuerpo=p.expresion)

    # Condicional y bucles

    @_('IF expresion THEN expresion ELSE expresion FI')
    def expresion(self, p):
        return Condicional(condicion=p.expresion0, verdadero=p.expresion1, falso=p.expresion2)

    @_('WHILE expresion LOOP expresion POOL')
    def expresion(self, p):
        return Bucle(condicion=p.expresion0, cuerpo=p.expresion1)

    #Let expresions
    @_('OBJECTID ":" TYPEID assign_opt')
    def let_func_one(self, p):
        return p.OBJECTID, p.TYPEID, p.assign_opt

    @_('let_func_one')
    def let_func(self, p):
        return [p.let_func_one]

    @_('let_func "," let_func_one')
    def let_func(self, p):
        return p.let_func + [p.let_func_one]

    @_('LET let_func IN expresion')
    def expresion(self, p):
        cuerpo = p.expresion
        for nombre, tipo, init in reversed(p.let_func):
            cuerpo = Let(nombre=nombre, tipo=tipo, inicializacion=init, cuerpo=cuerpo)
        return cuerpo

    @_('ASSIGN expresion')
    def assign_opt(self, p):
        return p.expresion

    @_(" ")
    def assign_opt(self, p):
        return NoExpr()

    # Rama Case

    @_('OBJECTID ":" TYPEID DARROW expresion ";"')
    def case_rep(self, p):
        return [RamaCase(nombre_variable=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expresion)]

    @_('case_rep OBJECTID ":" TYPEID DARROW expresion ";"')
    def case_rep(self, p):
        return p.case_rep + [RamaCase(nombre_variable=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expresion)]

    @_('CASE expresion OF case_rep ESAC')
    def expresion(self, p):
        return Swicht(expr=p.expresion, casos=p.case_rep)

    # Tipos y llaves

    @_('NEW TYPEID')
    def expresion(self, p):
        return Nueva(tipo=p.TYPEID)

    @_('"{" llaves_rep "}"')
    def expresion(self, p):
        return p.llaves_rep

    @_('llaves_rep expresion ";"')
    def llaves_rep(self, p):
        p.llaves_rep.expresiones.append(p.expresion)
        return p.llaves_rep

    @_('expresion ";"')
    def llaves_rep(self, p):
        return Bloque(expresiones=[p.expresion])

    @_('OBJECTID')
    def expresion(self, p):
        return Objeto(nombre=p.OBJECTID)

    @_('INT_CONST')
    def expresion(self, p):
        return Entero(valor=p.INT_CONST)

    @_('STR_CONST')
    def expresion(self, p):
        return String(valor=p.STR_CONST)

    @_('BOOL_CONST')
    def expresion(self, p):
        return Booleano(valor=p.BOOL_CONST)

    @_('NUMBER')
    def expresion(self, p):
        return Entero(valor=p.NUMBER)

    def error(self, p):
        if p:
            err_location = f'"{self.nombre_fichero}", line {p.lineno}'
            err_msg = f'syntax error at or near {p.type} = {p.value}'
            self.errores.append(f'{err_location}: {err_msg}')