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

# print("Pasta de entrada:", args.input_dir)
# print("Pasta de saída:", args.output_dir)\

# def logger(name: str) -> logging.Logger:
#     """Cria um logger com o nome especificado."""
#     logger = logging.getLogger(name)
#     logger.setLevel(logging.INFO)
#     return logger


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


if __name__ == '__main__':

    tabelas = leitura_arquivos(args.input_dir)

    for nome_tabela, df in tabelas.items():
        if nome_tabela == 'clientes':
            df = normaliza_datas(df, 'updated_at')
            print(df.head())
            df = deduplicar_dimensao(df, 'cliente_id', 'updated_at')
        elif nome_tabela == 'vendas':
            df = normaliza_datas(df, 'data')
            df = normaliza_valores_numericos(df, 'valor')
            df = normaliza_valores_numericos(df, 'quantidade')

        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)

        df.to_csv(f"{args.output_dir}/{nome_tabela}_tratado.csv", index=False)
        logging.info(f"{nome_tabela}_tratado.csv salvo com sucesso.")

