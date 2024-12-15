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

    # Regla principal que define el programa completo
    @_('clases')
    def Programa(self, p):
        return Programa(secuencia=p.clases)

    # Lista de clases
    @_('clase', 'clases clase') # puede ser una clase o una lista de clases seguida de una clase
    def clases(self, p):
        #Si es una lista de clases, p tendra el elemento clases y clase
        if len(p) == 2:
            return p.clases + [p.clase] #Clases ya es una lista
        else:
            return [p.clase]
        


    # Regla para clases ⟨Clase⟩ ::= CLASS TYPEID [inherits TYPEID] { (⟨Atributo⟩ | ⟨Metodo⟩ )* } ;

    @_('CLASS TYPEID atributosHeredados "{" atributos "}" ";"')
    def clase(self, p):
        return Clase(nombre=p.TYPEID, padre=p.atributosHeredados, nombre_fichero=self.nombre_fichero, caracteristicas=p.atributos)


    @_('INHERITS TYPEID')
    def atributosHeredados(self, p):
        return p.TYPEID
    
    @_('')
    def atributosHeredados(self, p):
        return 'Object'

    # Lista de atributos (features)
    @_('atributos  atributo')
    def atributos(self, p):
        return p.atributos + [p.atributo]

    @_(' ') #Si no hay atributos, se devuelve una lista vacía
    def atributos(self, p):
        return []
    
    @_('atributo')
    def atributo(self, p):
        return p[0]


    @_('metodo')
    def atributo(self, p):
        return p[0]
    
    
    @_('OBJECTID ":" TYPEID ";"')
    def atributo(self, p):
        return Atributo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=NoExpr()) #Para este tipo, es solo el Object id y su tipo, no tiene expresion
    

    #⟨Metodo⟩ ::= OBJECTID ( ) : TYPEID { ⟨Expresion⟩ } ; Pueden ser con la lista de formales vacía
    #| OBJECTID ( (⟨Formal⟩ , )* ⟨Formal⟩ ) : TYPEID { ⟨Expresion⟩ } ; Pueden ser con la lista de formales no vacía

    @_('OBJECTID "(" formales ")" ":" TYPEID "{" expresion "}" ";"') #Formales no vacía
    def metodo(self, p):
        return Metodo(nombre=p.OBJECTID, formales=p.formales, tipo=p.TYPEID, cuerpo=p.expresion)


    @_('formal')
    def formales(self, p):
        return [p.formal]
    

    @_('formales "," formal')
    def formales(self, p):
        return p.formales + [p.formal]

    @_(' ')
    def formales(self, p):
        return []

    
    @_('OBJECTID ":" TYPEID')
    def formal(self, p):
        return Formal(nombre_variable=p.OBJECTID, tipo=p.TYPEID)
    
    @_('OBJECTID ASSIGN expresion')
    def expresion(self, p):
        return Asignacion(nombre=p.OBJECTID, cuerpo=p.expresion)

    # Bloques de expresiones

    # Operaciones y expresiones básicas
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

    @_('"(" expresion ")"')
    def expresion(self, p):
        return p.expresion
        
    @_('NOT expresion')
    def expresion(self, p):
        return Not(expr=p.expresion, operador='NOT')

    @_('ISVOID expresion')
    def expresion(self, p):
        return EsNulo(expr=p.expresion)

    @_('"~" expresion')
    def expresion(self, p):
        return Neg(expr=p.expresion,operador='~')

    #Tipos de expresiones
    #Expresion estáticas: ⟨Expresion⟩ @ TYPEID . OBJECTID ( )

    @_('expresion "@" TYPEID "." OBJECTID "(" ")"')
    def expresion(self, p):
        return LlamadaMetodoEstatico(cuerpo=p.expresion, clase=p.TYPEID, nombre_metodo=p.OBJECTID, argumentos=[])
    

    #⟨Expresion⟩ @ TYPEID . OBJECTID ( (⟨Expresion⟩ ,)* ⟨Expresion⟩ )
    @_('expresion "@" TYPEID "." OBJECTID "(" expresiones  expresion ")"')
    def expresion(self, p):
        return LlamadaMetodoEstatico(cuerpo=p.expresion0, clase=p.TYPEID, nombre_metodo=p.OBJECTID, argumentos=p.expresiones + [p.expresion1])



    @_('expresiones expresion ","')
    def expresiones(self, p):
        return p.expresiones + [p.expresion]

    
    @_(' ')
    def expresiones(self, p):
        return []


    #Expresones dinámicas : [ ⟨Expresion⟩ .] OBJECTID ( (⟨Expresion⟩ ,)* ⟨Expresion⟩ )
                        # | [ ⟨Expresion⟩ .] OBJECTID ( )    

    @_('expresion "." OBJECTID "(" expresiones  expresion ")"')
    def expresion(self, p):
        return LlamadaMetodo(cuerpo=p.expresion0, nombre_metodo=p.OBJECTID, argumentos=p.expresiones + [p.expresion1])

    @_('OBJECTID "(" expresiones expresion ")"')
    def expresion(self, p):
        return LlamadaMetodo(nombre_metodo=p.OBJECTID, argumentos=p.expresiones + [p.expresion], cuerpo=Objeto(nombre='self'))

    @_('OBJECTID "(" ")"')
    def expresion(self, p):
        return LlamadaMetodo(nombre_metodo=p.OBJECTID, cuerpo=Objeto(nombre='self'))

    @_('expresion "." OBJECTID "(" ")"')
    def expresion(self, p):
        return LlamadaMetodo(cuerpo=p.expresion, nombre_metodo=p.OBJECTID, argumentos=[])
        

    #Estructuras de control de flujo: IF ⟨Expresion⟩ THEN ⟨Expresion⟩ ELSE ⟨Expresion⟩ FI
    #                               | WHILE ⟨Expresion⟩ LOOP ⟨Expresion⟩ POOL

    @_('IF expresion THEN expresion ELSE expresion FI')
    def expresion(self, p):
        return Condicional(condicion=p.expresion0, verdadero=p.expresion1, falso=p.expresion2)
    
    
    @_('WHILE expresion LOOP expresion POOL')
    def expresion(self, p):
        return Bucle(condicion=p.expresion0, cuerpo=p.expresion1)


    #LET OBJECTID : TYPEID [<- ⟨Expresion⟩] (, OBJECTID : TYPEID [<- ⟨Expresion⟩])* IN ⟨Expresion⟩
    

    #Declaracion de unica variable
    @_('OBJECTID ":" TYPEID opt_assign')
    def let_declaration(self, p):
        return (p.OBJECTID, p.TYPEID, p.opt_assign)
    
    #Declaracion de varias variables 
    @_('let_declaration')
    def let_declarations(self, p):
        return [p.let_declaration]
    
    @_('let_declarations "," let_declaration')
    def let_declarations(self, p):
        return p.let_declarations + [p.let_declaration]
    
    #Cuerpo completo
    @_('LET let_declarations IN expresion')
    def expresion(self, p):
        cuerpoExpresion = p.expresion
        for nombre, tipo, inicializacion in reversed(p.let_declarations):
            cuerpoExpresion = Let(nombre=nombre, tipo=tipo, inicializacion=inicializacion, cuerpo=cuerpoExpresion)
        return cuerpoExpresion
    
    @_('ASSIGN expresion')
    def opt_assign(self, p):
        return p.expresion
    
    @_(' ')
    def opt_assign(self, p):
        return NoExpr()

    #CASE ⟨Expresion⟩ OF (OBJECTID : TYPEID DARROW <Expresion>)+ ; ESAC

    @_('OBJECTID ":" TYPEID DARROW expresion ";"')
    def case_list(self, p):
        return [RamaCase(nombre_variable=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expresion)]

    @_('case_list OBJECTID ":" TYPEID DARROW expresion ";"')
    def case_list(self, p):
        return p.case_list + [RamaCase(nombre_variable=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expresion)]
    
    @_('CASE expresion OF case_list ESAC')
    def expresion(self, p):
        return Swicht(expr=p.expresion, casos=p.case_list)
    


    #Expresiones entre llaves: { (⟨Expresion⟩ ;) + }

    #Cogemos los espacioes entre expresiones
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

    
    # Asignación
    
    @_('NEW TYPEID')
    def expresion(self, p):
        return Nueva(tipo=p.TYPEID)
    
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
    

    # Manejo de errores
    def error(self, p):
        if p:
            print(f"Error de sintaxis: token inesperado '{p.value}' en línea {p.lineno}")
            self.errores.append(f"Error de sintaxis: token inesperado '{p.value}' en línea {p.lineno}")
            self.errok()
        else:
            print("Error de sintaxis: fin inesperado del archivo")
            self.errores.append("Error de sintaxis: fin inesperado del archivo")