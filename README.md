# 🤖 Bionexo Bot — Automação de Cotações

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Selenium](https://img.shields.io/badge/Selenium-WebDriver-green?logo=selenium)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

Robô de automação para fornecedores da plataforma **Bionexo**, que monitora cotações em aberto e responde automaticamente com base no catálogo de produtos do fornecedor.

---

## Como funciona

O bot usa **Selenium WebDriver** para acessar o portal Bionexo (BioID), navegar pelas cotações abertas e preencher propostas automaticamente, replicando as ações de um operador humano.

O matching entre o item solicitado e o catálogo do fornecedor é feito em três níveis:
1. **Match exato** — descrição idêntica
2. **Match por código** — código interno igual
3. **Match por palavras-chave** — ≥65% das palavras do item pedido estão na descrição do produto

---

## Funcionalidades

- Interface gráfica (customtkinter) — sem necessidade de linha de comando
- Importação de catálogo via Excel ou CSV com detecção automática de colunas
- Configuração de margem percentual sobre os preços
- Varredura periódica configurável (padrão: 10 minutos)
- Log de execuções em tempo real
- Compatível com Windows, macOS e Linux

---

## Stack

| Camada | Tecnologia |
|---|---|
| Automação web | Selenium + webdriver-manager |
| Interface gráfica | customtkinter |
| Leitura de planilhas | openpyxl |
| Linguagem | Python 3.8+ |

---

## Como rodar
```bash
# Opção rápida (instala dependências e abre o app)
python instalar_e_rodar.py

# Ou manualmente
pip install customtkinter openpyxl selenium webdriver-manager
python bionexo_bot.py
```

> Requer Google Chrome instalado. O ChromeDriver é gerenciado automaticamente.

---

## Estrutura do projeto
```
├── bionexo_bot.py          # Interface gráfica principal
├── bionexo_engine.py       # Lógica de matching e execução
├── bionexo_api.py          # Automação Selenium (login, navegação)
├── bionexo_data.py         # Gestão do catálogo e configurações
├── instalar_e_rodar.py     # Script de instalação automática
└── diagnostico_selenium.py # Ferramenta de diagnóstico
```
