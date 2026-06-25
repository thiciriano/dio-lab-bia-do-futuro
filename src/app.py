#!/usr/bin/env python3
"""
Interface de chat para MILA - Miniatura de Gastos Inteligente
Permite conversa interativa com o assistente de microdespesas
"""

import sys
import os

# Adiciona src ao path para importar módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.mila import MILA

def limpar_tela():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def imprimir_banner():
    """Imprime o banner inicial"""
    print("\n" + "="*50)
    print("🤖 MILA - Miniatura de Gastos Inteligente")
    print("💰 Assistente de Microdespesas")
    print("="*50)
    print("\nOlá! 👋 Sou MILA, seu assistente para controlar")
    print("aqueles pequenos gastos que se acumulam.")
    print("\nO que você pode fazer:")
    print("  • Registrar um gasto: 'Gastei R$5 com café'")
    print("  • Ver resumo: 'Quanto gastei?'")
    print("  • Sugestões: 'Como economizar?'")
    print("  • Resumo completo: 'Resumo'")
    print("  • Sair: 'Sair' ou 'exit'")
    print("\n" + "-"*50 + "\n")

def main():
    """Função principal - loop de chat"""
    limpar_tela()
    imprimir_banner()
    
    # Inicializa MILA
    try:
        mila = MILA(data_dir='data')
        print("✅ MILA carregada com sucesso!\n")
    except Exception as e:
        print(f"❌ Erro ao carregar MILA: {e}")
        sys.exit(1)
    
    # Loop de conversa
    while True:
        try:
            usuario_input = input("Você: ").strip()
            
            if not usuario_input:
                continue
            
            # Comandos especiais
            if usuario_input.lower() in ['sair', 'exit', 'quit']:
                print("\n👋 Até logo! Que seus gastos sejam menores! 💰")
                break
            
            if usuario_input.lower() == 'resumo':
                print(f"\nMILA: \n{mila.obter_resumo()}")
                print("-"*50 + "\n")
                continue
            
            # Processa mensagem normal
            resposta = mila.processar_mensagem(usuario_input)
            print(f"\nMILA: {resposta}\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Conversa interrompida. Até logo!")
            break
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            print("Tenta de novo!\n")

if __name__ == "__main__":
    main()
