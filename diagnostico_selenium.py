import sys
import time

def test_selenium():
    print("Iniciando teste de diagnóstico Bionexo Bot...")
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        print("✔ Bibliotecas Selenium e Webdriver-manager instaladas.")
    except ImportError as e:
        print(f"✘ Erro: Bibliotecas faltando. Execute 'pip install selenium webdriver-manager'. Detalhe: {e}")
        return

    try:
        print("Tentando baixar/instalar o ChromeDriver...")
        chrome_options = Options()
        chrome_options.add_argument("--headless") # Teste silencioso
        chrome_options.add_argument("--no-sandbox")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("Tentando acessar o Google para validar conexão...")
        driver.get("https://www.google.com")
        print(f"✔ Sucesso! Título da página: {driver.title}")
        
        driver.quit()
        print("\nO Selenium está funcionando perfeitamente em sua máquina.")
    except Exception as e:
        print(f"\n✘ ERRO CRÍTICO: Não foi possível iniciar o Chrome. Detalhes:")
        print(str(e))
        print("\nCertifique-se de que o Google Chrome está instalado no seu computador.")

if __name__ == "__main__":
    test_selenium()
