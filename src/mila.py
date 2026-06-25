import os
import json
from datetime import datetime
from typing import Dict, Tuple
import re

# Importações locais
try:
    from data_loader import DataLoader
    from analyzer import Analyzer
except ImportError:
    from src.data_loader import DataLoader
    from src.analyzer import Analyzer

class MILA:
    """Agente MILA - Miniatura de Gastos Inteligente e Lembrete de Ações"""
    
    SYSTEM_PROMPT = """Você é MILA, um assistente inteligente e amigável especializado em ajudar usuários a entender e gerenciar microdespesas.

### OBJETIVO PRINCIPAL
Ajudar o usuário a perceber, registrar e analisar pequenos gastos (até R$ 100) que se acumulam ao longo do tempo.

### PRINCÍPIOS FUNDAMENTAIS
1. SEMPRE baseie respostas nos dados fornecidos
2. NUNCA invente números ou gastos que não existem nos dados
3. Respostas CLARAS, DIRETAS e amigáveis
4. Se não souber algo, ADMITA e ofereça alternativa
5. SEMPRE confirme antes de registrar um novo gasto
6. Use emojis discretos

### REGRAS OPERACIONAIS

#### REGISTRAR GASTOS
Quando o usuário menciona um gasto:
1. Extraia: VALOR, DESCRIÇÃO, CATEGORIA (automática)
2. Confirme: "Correto? R$X em [CATEGORIA]?"
3. Se confirmado: "Anotado! ✅"
4. NUNCA registre sem confirmação explícita

#### CATEGORIAS
- 🍔 Alimentação: café, lanche, almoço, doce, refrigerante
- 🚗 Transporte: uber, taxi, ônibus, gasolina
- 🎮 Diversão: cinema, netflix, spotify, jogo
- 🏥 Saúde: farmácia, xampu, desodorante
- 📦 Outros: tudo mais

#### ANALISAR DADOS
Use APENAS dados do histórico. Nunca alucinhe números.

#### LIMITAÇÕES
Se o usuário perguntar fora de escopo, responda:
"Não consigo ajudar com [TEMA]. Mas posso analisar seus gastos!"

### TOM
Informal, otimista, prático. 1-2 emojis por mensagem máximo.
"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_loader = DataLoader(data_dir)
        self.analyzer = Analyzer(
            self.data_loader.transacoes,
            self.data_loader.config
        )
        self.historico_conversas = []
        self.gastos_pendentes = {}  # Para confirmar antes de registrar
    
    def processar_mensagem(self, mensagem: str) -> str:
        """Processa a mensagem do usuário e retorna resposta."""
        mensagem_lower = mensagem.lower().strip()
        
        # Detecta se é confirmação de gasto
        if self.gastos_pendentes:
            if mensagem_lower in ['sim', 's', 'ok', 'correto']:
                return self._confirmar_gasto()
            elif mensagem_lower in ['não', 'n', 'errado', 'cancel']:
                self.gastos_pendentes = {}
                return "Entendo. Vamos começar de novo! 👍"
        
        # Detecta tentativa de registrar gasto
        if self._contem_valor_monetario(mensagem):
            return self._processar_novo_gasto(mensagem)
        
        # Detecta pedidos de análise
        if any(palavra in mensagem_lower for palavra in ['quanto', 'gasto', 'total', 'resumo', 'análise']):
            return self._gerar_analise(mensagem)
        
        # Detecta pedidos de insights
        if any(palavra in mensagem_lower for palavra in ['economia', 'reduzir', 'economizar', 'sugestão']):
            return self._gerar_insights(mensagem)
        
        # Resposta padrão
        return self._resposta_padrao(mensagem)
    
    def _contem_valor_monetario(self, texto: str) -> bool:
        """Verifica se o texto contém um valor monetário (R$ ou números com vírgula/ponto)"""
        # Padrão: R$ 5.50, R$ 5,50, 5.50, 5,50
        padrao = r'(?:r\$\s*)?(\d+[.,]\d{1,2}|\d+)'
        return bool(re.search(padrao, texto, re.IGNORECASE))
    
    def _extrair_gasto(self, texto: str) -> Tuple[float, str]:
        """Extrai valor e descrição do texto"""
        # Extrai valor
        padrao = r'(?:r\$\s*)?(\d+[.,]\d{1,2}|\d+)'
        match = re.search(padrao, texto, re.IGNORECASE)
        valor = 0
        if match:
            valor_str = match.group(1).replace(',', '.')
            valor = float(valor_str)
        
        # Remove o valor do texto para pegar a descrição
        descricao = re.sub(padrao, '', texto, flags=re.IGNORECASE).strip()
        
        return valor, descricao
    
    def _detectar_categoria(self, descricao: str) -> str:
        """Detecta automaticamente a categoria baseado na descrição"""
        categorias = self.data_loader.get_categorias()
        descricao_lower = descricao.lower()
        
        for cat_key, cat_info in categorias.items():
            exemplos = cat_info.get('exemplos', [])
            for exemplo in exemplos:
                if exemplo.lower() in descricao_lower:
                    return cat_key
        
        # Padrão default
        if any(palavra in descricao_lower for palavra in ['café', 'comida', 'refeição', 'lanche']):
            return 'alimentacao'
        elif any(palavra in descricao_lower for palavra in ['uber', 'táxi', 'transporte']):
            return 'transporte'
        elif any(palavra in descricao_lower for palavra in ['netflix', 'jogo', 'filme', 'app']):
            return 'diversao'
        else:
            return 'outros'
    
    def _processar_novo_gasto(self, mensagem: str) -> str:
        """Processa um novo gasto extraído da mensagem"""
        valor, descricao = self._extrair_gasto(mensagem)
        categoria = self._detectar_categoria(descricao)
        
        # Validações
        if valor <= 0:
            return "❌ Não consegui extrair um valor válido. Tenta novamente?\nExemplo: 'Gastei R$5 com café'"
        
        if valor > 100:
            return f"⚠️ R${valor:.2f} parece alto para uma microdespesa (limite: R$100). Tem certeza?"
        
        # Armazena para confirmação
        agora = datetime.now()
        self.gastos_pendentes = {
            'valor': valor,
            'descricao': descricao if descricao else 'Gasto',
            'categoria': categoria,
            'data': agora.strftime('%Y-%m-%d'),
            'hora': agora.strftime('%H:%M'),
            'local': 'Não informado'
        }
        
        categoria_nome = self.data_loader.get_categorias().get(categoria, {}).get('nome', categoria)
        
        return f"""✏️ Deixa eu confirmar:
- Valor: R$ {valor:.2f}
- Descrição: {descricao if descricao else self.gastos_pendentes['categoria']}
- Categoria: {categoria_nome}

Correto? (sim/não)"""
    
    def _confirmar_gasto(self) -> str:
        """Confirma e registra o gasto pendente"""
        gasto = self.gastos_pendentes
        
        # Adiciona ao histórico
        self.data_loader.adicionar_transacao(
            gasto['data'],
            gasto['hora'],
            gasto['descricao'],
            gasto['categoria'],
            gasto['valor'],
            gasto['local']
        )
        
        # Atualiza o analisador
        self.analyzer.transacoes = self.data_loader.transacoes
        
        resposta = f"✅ Anotado! R${gasto['valor']:.2f} em {gasto['descricao']}\n\n"
        
        # Oferece insight rápido
        categoria = gasto['categoria']
        gastos_categoria = self.analyzer.gasto_por_categoria().get(categoria, 0)
        
        if categoria == 'alimentacao' and gastos_categoria > 100:
            resposta += "💡 Dica: Você já gastou bastante com alimentação esta semana! \n"
        
        resposta += "\nQuer continuar, ver resumo ou sair?"
        
        self.gastos_pendentes = {}
        return resposta
    
    def _gerar_analise(self, mensagem: str) -> str:
        """Gera análise baseada na pergunta do usuário"""
        mensagem_lower = mensagem.lower()
        
        if 'total' in mensagem_lower or 'quanto' in mensagem_lower and 'gasto' in mensagem_lower:
            return self.analyzer.gerar_resumo_executivo()
        
        if 'categoria' in mensagem_lower:
            categoria_top, valor_top = self.analyzer.categoria_top()
            return f"🏆 Sua categoria com maior gasto é:\n{categoria_top}: R$ {valor_top:.2f}"
        
        if 'dia' in mensagem_lower:
            dia_max, valor_max = self.analyzer.dia_maior_gasto()
            return f"📅 Dia com maior gasto:\n{dia_max}: R$ {valor_max:.2f}"
        
        return self.analyzer.gerar_resumo_executivo()
    
    def _gerar_insights(self, mensagem: str) -> str:
        """Gera sugestões de economia"""
        categoria_top, valor_top = self.analyzer.categoria_top()
        economia = self.analyzer.economia_potencial(categoria_top, 0.5)
        
        resposta = f"💡 OPORTUNIDADE DE ECONOMIA\n"
        resposta += f"Você gasta bastante com {categoria_top}: R$ {valor_top:.2f}\n\n"
        resposta += f"Se reduzisse em 50%, economizaria: R$ {economia:.2f}/mês ✨\n"
        resposta += f"Pequenas mudanças fazem grande diferença!"
        
        return resposta
    
    def _resposta_padrao(self, mensagem: str) -> str:
        """Resposta para mensagens genéricas"""
        respostas = [
            "🤖 Não entendi bem. Você quer:\n- Registrar um gasto? (ex: 'Gastei R$5 com café')\n- Ver resumo? (ex: 'Quanto gastei?')\n- Sugestões de economia? (ex: 'Como economizar?')",
            "Hmm, pode reformular? 😊\nPosso ajudar você a registrar gastos ou analisar padrões!",
            "Boa pergunta, mas fora do meu escopo! 🎯\nFoco em microdespesas. Quer registrar algo?"
        ]
        import random
        return random.choice(respostas)
    
    def obter_contexto(self) -> str:
        """Retorna o contexto para passar ao LLM"""
        return self.data_loader.get_contexto_para_prompt()
    
    def obter_resumo(self) -> str:
        """Retorna resumo completo de gastos"""
        return self.analyzer.gerar_resumo_executivo()
