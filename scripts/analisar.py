"""Recalcula indicadores do portfólio sem modificar os arquivos de entrada."""
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
import json
import openpyxl

ROOT = Path(__file__).resolve().parents[1]


def read_tables(path):
    workbook = openpyxl.load_workbook(path, read_only=True, data_only=True)
    tables = {}
    for sheet in workbook:
        rows = iter(sheet.values)
        headers = next(rows)
        tables[sheet.title] = [dict(zip(headers, row)) for row in rows]
    workbook.close()
    return tables


def unique(rows, key):
    values = [row[key] for row in rows]
    assert None not in values and len(values) == len(set(values)), key


def main():
    tables = read_tables(ROOT / 'data/saas_padronizado.xlsx')
    original = read_tables(ROOT / 'data/dataset_saas.xlsx')
    keys = {'clientes': 'id_cliente', 'planos': 'id_plano',
            'assinaturas': 'id_assinatura', 'historico_mensal': 'id_assinatura_mes',
            'faturas': 'id_fatura', 'uso_mensal': 'id_assinatura_mes'}
    for name, key in keys.items():
        unique(tables[name], key)
        assert tables[name] == original[name], f'Diferença entre arquivos: {name}'
    unique(tables['assinaturas'], 'id_cliente')
    client_ids = {r['id_cliente'] for r in tables['clientes']}
    sub_ids = {r['id_assinatura'] for r in tables['assinaturas']}
    plan_ids = {r['id_plano'] for r in tables['planos']}
    month_ids = {r['id_assinatura_mes'] for r in tables['historico_mensal']}
    assert all(r['id_cliente'] in client_ids for r in tables['assinaturas'])
    assert all(r['id_cliente'] in client_ids and r['id_assinatura'] in sub_ids
               and r['id_plano'] in plan_ids for r in tables['historico_mensal'])
    for name in ['faturas', 'uso_mensal']:
        assert all(r['id_assinatura_mes'] in month_ids for r in tables[name])

    start, end = datetime(2025, 12, 1), datetime(2026, 1, 1)
    subs, history, invoices = (tables[n] for n in ['assinaturas', 'historico_mensal', 'faturas'])
    mrr, plans = defaultdict(float), defaultdict(float)
    for row in history:
        mrr[row['competencia'].strftime('%Y-%m')] += row['valor_contratado_brl']
        if row['competencia'] == start:
            plans[row['id_plano']] += row['valor_contratado_brl']
    mrr = {k: round(v, 2) for k, v in sorted(mrr.items())}
    active = [r for r in subs if r['data_inicio'] < end and
              (r['data_cancelamento'] is None or r['data_cancelamento'] >= end)]
    base = [r for r in subs if r['data_inicio'] < start and
            (r['data_cancelamento'] is None or r['data_cancelamento'] >= start)]
    cancelled = [r for r in subs if r['data_cancelamento'] and start <= r['data_cancelamento'] < end]
    historical_cancelled = [r for r in subs if r['data_cancelamento'] and r['data_cancelamento'] < end]
    reasons = Counter(r['motivo_cancelamento'] for r in historical_cancelled)
    segments = {r['id_cliente']: r['segmento'] for r in tables['clientes']}
    segment_totals = Counter(segments[r['id_cliente']] for r in subs)
    segment_cancelled = Counter(segments[r['id_cliente']] for r in historical_cancelled)
    plan_names = {r['id_plano']: r['nome_plano'] for r in tables['planos']}
    result = {
        'linhas': {n: len(tables[n]) for n in keys},
        'mrr_por_competencia_brl': mrr,
        'clientes_ativos_dez_2025': len(active),
        'base_inicial_dez_2025': len(base),
        'cancelamentos_dez_2025': len(cancelled),
        'churn_dez_2025_pct': round(100 * len(cancelled) / len(base), 4),
        'receita_por_cliente_dez_2025_brl': round(mrr['2025-12'] / len(active), 2),
        'crescimento_anual_mrr_pct': round(100 * (mrr['2025-12'] / mrr['2024-12'] - 1), 4),
        'variacao_desde_pico_pct': round(100 * (mrr['2025-12'] / max(mrr.values()) - 1), 4),
        'mrr_por_plano_dez_2025_brl': {plan_names[k]: round(v, 2) for k, v in plans.items()},
        'motivos_cancelamento_historico': dict(reasons),
        'segmentos': {s: {'clientes': segment_totals[s], 'cancelados': segment_cancelled[s],
                         'proporcao_cancelada_pct': round(100 * segment_cancelled[s] / segment_totals[s], 2)}
                      for s in sorted(segment_totals)},
        'saldo_em_aberto_origem_brl': round(sum(max(0, r['valor_faturado_brl'] - (r['valor_pago_brl'] or 0)) for r in invoices), 2),
        'faturas_com_saldo': sum(r['valor_faturado_brl'] > (r['valor_pago_brl'] or 0) for r in invoices),
        'validacoes_recebidas': len(tables['validacoes']),
        'pendencias_recebidas': len(tables['pendencias']),
        'verificacao': 'Chaves únicas, referências principais e igualdade das seis tabelas de negócio entre os arquivos conferidas.'
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
