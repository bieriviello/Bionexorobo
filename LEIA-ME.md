# BIONEXO BOT — Guia Rápido

Sistema de automação de cotações para fornecedores da Bionexo.
Interface gráfica em Python, roda no Windows, Mac e Linux.
**Não precisa instalar nada além do Python.**

---

## Como rodar

### Opção 1 — Automático (recomendado)
Dê dois cliques em `instalar_e_rodar.py`
ou execute:
```
python instalar_e_rodar.py
```
Ele instala o que falta e abre o programa.

### Opção 2 — Manual
```
pip install customtkinter openpyxl
python bionexo_bot.py
```

---

## Primeiros passos no app

### 1. Importe seu catálogo (aba "Catálogo")
- Clique em **+ Importar Excel / CSV**
- Selecione sua planilha com os produtos
- O sistema detecta as colunas automaticamente
- Use o filtro por palavra-chave para localizar produtos

**Colunas reconhecidas automaticamente:**
| Coluna | Nomes aceitos |
|--------|--------------|
| Descrição | descricao, produto, item, material, nome |
| Código | codigo, cod, ref, sku, referencia |
| Preço | preco, valor, price, custo |
| Prazo | prazo, entrega, lead, dias |
| Marca | marca, fabricante, brand |
| Unidade | unidade, un, unit |
| Estoque | estoque, qtd, saldo, stock |
| Ativo | ativo, status, habilitado |

### 2. Configure suas credenciais (aba "Configurações")
- E-mail e senha da Bionexo
- CNPJ da sua empresa
- Margem extra opcional (ex: 5 = sobe 5% nos preços)
- Intervalo de varredura (padrão: 10 minutos)

### 3. Teste e ative o robô (aba "Robô")
- Clique em **⚡ Rodar uma vez agora** para testar
- Acompanhe o log em tempo real
- Se funcionar, clique **▶ Iniciar robô** para modo contínuo

---

## Como o robô encontra os produtos

1. **Match exato** — descrição idêntica
2. **Match por código** — código interno igual
3. **Match por palavras-chave** — 65% das palavras do item pedido aparecem na descrição do seu produto

Dica: quanto mais detalhada a descrição, melhor o match.

---

## Arquivos gerados pelo sistema

| Arquivo | Conteúdo |
|---------|----------|
| `bionexo_config.json` | Suas configurações salvas |
| `bionexo_historico.json` | Log de todas as execuções |

---

## Requisitos

- Python 3.8 ou superior
- Windows 10/11, macOS 11+ ou Linux
- Conexão com a internet
- Conta ativa de fornecedor na Bionexo

---

## Observação importante

O robô acessa o portal da Bionexo via requisições HTTP diretas.
Se a Bionexo atualizar a estrutura do portal, os endpoints podem
precisar de ajuste. Nesse caso, verifique o log de erros e
atualize as URLs na função `_login_bionexo` e `_buscar_cotacoes`.

Para a versão com API oficial (mais estável), entre em contato
com a Bionexo pelo e-mail: integracao@bionexo.com
