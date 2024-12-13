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
        full_test_dir = os.path.join(base_path, test_dir)
        
        # Find .test files
        for filename in os.listdir(full_test_dir):
            if filename.endswith('.test'):
                test_path = os.path.join(full_test_dir, filename)
                out_path = os.path.join(full_test_dir, filename.replace('.test', '.out'))
                
                # Read test file
                with open(test_path, 'r') as f:
                    test_content = f.read()
                
                # Read expected output
                with open(out_path, 'r') as f:
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
                
                # Compare actual and expected output
                with open(results_file_path, 'w') as f:
                    f.write("Actual Output:\n")
                    f.write('\n'.join(actual_output) + '\n\n')
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

if __name__ == '__main__':
    # Assuming the script is in the /01 directory
    base_path = os.path.dirname(os.path.abspath(__file__))
    run_lexer_tests(base_path)