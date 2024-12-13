import os
import sys
import difflib

# Ensure the lexer is imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Lexer import CoolLexer

def run_lexer_tests(base_path):
    # Create results directory if it doesn't exist
    results_dir = os.path.join(base_path, 'results')
    os.makedirs(results_dir, exist_ok=True)

    # Directories to check
    test_dirs = ['grading', 'minimos']

    # Iterate through test directories
    for test_dir in test_dirs:
        full_test_dir = os.path.join(base_path, "01", test_dir)
        
        # Skip if directory doesn't exist
        if not os.path.exists(full_test_dir):
            print(f"Directory not found: {full_test_dir}")
            continue
        
        # Find .test files
        for filename in os.listdir(full_test_dir):
            if filename.endswith('.test'):
                test_path = os.path.join(full_test_dir, filename)
                out_path = os.path.join(full_test_dir, filename.replace('.test', '.out'))
                
                # Ensure output file exists for expected output
                if not os.path.exists(out_path):
                    print(f"No corresponding .out file for {filename}")
                    continue
                
                # Read test file
                with open(test_path, 'r', encoding='utf-8') as f:
                    test_content = f.read()
                
                # Read expected output
                with open(out_path, 'r', encoding='utf-8') as f:
                    expected_output = f.read().strip().split('\n')
                
                # Run lexer
                lexer = CoolLexer()
                try:
                    actual_output = lexer.salida(test_content)
                except Exception as e:
                    print(f"Error processing {filename}: {e}")
                    continue
                
                # Create results file
                results_filename = f"{filename.replace('.test', '')}-[out].txt"
                results_file_path = os.path.join(results_dir, results_filename)
                
                # Ensure results directory exists
                os.makedirs(os.path.dirname(results_file_path), exist_ok=True)
                
                # Compare actual and expected output
                with open(results_file_path, 'w', encoding='utf-8') as f:
                    # Write actual output
                    f.write("Actual Output:\n")
                    f.write('\n'.join(actual_output) + '\n\n')
                    
                    # Write expected output
                    f.write("Expected Output:\n")
                    f.write('\n'.join(expected_output) + '\n\n')
                    
                    # Diff analysis
                    diff = list(difflib.unified_diff(
                        actual_output, 
                        expected_output, 
                        fromfile='Actual', 
                        tofile='Expected'
                    ))
                    
                    if diff:
                        f.write("Differences Found:\n")
                        f.write('\n'.join(diff))
                    else:
                        f.write("No differences found. Test passed.")
                
                # Print status
                print(f"Processed {filename}: {'PASSED' if not diff else 'FAILED'}")
                print(f"Results written to {results_file_path}")

if __name__ == '__main__':
    # Assuming the script is in the project directory
    base_path = os.path.dirname(os.path.abspath(__file__))
    run_lexer_tests(base_path)