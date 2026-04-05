import os
import json
import datetime

CONFIG_FILE = "bionexo_config.json"
HISTORICO_FILE = "bionexo_historico.json"

class DataManager:
    @staticmethod
    def carregar_config():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "email": "",
            "senha": "",
            "cnpj": "",
            "margem": "0",
            "prazo_padrao": "3",
            "intervalo_min": "10",
            "notificar_email": False,
            "email_notificacao": "",
            "auto_rodar": False,
            "arquivo_catalogo": "",
        }

    @staticmethod
    def salvar_config(cfg):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)

    @staticmethod
    def registrar_historico(cotacoes, respondidos, sem_match, status):
        entrada = {
            "timestamp": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "cotacoes": cotacoes,
            "respondidos": respondidos,
            "sem_match": sem_match,
            "status": status,
        }
        try:
            hist = []
            if os.path.exists(HISTORICO_FILE):
                with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
                    hist = json.load(f)
            hist.insert(0, entrada)
            hist = hist[:500]
            with open(HISTORICO_FILE, "w", encoding="utf-8") as f:
                json.dump(hist, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    @staticmethod
    def salvar_catalogo(catalogo):
        with open("catalogo_cache.json", "w", encoding="utf-8") as f:
            json.dump(catalogo, f, ensure_ascii=False, indent=2)

    @staticmethod
    def carregar_catalogo_cache():
        if not os.path.exists("catalogo_cache.json"):
            return None
        try:
            with open("catalogo_cache.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    @staticmethod
    def carregar_historico():
        if not os.path.exists(HISTORICO_FILE):
            return []
        try:
            with open(HISTORICO_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    @staticmethod
    def limpar_historico():
        if os.path.exists(HISTORICO_FILE):
            try:
                os.remove(HISTORICO_FILE)
            except Exception:
                pass
