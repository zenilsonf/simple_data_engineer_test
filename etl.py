from typing import List
import pandas as pd
import argparse
import logging
import os

#Variáveis
TABLES = ['clientes', 'vendas']


# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='[%(levelname)s] %(message)s'
)

parser = argparse.ArgumentParser(description='ETL processamento de arquivos CSV.')
parser.add_argument('--in', dest='input_dir', required=True)
parser.add_argument('--out', dest='output_dir', required=True)

args = parser.parse_args()


def leitura_arquivos(diretorio: str) -> dict:

    """Lê arquivos CSV de um diretório e retorna uma lista de todos os dataframes.
    Args:
        caminho (str): Caminho do diretório contendo os arquivos CSV.
    Returns:
        dfs: Lista contendo os dataframes.
    """
    dfs = {}
    logging.info(f'Lendo arquivos do diretório: {diretorio}')

    for tabela in TABLES:
        arquivo_path  = f'{diretorio}/{tabela}.csv'
        try:
            df = pd.read_csv(arquivo_path )
            logging.info(f'Arquivo {arquivo_path }.csv lido com sucesso.')
            logging.info(f'{len(df)} registros lidos do {tabela}.csv')
            dfs[tabela] = df
        except FileNotFoundError:
            logging.error(f'Arquivo {tabela}.csv não encontrado.')
            continue

    return dfs


def normaliza_datas(df: pd.DataFrame, nome_coluna: str) -> pd.DataFrame:
    """
        Converte colunas de data para o formato datetime.
        Args:
            df (pd.DataFrame): DataFrame contendo a coluna de data.
            nome_coluna (str): Nome da coluna que contém as datas.
        Returns:
            pd.DataFrame: DataFrame com a coluna de data convertida.
    """

    logging.info(f'Convertendo colunas de data para o formato datetime.')

    df[nome_coluna] = df[nome_coluna].str.replace(' ', 'T', regex=False)
    df[nome_coluna] = df[nome_coluna].str.replace('/', '-', regex=False)

    print(df.head())

    df[nome_coluna] = pd.to_datetime(df[nome_coluna], errors='coerce')

    num_linhas_descartadas = df[nome_coluna].isna().sum()
    logging.error(f"{num_linhas_descartadas} linhas descartadas por data inválida.")
    df.dropna(subset=[nome_coluna], inplace=True)

    df[f'{nome_coluna}_formatada'] = df[nome_coluna].dt.strftime('%Y-%m-%d')

    return df

def normaliza_valores_numericos(df: pd.DataFrame, nome_coluna: str) -> pd.DataFrame:
    """
        Normaliza valores numéricos em um DataFrame.
        Remove linhas com valores nulos, vazios ou não numéricos.
        Args:
            df (pd.DataFrame): DataFrame contendo colunas numéricas.
        Returns:
            pd.DataFrame: DataFrame com colunas numéricas normalizadas.
    """

    logging.info(f'Normalizando valores numéricos na coluna: {nome_coluna}')
    if nome_coluna in df.columns:
        # Substitui strings vazias por NaN antes de converter
        df[nome_coluna] = df[nome_coluna].replace('', pd.NA)
        df[nome_coluna] = pd.to_numeric(df[nome_coluna], errors='coerce')
        num_linhas_descartadas = df[nome_coluna].isna().sum()
        logging.error(f"{num_linhas_descartadas} linhas descartadas por valor numérico inválido.")
        df.dropna(subset=[nome_coluna], inplace=True)

    return df

def deduplicar_dimensao(df: pd.DataFrame, chave_primaria: str, coluna_prioridade: str) -> pd.DataFrame:
    """
        Deduplica um DataFrame com base em uma chave primária.
        Args:
            df (pd.DataFrame): DataFrame a ser deduplicado.
            chave_primaria (str): Nome da coluna que será usada como chave primária.
            coluna_prioridade (str): Nome da coluna que será usada para determinar a prioridade.
        Returns:
            pd.DataFrame: DataFrame deduplicado.
    """

    logging.info(f'Deduplicando DataFrame com base na chave primária: {chave_primaria}')
    df = df.sort_values(by=coluna_prioridade, ascending=False)
    df_deduplicado = df.drop_duplicates(subset=chave_primaria, keep='first')

    num_linhas_iniciais = len(df)
    num_linhas_finais = len(df_deduplicado)
    logging.info(f'Deduplicação concluída: {num_linhas_iniciais - num_linhas_finais} linhas duplicadas removidas.')

    return df_deduplicado


def fato_diario(dfvendas: pd.DataFrame) -> pd.DataFrame:
    """
        Cria uma tabela de fatos diários a partir de um DataFrame.
        Args:
            df (pd.DataFrame): DataFrame contendo os dados.
        Returns:
            pd.DataFrame: DataFrame com a tabela de fatos diários.
    """

    logging.info('Criando tabela de fatos diários.')

    dfvendas['valor_total'] = dfvendas['valor'] * dfvendas['quantidade']
    df_diario = dfvendas.groupby(['cliente_id', 'data_formatada'])['valor_total'].sum().reset_index()

    print(df_diario.head())

    return df_diario

if __name__ == '__main__':

    tabelas = leitura_arquivos(args.input_dir)

    for nome_tabela, df in tabelas.items():
        if nome_tabela == 'clientes':
            clientes_df = normaliza_datas(df, 'updated_at')
            clientes_df = deduplicar_dimensao(clientes_df, 'cliente_id', 'updated_at')
        elif nome_tabela == 'vendas':
            vendas_df = normaliza_datas(df, 'data')
            vendas_df = normaliza_valores_numericos(vendas_df, 'valor')
            vendas_df = normaliza_valores_numericos(vendas_df, 'quantidade')
            vendas_df = fato_diario(vendas_df)

    df_diario = vendas_df.merge(clientes_df[['cliente_id']], on='cliente_id', how='inner')
    df_diario = df_diario.rename(columns={'data_formatada': 'dt'})
    df_diario = df_diario[['dt', 'cliente_id', 'valor_total']]  


    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    df_diario.to_csv(f"{args.output_dir}/diario.csv", index=False)
    logging.info(f"diario.csv salvo com {len(df_diario)} registros.")

