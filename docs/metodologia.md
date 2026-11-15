# Metodologia e definições

## Fontes e escopo

Fontes fornecidas pelo autor: `data/dataset_saas.xlsx`, `data/saas_padronizado.xlsx` e a captura em `assets/dashboard-saas.png`. A análise usa o arquivo padronizado, com competências de janeiro/2024 a dezembro/2025. As planilhas foram copiadas sem edição. A base representa uma empresa fictícia.

## Granularidade

| Tabela | Uma linha representa | Chave |
|---|---|---|
| clientes | Uma empresa cliente | id_cliente |
| planos | Um plano de assinatura | id_plano |
| assinaturas | Uma assinatura e seu ciclo de vida | id_assinatura |
| historico_mensal | Uma assinatura em uma competência | id_assinatura_mes |
| faturas | Uma fatura | id_fatura |
| uso_mensal | O uso de uma assinatura em uma competência | id_assinatura_mes |

As chaves de cliente, assinatura e plano permitem cruzar os registros. Ao combinar fatos mensais, confirme a unicidade da chave para evitar multiplicação da receita. Esta é uma descrição dos dados; não atesta o desenho interno do modelo Power BI.

## Regras de cálculo

- **MRR por competência:** soma de `valor_contratado_brl` no histórico mensal. Não somar os MRRs de vários meses para chamar o resultado de MRR de encerramento. É receita contratada; não é caixa recebido.
- **Clientes ativos ao final do mês:** início anterior ao primeiro dia do mês seguinte e cancelamento ausente ou posterior/igual ao primeiro dia do mês seguinte. Nesta base há uma assinatura por cliente; em outro cenário, contar clientes distintos.
- **Base inicial do mês:** início anterior ao primeiro dia do mês e cancelamento ausente ou posterior/igual a essa data. Uma assinatura cancelada no primeiro dia ainda integra o denominador inicial desta convenção.
- **Cancelamentos do mês:** data de cancelamento no intervalo [início do mês, início do mês seguinte).
- **Churn mensal:** cancelamentos do mês / base inicial do mesmo mês. Para dezembro/2025: 14 / 655 = 2,1374%, exibido como 2,14%.
- **Receita por cliente:** MRR do mês / clientes ativos ao encerramento do mês. Para dezembro: R$ 236.268,45 / 641 = R$ 368,59.
- **Crescimento anual do MRR:** MRR dez/2025 / MRR dez/2024 − 1 = 56,42%.
- **Participação por plano:** MRR de cada plano / MRR total na mesma competência.
- **Motivos:** contagem de assinaturas canceladas até o encerramento de dezembro/2025, por motivo registrado.
- **Proporção histórica cancelada por segmento:** clientes cancelados no histórico / total de clientes do segmento no histórico. Não é uma taxa mensal, nem uma estimativa de sobrevivência ajustada por coorte.
- **Saldo em aberto:** soma de máximo(valor faturado − valor pago, 0) em todas as faturas do arquivo. Não reconstrói uma posição histórica de recebíveis e não aplica filtro de vencimento.

Valores monetários são calculados em reais; os resultados são arredondados apenas para apresentação. Comparações mantêm os mesmos períodos e denominadores.

## Qualidade e limites

O arquivo padronizado contém 51 registros de validação, todos com quantidade de exceções igual a zero, e nenhuma pendência. Esses diagnósticos foram recebidos com o arquivo, não produzidos originalmente por este portfólio. O script adicional recalcula indicadores e verifica unicidade e referências principais para a análise.

Motivos registrados são descritivos e podem conter viés de resposta. Uma associação entre segmento e cancelamento pode refletir diferenças de plano, porte, aquisição ou tempo de exposição. Não foram estimados efeitos causais nem construídos modelos preditivos. Não se calculam LTV, CAC ou lucro porque não há suporte suficiente de custos e premissas nesta análise.

Para investigar uso e churn, medir atividade em uma janela anterior ao cancelamento, definir uma data de referência para clientes ativos e comparar coortes equivalentes. Usar comportamento posterior ao evento introduziria vazamento de informação.

O link Power BI e a captura são fornecidos pelo autor. As medidas DAX, os passos de Power Query e o arquivo PBIX não foram disponibilizados; as regras acima documentam o recálculo independente, sem atribuí-las ao código interno do relatório.
