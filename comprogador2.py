import os
import sys
from Lexer import CoolLexer

def test_lexer(file_path):
    # Read the test file content
    with open(file_path, 'r') as f:
        test_content = f.read()
    
    # Create lexer instance
    lexer = CoolLexer()
    
    # Get lexer output
    try:
        output = lexer.salida(test_content)
        
        # Print each token
        print(f"Tokens for {os.path.basename(file_path)}:")
        for token in output:
            print(token)
        print("\n" + "="*50 + "\n")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def main():
    # Get the directory of the current script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Potential test directories
    test_dirs = ['grading', 'minimos']
    
    # Iterate through potential test directories
    for test_dir in test_dirs:
        full_test_dir = os.path.join(base_dir,"01", test_dir)
        print(f"Checking {full_test_dir}")

        # Check if directory exists
        if not os.path.exists(full_test_dir):
            print(f"Directory not found: {full_test_dir}")
            continue
        
        # Find and process .test files
        for filename in os.listdir(full_test_dir):
            if filename.endswith('.test.cool'):
                file_path = os.path.join(full_test_dir, filename)
                print(f"Processing {os.path.basename(file_path)}")
                test_lexer(file_path)

if __name__ == '__main__':
    main()