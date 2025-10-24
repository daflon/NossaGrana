# Performance <2s carregamento inicial
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def check_performance():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    
    start_time = time.time()
    driver.get('http://localhost:3000')
    
    # Aguarda carregamento completo
    driver.implicitly_wait(5)
    load_time = time.time() - start_time
    
    driver.quit()
    return load_time < 2.0, load_time

if __name__ == "__main__":
    passed, load_time = check_performance()
    print(f"Carregamento: {load_time:.2f}s - {'✅' if passed else '❌'}")