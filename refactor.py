import re

with open('bionexo_bot.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 1. doc string
for i, l in enumerate(lines):
    if 'pip install customtkinter openpyxl pandas playwright requests' in l:
        lines[i] = '    pip install customtkinter openpyxl\n'
        break

# 2. HAS_PANDAS
start_idx = -1
end_idx = -1
for i, l in enumerate(lines):
    if 'try:' in l and i+1 < len(lines) and 'import pandas as pd' in lines[i+1]:
        start_idx = i
    if start_idx != -1 and 'HAS_PANDAS = False' in l:
        end_idx = i
        break
if start_idx != -1:
    del lines[start_idx:end_idx+1]

# 3. Imports
for i, l in enumerate(lines):
    if 'import webbrowser' in l:
        lines[i] = 'from bionexo_data import DataManager\nfrom bionexo_engine import BionexoBotEngine\n'
        break

# 4. config functions
start_idx = -1
end_idx = -1
for i, l in enumerate(lines):
    if 'def carregar_config():' in l:
        start_idx = i
    if start_idx != -1 and 'def salvar_config(cfg):' in l:
        # find end of salvar conf
        for j in range(i, i+50):
            if 'json.dump(' in lines[j]:
                end_idx = j
                break
if end_idx != -1:
    del lines[start_idx:end_idx+1]

# 5. init
for i, l in enumerate(lines):
    if 'self.config = carregar_config()' in l:
        lines[i] = '''        self.config = DataManager.carregar_config()
        callbacks = {
            "log": self._log,
            "metric_add": self._atualizar_metrica,
            "finish_cycle": self._bionexo_engine_finish
        }
        self.engine = BionexoBotEngine(self.config, self.catalogo, callbacks)
'''
        break

# 6. salvar na ui
for i, l in enumerate(lines):
    if 'salvar_config(self.config)' in l:
        lines[i] = l.replace('salvar_config', 'DataManager.salvar_config')

# 7. data mgr historico load
for i, l in enumerate(lines):
    if 'with open("bionexo_historico.json", "r", encoding="utf-8") as f:' in l:
         lines[i] = lines[i].replace('with open', '# with open')
    if 'hist = json.load(f)' in lines[i]:
         lines[i] = lines[i].replace('hist = json.load(f)', 'hist = DataManager.carregar_historico()')
    if 'os.remove("bionexo_historico.json")' in lines[i]:
         lines[i] = '                DataManager.limpar_historico()\n'

# 8. engine block delete
start_idx = -1
end_idx = -1
for i, l in enumerate(lines):
    if 'def _iniciar_bot(self):' in l:
        start_idx = i
    if 'def _build_pagina_historico(self):' in l:
        end_idx = i - 1
        break

if start_idx != -1 and end_idx != -1:
    print(f'Deleting engine block from {start_idx} to {end_idx}')
    lines[start_idx:end_idx+1] = ['''
    def _bionexo_engine_finish(self):
        self.after(0, lambda: self._set_estado_bot(False))

    def _iniciar_bot(self):
        if not self._validar_pre_inicio():
            return
        self._set_estado_bot(True)
        self.thread_bot = threading.Thread(target=self.engine.iniciar, daemon=True)
        self.thread_bot.start()

    def _parar_bot(self):
        self.engine.parar()
        self._set_estado_bot(False)
        self._log("Robô parado pelo usuário.", "aviso")

    def _rodar_agora(self):
        if not self._validar_pre_inicio():
            return
        self._log("▶ Execução manual iniciada...")
        threading.Thread(target=self.engine.testar_uma_vez, daemon=True).start()

''']

with open('bionexo_bot.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done!')
