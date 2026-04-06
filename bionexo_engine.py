import time
import re
from bionexo_api import BionexoAPI
from bionexo_data import DataManager

class BionexoBotEngine:
    def __init__(self, config, catalogo, callbacks):
        self.config = config
        self.catalogo = catalogo
        # callbacks: log(msg, tipo), metric_add(name, val), finish_cycle()
        self.log = callbacks.get("log", lambda m, t: print(m))
        self.metric_add = callbacks.get("metric_add", lambda n, v: None)
        self.finish_cycle = callbacks.get("finish_cycle", lambda: None)
        
        self.api = BionexoAPI(config, log_callback=self.log)
        self.rodando = False

    def iniciar(self, manual=False):
        self.rodando = True
        self.manual_mode = manual
        intervalo = int(self.config.get("intervalo_min", 10)) * 60
        primeiro_ciclo = True
        
        while self.rodando:
            if not self._ciclo(manual=self.manual_mode):
                # Se o ciclo falhou (ex: login falhou), paramos o bot
                self.rodando = False
                break
            
            primeiro_ciclo = False
            # ... resto do loop ...
            if not self.rodando:
                break
            # Espera inteligente (pode ser interrompida)
            for _ in range(intervalo):
                if not self.rodando:
                    break
                time.sleep(1)

    def parar(self):
        self.rodando = False
        if self.api:
            self.api.fechar()

    def testar_uma_vez(self):
        self._ciclo()
        if self.api:
            self.api.fechar()

    def _ciclo(self, manual=False):
        self.log("─" * 45, "info")
        self.log(f"Iniciando ciclo de varredura ({'Manual' if manual else 'Auto'})...", "info")
        
        try:
            if manual:
                sessao_valida = self.api.login_manual()
            else:
                headless = self.config.get("navegador_visivel") != True
                self.log(f"Fazendo login via BioID (Visible={'No' if headless else 'Yes'})...", "info")
                sessao_valida = self.api.login(headless=headless)
            
            if not sessao_valida:
                self.log("Falha no login ou inicialização do navegador.", "erro")
                self.metric_add("erros", 1)
                DataManager.registrar_historico(0, 0, 0, "Falha no login/driver")
                self.finish_cycle()
                return False

            self.log("Navegador pronto e logado.", "ok")
            cotacoes = self.api.buscar_cotacoes()
            self.log(f"Cotações identificadas: {len(cotacoes)}", "info")

            if not cotacoes:
                self.log("Nenhuma cotação aberta encontrada no painel. Aguardando próximo ciclo...", "info")
                DataManager.registrar_historico(0, 0, 0, "Sem cotações")
                self.finish_cycle()
                return True

            total_resp = 0
            total_sem = 0

            for cotacao in cotacoes:
                if not self.rodando: break
                r, s = self._processar_cotacao(cotacao)
                total_resp += r
                total_sem += s

            self.metric_add("respondidas_hoje", total_resp)
            self.metric_add("sem_match", total_sem)
            self.log(f"Ciclo concluído — {total_resp} respondidos, {total_sem} sem match.", "ok")
            DataManager.registrar_historico(len(cotacoes), total_resp, total_sem, "OK")
            self.finish_cycle()
        except Exception as e:
            self.log(f"Erro crítico no ciclo: {e}", "erro")
            self.metric_add("erros", 1)
            DataManager.registrar_historico(0, 0, 0, f"Erro: {e}")
            self.finish_cycle()
        finally:
            # No modo manual, NUNCA fechamos o navegador automaticamente
            if not manual:
                self.api.fechar()

    def _processar_cotacao(self, cotacao):
        cid = cotacao.get("id") or "?"
        itens = cotacao.get("itens") or []
        respondidos = 0
        sem_match = 0

        self.log(f"  Analisando PDC {cid}: {len(itens)} itens", "info")
        self.metric_add("total_itens", len(itens))

        for item in itens:
            desc = str(item.get("descricao") or "").strip()
            if not desc: continue
            
            match = self._encontrar_produto(desc)
            if not match:
                self.log(f"    ✘ sem correspondência: {desc[:50]}", "info")
                sem_match += 1
                continue

            margem = float(self.config.get("margem", 0)) / 100
            preco_final = match["preco"] * (1 + margem)
            
            # Envia proposta via Selenium
            ok = self.api.enviar_proposta(
                cotacao.get("id"), 
                item.get("id"), 
                preco_final, 
                match["prazo"], 
                match["marca"], 
                match["unidade"]
            )

            if ok:
                self.log(f"    ✔ {match['descricao'][:40]} → R$ {preco_final:.2f}", "ok")
                respondidos += 1
            else:
                self.log(f"    ✘ falha no envio: {desc[:40]}", "erro")
                sem_match += 1

        return respondidos, sem_match

    def _encontrar_produto(self, descricao_item):
        desc_norm = descricao_item.lower().strip()
        ativos = [p for p in self.catalogo if p.get("ativo") == "SIM" and p.get("preco", 0) > 0]

        # 1. Match exato
        for p in ativos:
            if p["descricao"].lower() == desc_norm or (p.get("codigo") and p["codigo"].lower() == desc_norm):
                return p

        # 2. Match parcial por palavras-chave (Fuzzy leve)
        palavras = [w for w in re.sub(r"[^a-z0-9 ]", " ", desc_norm).split() if len(w) > 2]
        if not palavras: return None
            
        melhor, melhor_score = None, 0
        for p in ativos:
            haystack = re.sub(r"[^a-z0-9 ]", " ", p["descricao"].lower())
            score = sum(1 for w in palavras if w in haystack)
            pct = score / len(palavras)
            if pct >= 0.70 and score > melhor_score:
                melhor, melhor_score = p, score
        return melhor
