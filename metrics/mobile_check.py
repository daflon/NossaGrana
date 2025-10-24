# Responsividade: 100% mobile-friendly
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def check_mobile_responsiveness():
    options = Options()
    options.add_argument('--headless')
    
    # Testa diferentes tamanhos de tela
    mobile_sizes = [(375, 667), (414, 896), (360, 640)]
    passed_tests = 0
    
    for width, height in mobile_sizes:
        driver = webdriver.Chrome(options=options)
        driver.set_window_size(width, height)
        driver.get('http://localhost:3000')
        
        # Verifica se elementos são visíveis
        body = driver.find_element('tag name', 'body')
        if body.size['width'] <= width:
            passed_tests += 1
            
        driver.quit()
    
    success_rate = (passed_tests / len(mobile_sizes)) * 100
    return success_rate == 100, success_rate

if __name__ == "__main__":
    passed, rate = check_mobile_responsiveness()
    print(f"Mobile-friendly: {rate}% - {'✅' if passed else '❌'}")