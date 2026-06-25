# 🤖 MILA - Código Fonte

Aplicação funcional do assistente de microdespesas MILA.

## Arquivos

- **`mila.py`**: Classe principal do agente (processamento, análises, confirmações)
- **`data_loader.py`**: Carregamento e gerenciamento de dados
- **`analyzer.py`**: Análise de gastos e geração de insights
- **`app.py`**: Interface de chat no terminal

## Como Usar

### 1. Executar o Chat Interativo

```bash
python src/app.py
```

Você verá o banner de boas-vindas e poderá conversar com MILA.

### 2. Exemplos de Interação

```
Você: Gastei R$6 com café
MILA: ✏️ Deixa eu confirmar:
- Valor: R$ 6.00
- Descrição: café
- Categoria: Alimentação
Correto? (sim/não)

Você: sim
MILA: ✅ Anotado! R$6.00 em café
...

Você: Quanto gastei?
MILA: 📊 RESUMO DE MICRODESPESAS
=====================================
💰 Total gasto: R$ 439.30
... (mais informações)

Você: Como economizar?
MILA: 💡 OPORTUNIDADE DE ECONOMIA
Você gasta bastante com Alimentação: R$ 267.00
...
```

### 3. Comandos Especiais

| Comando | Efeito |
|---------|--------|
| `resumo` | Exibe resumo completo de todos os gastos |
| `sair` / `exit` | Encerra o programa |

## Estrutura de Dados

### Carregamento

```python
from src.mila import MILA

mila = MILA(data_dir='data')
resposta = mila.processar_mensagem("Gastei R$5 com café")
print(resposta)
```

### Métodos Principais

```python
# Processar mensagem do usuário
resposta = mila.processar_mensagem("Quanto gastei com café?")

# Obter resumo
resumo = mila.obter_resumo()

# Obter contexto para LLM
contexto = mila.obter_contexto()

# Acessar analisador
gasto_total = mila.analyzer.gasto_total()
categoria_top = mila.analyzer.categoria_top()
```

## Fluxo de Processamento

```
Mensagem do Usuário
        ↓
Detectar tipo (gasto/análise/insight)
        ↓
┌─────────────────────────────────────┐
│ Tipo: NOVO GASTO                    │
│ • Extrai valor e descrição          │
│ • Detecta categoria automática      │
│ • Pede confirmação                  │
│ • Registra (se confirmado)          │
└─────────────────────────────────────┘
        ↓
┌─────────────────────────────────────┐
│ Tipo: ANÁLISE                       │
│ • Consulta dados carregados         │
│ • Gera resumo/comparação            │
│ • Apresenta insights                │
└─────────────────────────────────────┘
        ↓
Resposta ao Usuário
```

## Validações e Segurança

✅ Confirmação obrigatória antes de registrar  
✅ Limite máximo de R$100 por microdespesa  
✅ Todas as respostas baseadas em dados reais  
✅ Categorização automática (com exemplos)  
✅ Reconhecimento de padrões (café repetido, etc.)  

## Limitações Atuais

- ⚠️ Sem integração com LLM externo (usa processamento local)
- ⚠️ Dados salvos apenas em memória (não persiste em arquivo)
- ⚠️ Sem autenticação ou segurança avançada
- ⚠️ Interface terminal simples (sem GUI)

## Próximas Melhorias

- [ ] Integração com OpenAI API (GPT-4)
- [ ] Persistência em banco de dados
- [ ] Interface Streamlit com gráficos
- [ ] Previsão de gastos (ML)
- [ ] Notificações de limite ultrapassado
- [ ] Export de relatórios em PDF
