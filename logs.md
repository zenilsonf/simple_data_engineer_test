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


# Leitura e Debug de Logs - Respostas

## Snippet 1 – Python/ETL
    ```
    KeyError: 'valor'
    File "etl.py", line 42, in transformar
        df['valor_total'] = df['valor'] * df['quantidade']
    ```

    ### 1) Causa provável:
    A coluna 'valor' não existe no DataFrame. Possíveis cenários:
    - O arquivo CSV não possui a coluna 'valor'
    - A coluna tem nome diferente (ex: 'preco', 'price', 'Valor')
    - Erro na leitura do CSV ou transformação anterior removeu a coluna

    ### 2) Duas correções/mitigações:
    **Correção 1 - Validação de schema:**
    ```python
    def valida_schema(df, colunas_necessarias):
        colunas_faltantes = set(colunas_obrigatorias) - set(df.columns)
        if colunas_faltantes:
            raise ValueError(f"Colunas faltantes: {colunas_faltantes}")
        
    # Usar antes da transformação
    valida_schema(df, ['valor', 'quantidade'])
    ```

    **Correção 2 - Tratamento defensivo:**
    ```python
    if 'valor' in df.columns and 'quantidade' in df.columns:
        df['valor_total'] = df['valor'] * df['quantidade']
    else:
        logging.error(f"Colunas disponíveis: {df.columns.tolist()}")
        raise KeyError("Colunas 'valor' ou 'quantidade' não encontradas")
    ```

    ### 3) Como validar a correção:
    - **Teste unitário**: Criar DataFrame sem a coluna 'valor' e verificar se o erro é tratado adequadamente
    - **Log de debug**: Adicionar `print(df.columns)` antes da linha 42 para confirmar colunas disponíveis
    - **Verificação de arquivo**: Inspecionar o CSV de origem para confirmar nomes das colunas

---

## Snippet 2 – Airflow
    ```
    airflow.exceptions.AirflowException: The conn_id 'postgres_dw' isn't defined
    Task: load_dw >> PostgresOperator
    ```

    ### 1) Causa provável:
        A conexão 'postgres_dw' não foi configurada no Airflow. O PostgresOperator está tentando usar uma conexão que não existe nas configurações do Airflow.

    ### 2) Duas correções/mitigações:
        **Correção 1 - Criar conexão via Interface Web:**
        1. Acessar Airflow UI → Admin → Connections
        2. Criar nova conexão:
        - Conn Id: `postgres_dw`
        - Conn Type: `Postgres`
        - Host, Port, Schema, Login, Password conforme ambiente

        **Correção 2 - Configurar via código/variável de ambiente:**
        ```python
        # No DAG, usar variáveis de ambiente
        from airflow.models import Variable

        postgres_operator = PostgresOperator(
            task_id='load_dw',
            postgres_conn_id=Variable.get("POSTGRES_CONN_ID", default_var="postgres_default"),
            sql="SELECT 1"
        )
        ```

    ### 3) Como validar a correção:
        - **Teste de conexão**: Na UI do Airflow, usar o botão "Test" na conexão criada
        - **Execução manual**: Executar a task manualmente no Airflow UI
        - **Log verification**: Verificar se os logs da task não mostram mais erro de conexão

    ---

## Snippet 3 – Spark
    ```
    Job aborted due to stage failure: Task 7 in stage 23.0 failed 4 times
    Caused by: java.lang.OutOfMemoryError: Java heap space
    ```

    ### 1) Causa provável:
        Memória insuficiente alocada para o driver ou executors do Spark. O job está processando mais dados do que a heap consegue comportar, causando OutOfMemoryError.

    ### 2) Duas correções/mitigações:
        **Correção 1 - Aumentar memória do Spark:**
        ```bash
        # Configurações ao submeter o job
        spark-submit \
        --driver-memory 4g \
        --executor-memory 4g \
        --executor-cores 2 \
        --num-executors 4 \
        --conf spark.sql.adaptive.enabled=true \
        meu_script.py
        ```

    **Correção 2 - Otimizar processamento:**
        ```python
        # Particionar dados para reduzir carga de memória
        df = df.repartition(200)  # Aumentar partições

        # Usar cache apenas quando necessário
        df.cache() # só se usar múltiplas vezes

        # Processar em batches menores
        df.write.mode("append").option("batchsize", 1000).save()
        ```

    ### 3) Como validar a correção:
        - **Monitoramento**: Usar Spark UI (porta 4040) para monitorar uso de memória durante execução
        - **Teste incremental**: Processar dataset menor primeiro, depois aumentar gradualmente
        - **Métricas de performance**: Verificar se o job completa sem falhas e observar tempo de execução
