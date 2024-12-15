import os
from Lexer import CoolLexer
from Parser import CoolParser

def test_lexer(file_path):
    """
    Prueba el lexer leyendo el archivo especificado y mostrando los tokens generados.
    """
    try:
        with open(file_path, 'r') as f:
            test_content = f.read()
        
        # Crear instancia del lexer
        lexer = CoolLexer()
        tokens = lexer.salida(test_content)
        
        # Mostrar tokens
        print(f"Tokens para {os.path.basename(file_path)}:")
        for token in tokens:
            print(token)
        print("\n" + "=" * 50 + "\n")
        return tokens  # Opcional: devolver tokens para depuración
    except Exception as e:
        print(f"Error al procesar el lexer para {file_path}: {e}")
        return None

def test_parser(file_path):
    """
    Prueba el parser usando el contenido del archivo especificado.
    """
    try:
        with open(file_path, 'r') as f:
            test_content = f.read()
        
        # Crear instancias de lexer y parser
        lexer = CoolLexer()
        parser = CoolParser()
        CoolParser.nombre_fichero = file_path  # Configurar el nombre del archivo para el parser
        
        # Obtener el resultado del parser
        ast = parser.parse(lexer.tokenize(test_content))
        
        # Mostrar el AST resultante
        print(f"AST para {os.path.basename(file_path)}:")
        print(ast)
        print("\n" + "=" * 50 + "\n")
        return ast  # Opcional: devolver AST para depuración
    except Exception as e:
        print(f"Error al procesar el parser para {file_path}: {e}")
        return None

def process_directory(base_dir, folder, test_function):
    """
    Procesa un directorio con subcarpetas y aplica una función de prueba a cada archivo .test.cool.
    """
    full_dir = os.path.join(base_dir, folder)
    test_dirs = ['grading', 'minimos']

    for test_dir in test_dirs:
        test_dir_path = os.path.join(full_dir, test_dir)
        print(f"Checking {test_dir_path}")

        # Verificar si el directorio existe
        if not os.path.exists(test_dir_path):
            print(f"Directory not found: {test_dir_path}")
            continue

        # Procesar archivos .test.cool
        for filename in os.listdir(test_dir_path):
            if filename.endswith('.test.cool'):
                file_path = os.path.join(test_dir_path, filename)
                print(f"Processing {os.path.basename(file_path)}")
                test_function(file_path)

def main():
    # Obtener el directorio base del script actual
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Procesar tests para el lexer (en carpeta 01)
    print(">>> Running Lexer Tests <<<")
    process_directory(base_dir, "01", test_lexer)
    
    # Procesar tests para el parser (en carpeta 02)
    print(">>> Running Parser Tests <<<")
    process_directory(base_dir, "02", test_parser)

if __name__ == '__main__':
    main()
