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
                                                                    #Lo de arriba es un or |, entonces hay que definir para cuando sea <Atributo> y <Metodo>
    @_('CLASS TYPEID "{" atributos "}" ";"')
    def clase(self, p):
        return Clase(nombre=p.TYPEID, padre="Object", nombre_fichero=self.nombre_fichero, caracteristicas=p.atributos)

    @_('CLASS TYPEID "{" metodos "}" ";"')
    def clase(self, p):
        return Clase(nombre=p.TYPEID, padre="Object", nombre_fichero=self.nombre_fichero, caracteristicas=p.metodos)
    

    @_('CLASS TYPEID INHERITS TYPEID "{" atributos "}" ";"')
    def clase(self, p):
        return Clase(nombre=p.TYPEID0, padre=p.TYPEID1, nombre_fichero=self.nombre_fichero, caracteristicas=p.atributos)

    @_('CLASS TYPEID INHERITS TYPEID "{" metodos "}" ";"')
    def clase(self, p):
        return Clase(nombre=p.TYPEID0, padre=p.TYPEID1, nombre_fichero=self.nombre_fichero, caracteristicas=p.metodos)


    # Lista de atributos (features)
    @_('atributos  atributo')
    def atributos(self, p):
        return p.atributos + [p.atributo]

    @_(' ') #Si no hay atributos, se devuelve una lista vacía
    def atributos(self, p):
        return []

    #Definimos las reglas para atributs:⟨Atributo⟩ ::= OBJECTID : TYPEID [ASSIGN ⟨Expresion⟩];
    @_('OBJECTID ":" TYPEID ";"')
    def atributo(self, p):
        return Atributo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=NoExpr()) #Para este tipo, es solo el Object id y su tipo, no tiene expresion
    
    @_('OBJECTID ":" TYPEID ASSIGN expresion ";"')
    def atributo(self, p):
        return Atributo(nombre=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expresion)
    

    # Defininoms los métodos y su gramática
    @_('metodos metodo', ' ') #Si hay más de un método, se devuelve una lista con los métodos
    def metodos(self, p):
        return [p.metodos] + p.metodo
    
    #⟨Metodo⟩ ::= OBJECTID ( ) : TYPEID { ⟨Expresion⟩ } ; Pueden ser con la lista de formales vacía
    #| OBJECTID ( (⟨Formal⟩ , )* ⟨Formal⟩ ) : TYPEID { ⟨Expresion⟩ } ; Pueden ser con la lista de formales no vacía

    @_('OBJECTID "(" ")" ":" TYPEID "{" expresion "}" ";"') #Formales vacía
    def metodo(self, p):
        return Metodo(nombre=p.OBJECTID, formales=[], tipo=p.TYPEID, cuerpo=p.expresion)
    
    @_('OBJECTID "(" formales ")" ":" TYPEID "{" expresion "}" ";"') #Formales no vacía

    @_('formales formal "," ')
    def formales(self, p):
        return p.formales + [p.formal]

    #Caso en que formales este vacio
    @_(" ")
    def formales(self, p):
        return []
    
    @_('OBJECTID ":" TYPEID')
    def formal(self, p):
        return Formal(nombre_variable=p.OBJECTID, tipo=p.TYPEID)

    # Bloques de expresiones

    # Operaciones y expresiones básicas
    @_('expresion "+" expresion',
       'expresion "-" expresion',
       'expresion "*" expresion',
       'expresion "/" expresion',
       'expresion "<" expresion',
       'expresion "=" expresion',
       'expresion LE expresion',
       '"(" expresion ")"',
       '"~" expresion')
    def expresion(self, p):
        if p[1] == '+':
            return Suma(izquierda=p.expresion0, derecha=p.expresion1, operando='+')
        elif p[1] == '-':
            return Resta(izquierda=p.expresion0, derecha=p.expresion1, operando="-")
        elif p[1] == '*':
            return Multiplicacion(izquierda=p.expresion0, derecha=p.expresion1, operando='*')
        elif p[1] == '/':
            return Division(izquierda=p.expresion0, derecha=p.expresion1, operando='/')
        elif p[1] == '<':
            return Menor(izquierda=p.expresion0, derecha=p.expresion1, operando='<')
        elif p[1] == '=':
            return Igual(izquierda=p.expresion0, derecha=p.expresion1, operando="=")
        elif p[1] == 'LE':
            return LeIgual(izquierda=p.expresion0, derecha=p.expresion1, operando='<=')
        elif p[0] == '(' and p[2] == ')':
            pass
        elif p[0] == '~':
            return Neg(expr=p.expresion, operador='~')
        

    @_('ISVOID expresion')
    def expresion(self, p):
        return EsNulo(expr=p.expresion)

    @_('NOT expresion')
    def expresion(self, p):
        return Not(expr=p.expresion, operador='NOT')

    #Tipos de expresiones
    #Expresion estáticas: ⟨Expresion⟩ @ TYPEID . OBJECTID ( )

    @_('expresion "@" TYPEID "." OBJECTID "(" ")"')
    def expresion(self, p):
        return LlamadaMetodoEstatico(cuerpo=p.expresion, clase=p.TYPEID, nombre_metodo=p.OBJECTID, argumentos=[])
    

    @_('expresiones expresion ","')
    def expresiones(self, p):
        return p.expresiones + [p.expresion]


    
    @_(' ')
    def expresiones(self, p):
        return []

    #⟨Expresion⟩ @ TYPEID . OBJECTID ( (⟨Expresion⟩ ,)* ⟨Expresion⟩ )
    @_('expresion "@" TYPEID "." OBJECTID "(" expresiones "," expresion ")"')
    def expresion(self, p):
        return LlamadaMetodoEstatico(cuerpo=p.expresion0, clase=p.TYPEID, nombre_metodo=p.OBJECTID, argumentos=p.expresiones + [p.expresion1])

    #Expresones dinámicas : [ ⟨Expresion⟩ .] OBJECTID ( (⟨Expresion⟩ ,)* ⟨Expresion⟩ )
                        # | [ ⟨Expresion⟩ .] OBJECTID ( )

    @_('expresion "." OBJECTID "(" ")"')
    def expresion(self, p):
        return LlamadaMetodo(cuerpo=p.expresion, nombre_metodo=p.OBJECTID, argumentos=[])
    

    @_('expresion "." OBJECTID "(" expresiones "," expresion ")"')
    def expresion(self, p):
        return LlamadaMetodo(cuerpo=p.expresion0, nombre_metodo=p.OBJECTID, argumentos=p.expresiones + [p.expresion1])

    #Estructuras de control de flujo: IF ⟨Expresion⟩ THEN ⟨Expresion⟩ ELSE ⟨Expresion⟩ FI
    #                               | WHILE ⟨Expresion⟩ LOOP ⟨Expresion⟩ POOL

    @_('IF expresion THEN expresion ELSE expresion FI')
    def expresion(self, p):
        return Condicional(condicion=p.expresion0, verdadero=p.expresion1, falso=p.expresion2)
    
    @_('WHILE expresion LOOP expresion POOL')
    def expresion(self, p):
        return Bucle(condicion=p.expresion0, cuerpo=p.expresion1)


    #LET OBJECTID : TYPEID [<- ⟨Expresion⟩] (, OBJECTID : TYPEID [<- ⟨Expresion⟩])* IN ⟨Expresion⟩

    @_(' ')
    def opt_assign(self, p):
        return NoExpr()
    
    @_('ASSIGN expresion')
    def opt_assign(self, p):
        return p.expresion

    #Declaracion de unica variable
    @_('OBJECTID ":" TYPEID opt_assign')
    def let_declaration(self, p):
        return (p.OBJECTID, p.TYPEID, p.opt_assign)
    
    #Declaracion de varias variables 
    @_('let_declaration')
    def let_declarations(self, p):
        return [p.let_declarations]
    
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
    


    #CASE ⟨Expresion⟩ OF (OBJECTID : TYPEID DARROW <Expresion>)+ ; ESAC

    @_('OBJECTID ":" TYPEID DARROW expresion')
    def case_list(self, p):
        return [RamaCase(nombre_variable=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expresion)]

    @_('case_list OBJECTID ":" TYPEID DARROW expresion')
    def case_list(self, p):
        return p.case_list + [RamaCase(nombre_variable=p.OBJECTID, tipo=p.TYPEID, cuerpo=p.expresion)]
    
    @_('CASE expresion OF case_list ";" ESAC')
    def expresion(self, p):
        return Swicht(expr=p.expresion, casos=p.case_list)
    


    #Expresiones entre llaves: { (⟨Expresion⟩ ;) + }

    #Cogemos los espacioes entre expresiones
    @_(' ')
    def espacios(self, p):
        return []
    
    @_('espacios expresion ";"')
    def expresion_lista(self, p):
        return Bloque(expresiones=p.espacios + [p.expresion])

    @_('"{" expresion_lista expresion ";" "}"')
    def expresion(self, p):
        return Bloque(expresiones=p.expresion_lista + [p.expresion])
    

    
    # Asignación
    
    @_('NEW TYPEID')
    def expresion(self, p):
        return Nueva(tipo=p.TYPEID)
    
    @_('INT_CONST')
    def expresion(self, p):
        return Entero(valor=p.INT_CONST)
    
    @_('STR_CONST')
    def expresion(self, p):
        return String(valor=p.STR_CONST)
    
    @_('BOOL_CONST')
    def expresion(self, p):
        return Booleano(valor=p.BOOL_CONST)

    @_('OBJECTID')
    def expresion(self, p):
        return Objeto(nombre=p.OBJECTID)
    

    # Manejo de errores
    def error(self, p):
        if p:
            print(f"Error de sintaxis: token inesperado '{p.value}' en línea {p.lineno}")
            self.errores.append(f"Error de sintaxis: token inesperado '{p.value}' en línea {p.lineno}")
            self.errok()
        else:
            print("Error de sintaxis: fin inesperado del archivo")
            self.errores.append("Error de sintaxis: fin inesperado del archivo")