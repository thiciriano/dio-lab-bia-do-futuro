import json
import csv
from datetime import datetime
from pathlib import Path

class DataLoader:
    """Carrega e gerencia os dados de microdespesas."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.config = self._load_config()
        self.transacoes = self._load_transacoes()
    
    def _load_config(self) -> dict:
        """Carrega config_usuario.json"""
        config_path = self.data_dir / "config_usuario.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _load_transacoes(self) -> list:
        """Carrega microdespesas.csv"""
        transacoes = []
        csv_path = self.data_dir / "microdespesas.csv"
        
        if csv_path.exists():
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row['valor'] = float(row['valor'])
                    transacoes.append(row)
        
        return transacoes
    
    def get_categorias(self) -> dict:
        """Retorna categorias disponíveis"""
        return self.config.get('categorias', {})
    
    def get_usuario(self) -> dict:
        """Retorna dados do usuário"""
        return self.config.get('usuario', {})
    
    def get_contexto_para_prompt(self) -> str:
        """Monta contexto estruturado para o LLM"""
        usuario = self.get_usuario()
        categorias = self.get_categorias()
        
        # Calcula resumo
        total_gasto = sum(t['valor'] for t in self.transacoes)
        gasto_por_categoria = {}
        for t in self.transacoes:
            cat = t['categoria']
            gasto_por_categoria[cat] = gasto_por_categoria.get(cat, 0) + t['valor']
        
        categoria_top = max(gasto_por_categoria.items(), key=lambda x: x[1])[0] if gasto_por_categoria else "N/A"
        
        # Últimos 5 gastos
        ultimos_gastos = self.transacoes[-5:] if self.transacoes else []
        
        contexto = f"""
=== CONTEXTO DO USUÁRIO ===
Nome: {usuario.get('nome', 'Usuário')}
Meta mensal: R$ {usuario.get('meta_mensal', 0):.2f}

=== RESUMO DE GASTOS ===
Total: R$ {total_gasto:.2f}
Transações: {len(self.transacoes)}
Categoria Top: {categoria_top}

=== ÚLTIMOS GASTOS ===
"""
        for t in ultimos_gastos:
            contexto += f"- {t['data']} {t['hora']} {t['descricao']} (R${t['valor']:.2f}) - {t['local']}\n"
        
        contexto += "\n=== CATEGORIAS DISPONÍVEIS ===\n"
        for cat_key, cat_info in categorias.items():
            contexto += f"- {cat_info['nome']}: R${cat_info['meta_semanal']:.2f}/semana\n"
        
        return contexto
    
    def adicionar_transacao(self, data: str, hora: str, descricao: str, 
                            categoria: str, valor: float, local: str, notas: str = "") -> None:
        """Adiciona uma nova transação"""
        self.transacoes.append({
            'data': data,
            'hora': hora,
            'descricao': descricao,
            'categoria': categoria,
            'valor': valor,
            'local': local,
            'notas': notas
        })
    
    def salvar_transacoes(self) -> None:
        """Salva transações no CSV"""
        csv_path = self.data_dir / "microdespesas.csv"
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            if self.transacoes:
                fieldnames = self.transacoes[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.transacoes)
