from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import statistics

class Analyzer:
    """Analisa gastos e gera insights."""
    
    def __init__(self, transacoes: list, config: dict):
        self.transacoes = transacoes
        self.config = config
        self.categorias = config.get('categorias', {})
    
    def gasto_total(self) -> float:
        """Total de gastos"""
        return sum(t['valor'] for t in self.transacoes)
    
    def gasto_por_categoria(self) -> Dict[str, float]:
        """Gastos agrupados por categoria"""
        resultado = {}
        for t in self.transacoes:
            cat = t['categoria']
            resultado[cat] = resultado.get(cat, 0) + t['valor']
        return resultado
    
    def categoria_top(self) -> Tuple[str, float]:
        """Categoria com maior gasto"""
        gasto_cat = self.gasto_por_categoria()
        if gasto_cat:
            top_cat = max(gasto_cat.items(), key=lambda x: x[1])
            return top_cat
        return ("N/A", 0)
    
    def gasto_por_dia(self) -> Dict[str, float]:
        """Gastos agrupados por dia"""
        resultado = {}
        for t in self.transacoes:
            data = t['data']
            resultado[data] = resultado.get(data, 0) + t['valor']
        return resultado
    
    def dia_maior_gasto(self) -> Tuple[str, float]:
        """Dia com maior gasto"""
        gasto_dia = self.gasto_por_dia()
        if gasto_dia:
            dia_max = max(gasto_dia.items(), key=lambda x: x[1])
            return dia_max
        return ("N/A", 0)
    
    def gasto_medio_diario(self) -> float:
        """Média de gasto por dia"""
        gasto_dia = self.gasto_por_dia()
        if gasto_dia:
            return sum(gasto_dia.values()) / len(gasto_dia)
        return 0
    
    def gasto_por_descricao(self) -> Dict[str, Tuple[int, float]]:
        """Agrupa por tipo de gasto (ex: café, uber)"""
        resultado = {}
        for t in self.transacoes:
            desc = t['descricao'].lower()
            if desc not in resultado:
                resultado[desc] = (0, 0)
            count, total = resultado[desc]
            resultado[desc] = (count + 1, total + t['valor'])
        return resultado
    
    def gastos_mais_frequentes(self, top_n: int = 5) -> List[Dict]:
        """Retorna os gastos mais frequentes"""
        por_desc = self.gasto_por_descricao()
        sorted_desc = sorted(por_desc.items(), key=lambda x: x[1][0], reverse=True)[:top_n]
        
        resultado = []
        for desc, (count, total) in sorted_desc:
            resultado.append({
                'descricao': desc,
                'quantidade': count,
                'total': total,
                'media': total / count
            })
        return resultado
    
    def economia_potencial(self, categoria: str, reducao_percentual: float = 0.5) -> float:
        """Calcula economia potencial se reduzir gasto de uma categoria"""
        gasto_cat = self.gasto_por_categoria().get(categoria, 0)
        return gasto_cat * reducao_percentual
    
    def comparacao_com_meta(self, categoria: str) -> Dict:
        """Compara gasto real com meta"""
        gasto_real = self.gasto_por_categoria().get(categoria, 0)
        cat_info = self.categorias.get(categoria, {})
        meta_semanal = cat_info.get('meta_semanal', 0)
        
        # Assume 4 semanas por mês
        meta_mensal = meta_semanal * 4
        
        return {
            'categoria': categoria,
            'gasto_real': gasto_real,
            'meta_mensal': meta_mensal,
            'diferenca': gasto_real - meta_mensal,
            'percentual_da_meta': (gasto_real / meta_mensal * 100) if meta_mensal > 0 else 0,
            'ultrapassou': gasto_real > meta_mensal
        }
    
    def gasto_por_hora(self) -> Dict[str, float]:
        """Gastos agrupados por hora"""
        resultado = {}
        for t in self.transacoes:
            hora = t['hora'].split(':')[0]  # Pega só a hora (HH)
            resultado[hora] = resultado.get(hora, 0) + t['valor']
        return resultado
    
    def horario_pico_gasto(self) -> Tuple[str, float]:
        """Hora com mais gastos"""
        gasto_hora = self.gasto_por_hora()
        if gasto_hora:
            hora_max = max(gasto_hora.items(), key=lambda x: x[1])
            return hora_max
        return ("N/A", 0)
    
    def gerar_resumo_executivo(self) -> str:
        """Gera resumo completo de gastos"""
        resumo = "📊 RESUMO DE MICRODESPESAS\n"
        resumo += "=" * 40 + "\n\n"
        
        resumo += f"💰 Total gasto: R$ {self.gasto_total():.2f}\n"
        resumo += f"📈 Transações: {len(self.transacoes)}\n"
        resumo += f"📉 Média/dia: R$ {self.gasto_medio_diario():.2f}\n\n"
        
        resumo += "📌 Por Categoria:\n"
        for cat, valor in self.gasto_por_categoria().items():
            percentual = (valor / self.gasto_total() * 100) if self.gasto_total() > 0 else 0
            resumo += f"  • {cat}: R$ {valor:.2f} ({percentual:.1f}%)\n"
        
        resumo += f"\n📍 Dia maior gasto: {self.dia_maior_gasto()[0]} (R$ {self.dia_maior_gasto()[1]:.2f})\n"
        
        resumo += f"\n⏰ Horário pico: {self.horario_pico_gasto()[0]}:00 (R$ {self.horario_pico_gasto()[1]:.2f})\n"
        
        resumo += "\n🔝 Top 5 Gastos Frequentes:\n"
        for idx, item in enumerate(self.gastos_mais_frequentes(5), 1):
            resumo += f"  {idx}. {item['descricao']}: {item['quantidade']}x (R$ {item['total']:.2f}, média R$ {item['media']:.2f})\n"
        
        return resumo
