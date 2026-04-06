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

    def login_manual(self):
        """Abre o site e espera o usuário logar manualmente."""
        if not self.driver:
            if not self._inicializar_driver(headless=False): # Força visível
                return None
        
        self.driver.maximize_window()
        self.driver.get("https://www.bionexo.com/")
        self.log("Aguardando LOGIN MANUAL no navegador...", "aviso")
        self.log("Por favor, faça o login e entre no painel principal.", "info")
        
        # Loop de espera (máximo 10 minutos)
        for i in range(600):
            try:
                curr_url = self.driver.current_url
                # Se não estamos nas telas de login/asgardeo e estamos no domínio bionexo:
                # O painel pode ser bionexo.bionexo.com ou revolution.bionexo.com
                if "bionexo.com" in curr_url and not any(x in curr_url for x in ["login.", "auth.", "asgardeo", "accounts.", "index3.jsp"]):
                    self.log("Login manual detectado com sucesso!", "ok")
                    return self.driver
            except:
                pass
            time.sleep(1)
        
        self.log("Tempo limite para login manual excedido.", "erro")
        return None

    def login(self, headless=True):
        if self.driver:
            # Verifica se já estamos logados em uma sessão ativa
            try:
                curr_url = self.driver.current_url
                if "bionexo.com" in curr_url and not any(x in curr_url for x in ["login.", "auth.", "asgardeo", "accounts.", "index3.jsp"]):
                    self.log("Sessão ativa detectada. Mantendo conexão aberta.", "ok")
                    return self.driver
            except:
                pass

        if not self.driver:
            if not self._inicializar_driver(headless):
                return None

        self.driver.maximize_window()

        try:
            # 1. Inicia pela Home
            self.log("Acessando Bionexo (bionexo.com)...", "info")
            self.driver.get("https://www.bionexo.com/")
            
            # 2. Clica no botão de Login da Home
            try:
                btn_login_home = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a[class*='buttons_login']")))
                btn_login_home.click()
                self.log("Clicado no botão Login da Home.", "info")
            except:
                self.log("Botão de login da home não encontrado, tentando URL direta...", "aviso")
                self.driver.get("https://login.bionexo.com/")

            # 3. Preenche login na Asgardeo
            self.log("Aguardando formulário de login (Asgardeo)...", "info")
            
            username_field = self.wait.until(EC.element_to_be_clickable((By.ID, "usernameUserInput")))
            username_field.clear()
            username_field.send_keys(self.config.get("email", ""))
            
            password_field = self.wait.until(EC.element_to_be_clickable((By.ID, "password")))
            password_field.clear()
            password_field.send_keys(self.config.get("senha", ""))
            
            btn_entrar = self.wait.until(EC.element_to_be_clickable((By.ID, "sign-in-button")))
            btn_entrar.click()
            self.log("Credenciais enviadas.", "info")

            # 4. Trata tela de "Acessar Portal" (se aparecer)
            time.sleep(5) 
            if "Acessar Portal" in self.driver.page_source or "Acessar" in self.driver.page_source:
                self.log("Detectada tela de seleção de portal. Tentando entrar...", "info")
                try:
                    btn_acessar = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Acessar') or contains(text(), 'Portal')] | //a[contains(text(), 'Acessar') or contains(text(), 'Portal')]")
                    btn_acessar.click()
                except:
                    self.log("Não foi possível clicar no botão 'Acessar Portal' automaticamente.", "aviso")

            # 5. Aguarda chegar na plataforma real
            self.wait.until(lambda d: "bionexo.com" in d.current_url and "login" not in d.current_url)
            
            self.log("Login realizado e portal acessado!", "ok")
            return self.driver

        except Exception as e:
            self.log(f"Erro no fluxo de login: {e}", "erro")
            self.driver.save_screenshot("erro_login.png")
            self.fechar()
            return None

    def buscar_cotacoes(self):
        try:
            self.log("Buscando cotações no painel...", "info")
            
            # Tenta encontrar o link de cotações no menu
            try:
                # Espera o menu estar visível e pronto
                self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(5) # Delay para React carregar o menu

                seletores_menu = [
                    "//a[contains(text(), 'Cotações')]",
                    "//span[contains(text(), 'Cotações')]",
                    "//a[contains(text(), 'Mercado')]",
                    "//a[contains(@href, 'cotacoes')]",
                    "//li[contains(@class, 'menu')]//span[contains(text(), 'Cotações')]"
                ]
                
                link_cotacoes = None
                for selector in seletores_menu:
                    try:
                        link_cotacoes = self.driver.find_element(By.XPATH, selector)
                        if link_cotacoes and link_cotacoes.is_displayed(): 
                            break
                        else:
                            link_cotacoes = None
                    except: continue
                
                if link_cotacoes:
                    self.driver.execute_script("arguments[0].click();", link_cotacoes)
                    self.log("Menu 'Cotações' acessado via script.", "info")
                else:
                    self.log("Aba de cotações não identificada no menu. Tentando detecção na página atual.", "info")
            except Exception as e:
                self.log(f"Falha na navegação: {e}", "aviso")

            # Aguarda o carregamento dos itens (específico para Revolution e Legacy)
            time.sleep(8) 
            
            # Seletores amplos para suportar tabelas ou grids
            seletores_itens = [
                "//tr[contains(@class, 'grid-row')]",
                "//div[contains(@class, 'opportunity')]",
                "//div[contains(@class, 'cotacao')]",
                "//*[contains(@class, 'card-') and contains(@class, 'cotacao')]",
                "//table//tr[position() > 1]"
            ]
            
            elementos = []
            for selector in seletores_itens:
                items = self.driver.find_elements(By.XPATH, selector)
                if len(items) > 0:
                    elementos = items
                    self.log(f"Itens detectados via seletor: {selector}", "info")
                    break
            
            cotacoes = []
            for el in elementos:
                try:
                    # Tenta extrair ID de vários atributos comuns
                    cid = el.get_attribute("id") or el.get_attribute("data-id") or el.get_attribute("aria-label")
                    if cid and len(str(cid)) > 5: # Um ID real costuma ser longo
                        cotacoes.append({"id": cid, "itens": []})
                except:
                    continue
            
            # Se não encontrou nada pelo ID, mas tem elementos, tenta pegar o texto
            if not cotacoes and len(elementos) > 0:
                self.log("Detectados elementos sem ID, usando contador como referência.", "aviso")
                for i in range(len(elementos)):
                    cotacoes.append({"id": f"temp_{i}", "itens": []})

            self.log(f"Encontradas {len(cotacoes)} possíveis cotações.", "info")
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
