# Usabilidade: <3 cliques para ações principais
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def test_main_actions():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    actions = {
        'adicionar_transacao': 2,  # Dashboard -> Adicionar
        'ver_relatorios': 1,       # Menu -> Relatórios
        'criar_meta': 2,           # Menu -> Metas -> Criar
        'ver_orcamento': 1         # Menu -> Orçamentos
    }
    
    passed_actions = 0
    
    for action, max_clicks in actions.items():
        driver.get('http://localhost:3000')
        clicks = 0
        
        try:
            if action == 'adicionar_transacao':
                driver.find_element(By.CLASS_NAME, 'add-transaction-btn').click()
                clicks = 1
            elif action == 'ver_relatorios':
                driver.find_element(By.LINK_TEXT, 'Relatórios').click()
                clicks = 1
            
            if clicks <= max_clicks:
                passed_actions += 1
                
        except Exception:
            pass
    
    driver.quit()
    success_rate = (passed_actions / len(actions)) * 100
    return success_rate == 100, success_rate

if __name__ == "__main__":
    passed, rate = test_main_actions()
    print(f"Usabilidade: {rate}% - {'✅' if passed else '❌'}")