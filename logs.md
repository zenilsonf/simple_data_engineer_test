# Leitura e Debug de Logs

Para **cada** trecho abaixo, responda:

1) Causa provável (qual o problema raiz?),  
2) Duas correções/mitigações possíveis,  
3) Como validar a correção (experimento/verificação).

---

## Snippet 1 – Python/ETL
```
KeyError: 'valor'
File "etl.py", line 42, in transformar
    df['valor_total'] = df['valor'] * df['quantidade']
```

---

## Snippet 2 – Airflow
```
airflow.exceptions.AirflowException: The conn_id 'postgres_dw' isn't defined
Task: load_dw >> PostgresOperator
```

---

## Snippet 3 – Spark
```
Job aborted due to stage failure: Task 7 in stage 23.0 failed 4 times
Caused by: java.lang.OutOfMemoryError: Java heap space
```
