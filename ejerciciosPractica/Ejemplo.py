from sly import Lexer, Parser
from sly.yacc import _  # Import the underscore function



class EjemploLex(Lexer):
    tokens={'UNO', 'DOS', 'MAS', 'POR'}
    UNO = '1'
    DOS = '2'
    MAS = '\+'
    POR = '\*'
    


class EjemploParser(Parser):
    tokens=EjemploLex.tokens
    debugfile="salida.out"
    @_("E OP E")
    def E(self, p):
        pass
   
    @_("N")
    def E(self, p):
        pass

    @_("N D")
    def N(self, p):
        pass
    
    @_("D")
    def N(self, p):
        pass

    @_("UNO")
    def D(self, p):
        pass

    @_("DOS")
    def D(self, p):
        pass

    @_('MAS', 'POR')
    def OP(self, p):
        pass
        
