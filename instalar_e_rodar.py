#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════╗
║       BIONEXO BOT — Instalador / Launcher    ║
╚══════════════════════════════════════════════╝

Execute este arquivo para instalar as dependências
e abrir o Bionexo Bot automaticamente.

    python instalar_e_rodar.py
"""
import subprocess
import sys
import os

DEPS = ["customtkinter", "openpyxl"]

def verificar_e_instalar(pacotes):
    print("\n╔══════════════════════════════════════════════╗")
    print("║       BIONEXO BOT — Configuração inicial     ║")
    print("╚══════════════════════════════════════════════╝")
    print()

    for pacote in pacotes:
        try:
            __import__(pacote.replace("-", "_"))
            print(f"  ✔ {pacote} já instalado")
        except ImportError:
            print(f"  → Instalando {pacote}...", end=" ", flush=True)
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", pacote, "--quiet"],
                capture_output=True
            )
            if result.returncode == 0:
                print("OK")
            else:
                print(f"ERRO\n\n  Tente manualmente: pip install {pacote}")
                sys.exit(1)

    print()
    print("  Todas as dependências prontas. Iniciando o app...")
    print()

    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bionexo_bot.py")
    os.execv(sys.executable, [sys.executable, script])


if __name__ == "__main__":
    verificar_e_instalar(DEPS)
