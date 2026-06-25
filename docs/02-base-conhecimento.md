# Base de Conhecimento: MILA 💰

## Dados Utilizados

MILA utiliza 2 arquivos principais:

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `microdespesas.csv` | CSV | Histórico de gastos do usuário (últimos 30 dias) |
| `config_usuario.json` | JSON | Categorias, metas semanais, limites, perfil do usuário |

### Estrutura do `microdespesas.csv`
- **data**: Data do gasto (YYYY-MM-DD)
- **hora**: Horário do gasto (HH:MM)
- **descricao**: Descrição natural (ex: "Café da manhã")
- **categoria**: Categoria automática (alimentacao, transporte, diversao, saude, outros)
- **valor**: Valor em R$ (até 100.00 = microdespesa)
- **local**: Onde foi gasto
- **notas**: Observações extras

### Estrutura do `config_usuario.json`
- **usuario**: Nome, meta mensal, moeda
- **categorias**: Lista de categorias com metas semanais e exemplos
- **limites**: Máximo por transação, limite mensal
- **insights_disponiveis**: Tipos de análises que MILA pode fazer

---

## Adaptações nos Dados

Os dados foram adaptados para refletir **padrões reais de microdespesas**:

✅ **Dados Reais**: 30 dias de gastos variados (não fictícios)  
✅ **Padrões Realistas**: Café repetido (mostra hábito), variação de dias/horários  
✅ **Distribuição Justa**: Alimentação ~60%, Transporte ~20%, Diversão ~20%  
✅ **Microdespesas**: Todos os itens ≤ R$50 (exceto dias especiais como cinema)  
✅ **Dados Suficientes**: 40+ transações para gerar insights significativos  

---

## Estratégia de Integração

### Como os dados são carregados?
MILA carrega os dados no **início da conversa**:
1. Arquivo `config_usuario.json` é lido → perfil do usuário
2. Arquivo `microdespesas.csv` é lido → histórico (últimos 30 dias)
3. Dados são inseridos no **system prompt** para contexto permanente
4. Usuário pode adicionar novos gastos → agente atualiza na sessão

### Como os dados são usados no prompt?
Os dados vão no **system prompt** como contexto estruturado:
- Categorias disponíveis
- Metas semanais
- Últimos 10 gastos (para contextualizar padrões)
- Resumo: Total gasto, categoria top, dias analisados

Quando o usuário faz perguntas (ex: "quanto gastei com café?"), o agente **busca no histórico** e responde com dados reais.

---

## Exemplo de Contexto Montado

```
=== CONTEXTO DO USUÁRIO ===
Nome: João Silva
Meta mensal: R$ 500.00
Dias analisados: 30 (16/06 a 25/06)

=== RESUMO DE GASTOS ===
Total: R$ 439.30
Categoria Top: Alimentação (R$ 267.00 - 60%)
Dia maior gasto: 2025-06-21 (R$ 76.90)

=== ÚLTIMOS GASTOS ===
- 25/06 14:00 Lanche (R$9.50) - Lanchonete
- 25/06 16:00 Livro digital (R$19.90) - Plataforma
- 24/06 20:00 Pipoca (R$8.00) - Cinema
- 24/06 18:00 Uber (R$16.00) - App
... (mais gastos)

=== CATEGORIAS E METAS SEMANAIS ===
📌 Alimentação: R$150/semana (Gasto atual: R$267 - ⚠️ ULTRAPASSOU)
🚗 Transporte: R$100/semana (Gasto atual: R$59 - ✅ No controle)
🎮 Diversão: R$100/semana (Gasto atual: R$113 - ⚠️ ULTRAPASSOU)
🏥 Saúde: R$80/semana (Gasto atual: R$0 - ✅ No controle)
```

Quando o usuário pergunta: **"Quanto gastei com café?"**

MILA responde:
> "Você registrou **7 cafés nos últimos 10 dias**, totalizando **R$42**. Média de ~R$6 por café. Se reduzisse para 3 cafés/semana, economizaria cerca de **R$120/mês**!"

Últimas transações:
- 01/11: Supermercado - R$ 450
- 03/11: Streaming - R$ 55
...
```
