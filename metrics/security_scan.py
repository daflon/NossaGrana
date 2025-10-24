# Segurança: 0 vulnerabilidades críticas
import subprocess
import json

def check_security():
    # Executa bandit para análise de segurança
    result = subprocess.run(['bandit', '-r', '../backend', '-f', 'json'], 
                          capture_output=True, text=True)
    
    if result.stdout:
        data = json.loads(result.stdout)
        critical_issues = [issue for issue in data.get('results', []) 
                          if issue.get('issue_severity') == 'HIGH']
        return len(critical_issues) == 0, len(critical_issues)
    
    return True, 0

if __name__ == "__main__":
    passed, issues = check_security()
    print(f"Vulnerabilidades críticas: {issues} - {'✅' if passed else '❌'}")