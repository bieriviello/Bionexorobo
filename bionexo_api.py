import urllib.request
import urllib.parse
import urllib.error
import json

class BionexoAPI:
    def __init__(self, config, log_callback=None):
        self.config = config
        self.log_callback = log_callback or print

    def log(self, msg, tipo="info"):
        self.log_callback(msg, tipo)

    def login(self):
        try:
            dados = urllib.parse.urlencode({
                "login": self.config.get("email", ""),
                "senha": self.config.get("senha", ""),
                "cnpj":  self.config.get("cnpj", "").replace(".", "").replace("/", "").replace("-", ""),
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://www.bionexo.com/login",
                data=dados,
                headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/x-www-form-urlencoded"},
            )
            req.add_unredirected_header("Cookie", "")

            opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
            resp = opener.open(req, timeout=15)

            cookie_header = resp.headers.get("Set-Cookie", "")
            if cookie_header:
                return {"cookie": cookie_header, "opener": opener}

            all_cookies = [v for k, v in resp.headers.items() if k.lower() == "set-cookie"]
            if all_cookies:
                return {"cookie": "; ".join(all_cookies), "opener": opener}

            return None
        except Exception as e:
            self.log(f"  Erro de conexão: {e}", "erro")
            return None

    def buscar_cotacoes(self, sessao):
        try:
            req = urllib.request.Request(
                "https://www.bionexo.com/wss/cotacao/fornecedor/abertas",
                headers={
                    "Cookie": sessao["cookie"],
                    "Accept": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                    "User-Agent": "Mozilla/5.0",
                },
            )
            resp = sessao["opener"].open(req, timeout=15)
            dados = json.loads(resp.read().decode("utf-8"))
            return dados if isinstance(dados, list) else dados.get("cotacoes", dados.get("data", []))
        except Exception as e:
            self.log(f"  Erro ao buscar cotações: {e}", "aviso")
            return []

    def enviar_proposta(self, sessao, cotacao_id, item_id, preco, prazo_entrega, marca, unidade):
        try:
            payload = json.dumps({
                "cotacaoId": cotacao_id,
                "itemId":    item_id,
                "preco":     round(preco, 2),
                "prazoEntrega": prazo_entrega,
                "marca":     marca or "Conforme especificação",
                "unidade":   unidade,
            }).encode("utf-8")

            req = urllib.request.Request(
                "https://www.bionexo.com/wss/cotacao/responder",
                data=payload,
                headers={
                    "Cookie": sessao["cookie"],
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                    "User-Agent": "Mozilla/5.0",
                },
            )
            resp = sessao["opener"].open(req, timeout=10)
            return resp.status in (200, 201)
        except Exception:
            return False
