# Cobertura de Testes >80%
import subprocess
import re

def check_coverage():
    result = subprocess.run(['python', '-m', 'pytest', '--cov=.', '--cov-report=term'], 
                          capture_output=True, text=True, cwd='../backend')
    
    match = re.search(r'TOTAL.*?(\d+)%', result.stdout)
    coverage = int(match.group(1)) if match else 0
    
    return coverage >= 80, coverage

if __name__ == "__main__":
    passed, percent = check_coverage()
    print(f"Cobertura: {percent}% - {'✅' if passed else '❌'}")