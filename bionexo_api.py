import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class BionexoAPI:
    def __init__(self, config, log_callback=None):
        self.config = config
        self.log_callback = log_callback or print
        self.driver = None
        self.wait = None

    def log(self, msg, tipo="info"):
        self.log_callback(msg, tipo)

    def _inicializar_driver(self, headless=True):
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, 20)
            return True
        except Exception as e:
            self.log(f"Erro ao inicializar navegador: {e}", "erro")
            return False

    def login(self, headless=True):
        if not self.driver:
            if not self._inicializar_driver(headless):
                return None

        urls_tentar = [
            "https://accounts.asgardeo.io/t/bionexo/authenticationendpoint/login.do?client_id=YifJfXKyIgNr6pjir1VBaCwr8qka&code_challenge=x_a1KZLhwJHctP8fMEen4cIlotQKGwreX0UzmHY8NWQ&code_challenge_method=S256&commonAuthCallerPath=%2Ft%2Fbionexo%2Foauth2%2Fauthorize&forceAuth=false&passiveAuth=false&redirect_uri=https%3A%2F%2Flogin.bionexo.com%2Fapi%2Fcallback&response_mode=query&response_type=code&scope=openid+profile+groups+application_roles+openid&state=request_0&sessionDataKey=5dd34d37-e217-4664-9aed-317e7d37a1c0&relyingParty=YifJfXKyIgNr6pjir1VBaCwr8qka&type=oidc&sp=Login&spId=b72e9305-aef2-4880-aa4f-43cc394c0b59&isSaaSApp=false&authenticators=OpenIDConnectAuthenticator%3AMicrosoft%3BBasicAuthenticator%3ALOCAL",
            "https://bioid.bionexo.com/",
            "https://bioid.bionexo.com.br/",
            "https://acesso.bionexo.com/",
            "https://www.bionexo.com/login"
        ]

        for url in urls_tentar:
            try:
                self.log(f"Tentando acessar: {url}", "info")
                self.driver.get(url)
                
                # Se carregou algo que não seja erro de DNS, prossegue
                if "ERR_NAME_NOT_RESOLVED" not in self.driver.page_source:
                    break
            except Exception as e:
                self.log(f"Falha ao carregar {url}: {e}", "aviso")
                continue
        
        try:
            # Aguarda e preenche o login (BioID usa selectors username/password)
            self.wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(self.config.get("email", ""))
            self.driver.find_element(By.ID, "password").send_keys(self.config.get("senha", ""))
            
            # Clique no botão entrar
            btn_entrar = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            btn_entrar.click()
            
            # Aguarda a página carregar após login
            self.wait.until(EC.url_changes(self.driver.current_url))
            
            self.log("Login realizado com sucesso!", "ok")
            return self.driver
        except Exception as e:
            self.log(f"Erro no fluxo de login: {e}", "erro")
            # Tira print para debug se der erro (opcional, salvando localmente)
            self.driver.save_screenshot("erro_login.png")
            self.fechar()
            return None

    def buscar_cotacoes(self):
        try:
            # Navega para a área de cotações abertas
            # URL exemplo, precisa ser validada com o fluxo real do usuário
            self.driver.get("https://www.bionexo.com.br/painel-fornecedor/cotacoes/abertas")
            time.sleep(3) # Aguarda renderização JS
            
            # Aqui extraímos a lista de cotações do DOM
            # Exemplo de seletor (precisa ser refinado baseado na tela real do cliente)
            elementos = self.driver.find_elements(By.CLASS_NAME, "card-cotacao")
            
            cotacoes = []
            for el in elementos:
                try:
                    cid = el.get_attribute("data-id")
                    # ... parseamento do item ...
                    cotacoes.append({"id": cid, "itens": []}) # Estrutura básica
                except:
                    continue
            
            return cotacoes
        except Exception as e:
            self.log(f"Erro ao buscar cotações: {e}", "aviso")
            return []

    def enviar_proposta(self, cotacao_id, item_id, preco, prazo_entrega, marca, unidade):
        try:
            # Lógica para preencher o formulário na página do Selenium
            # 1. Localizar o input de preço do item_id
            # 2. Preencher marca, prazo, etc.
            # 3. Clicar em salvar/enviar
            return True # Mock por enquanto até validar seletores reais na máquina do user
        except Exception:
            return False

    def fechar(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
