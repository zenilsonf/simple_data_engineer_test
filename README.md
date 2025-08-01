# Desafio Rápido – Engenheiro(a) de Dados (Python + Logs)

**Tempo sugerido:** 30–40 minutos  
**Objetivo:** Construir um mini–pipeline em **Python** (apenas 1 script) que lê dados brutos, trata problemas simples, agrega e salva um resultado; e demonstrar leitura/diagnóstico de logs (parte separada em `logs.md`).

## Tarefas (pipeline)
Entrada: dois CSVs em `./data`

- `clientes.csv` com possíveis duplicidades por `cliente_id` e `updated_at`.
- `vendas.csv` com linhas problemáticas (datas/valores).

Implementar um script executável via linha de comando:

```
python etl.py --in ./data --out ./out
```

ou

```
spark-submit etl.py --in ./data --out ./out
```

### Requisitos mínimos
1. **Normalizar datas** para `YYYY-MM-DD`. Ignorar linhas com data inválida (logar erro).
2. **Deduplicar clientes** por `cliente_id`, escolhendo o registro de **maior `updated_at`**.
3. **Agregação de vendas (valor_total)** por dia e `cliente_id`: `valor_total = soma(valor * quantidade)`.
4. **Inner join** com clientes deduplicados (linhas sem cliente válido não entram).
5. **Salvar** um arquivo `out/diario.csv` com as colunas:
   - `dt` (data no formato `YYYY-MM-DD`)
   - `cliente_id`
   - `valor_total`
6. **Logging** útil (níveis `INFO` e `ERROR`) mostrando: contagens lidas, descartes por validação, registros salvos.
7. **Tratamento de erros** apenas onde necessário (sem esconder stacktraces úteis).

### Restrições
- Evite dependências pesadas. Você pode usar **pyspark** (preferencialmente), **pandas** ou apenas a biblioteca padrão (`csv`, `datetime`).
- Mantenha o código em um **único arquivo** `etl.py` com funções pequenas e claras.
- Qualidade do log conta – mensagens que ajudem a depurar.

### Datasets
- Dados de exemplo estão em `./data`. Incluem duplicidades e linhas inválidas propositalmente.

### Entrega esperada
- Código que **roda sem ajustes** com os dados fornecidos.
- Mensagens de log indicando decisões (linhas descartadas, normalização etc.).
- Arquivo gerado em `./out/diario.csv`.

## Dicas
- Valide schema obrigatório antes de processar.
- Para datas, normalize diferentes formatos; descarte inválidas com log.
- Para valores, trate conversões e quantidades ausentes com log e descarte da linha de venda.

---

## Parte 2 – Leitura de Logs
Abra `logs.md`. Para cada trecho:

1) aponte a **causa provável**,  
2) proponha **duas correções/mitigações**,  
3) descreva **como validar** a correção.

---
