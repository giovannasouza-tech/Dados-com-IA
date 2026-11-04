"""Roda a demonstração inteira: gera o ERP fictício, carrega, relata e valida."""
import subprocess
import sys

for passo in ["carga/gerar_dados_ficticios.py", "carga/carregar.py",
              "relatorio/gerar_relatorio.py", "automacoes/validar_sellout.py"]:
    print(f"\n=== {passo} ===")
    subprocess.run([sys.executable, passo])
