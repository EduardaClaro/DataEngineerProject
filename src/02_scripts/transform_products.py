import os # importacao p/ manipular arquivos e diretorios
import logging # importacao p/ configurar o logging
from datetime import datetime # importacao p/ manipular datas
from pyspark.sql import SparkSession # importacao p/ manipular dados com Spark
from pyspark.sql.functions import col, round as spark_round, explode # importacao p/ funcoes do Spark
# Mover arquivo CSV para arquivo único
import glob # importacao p/ buscar arquivos com padrao
import shutil # importacao p/ mover arquivos

# Configuracao do logging
logging.basicConfig(level=logging.INFO) # logging para informar o progresso
logger = logging.getLogger(__name__) # logger para a configuracao atual


def transform_products(input_path, output_path): # define a funcao com paramentros
# input_path: caminho do arquivo JSON de entrada
# output_path: caminho onde o CSV sera salvo
    """Lê JSON, transforma e salva em CSV"""
    
    spark = SparkSession.builder.appName("ProductsTransformation").getOrCreate() # iniciando a sessao Spark
    
    try:
        # Ler JSON
        logger.info(f"Lendo: {input_path}") # log do caminho do arquivo JSON
        df = spark.read.option("multiLine", "true").json(input_path) # criando uma variavel para ler o JSON
        
        # Extrair array de produtos usando explode
        products_df = df.select(explode("products").alias("product")).select("product.*") # extrai o array de produtos e renomeia a coluna
        
        logger.info(f"Produtos lidos: {products_df.count()}") # log do numero de produtos lidos
        
        # Transformar e selecionar colunas
        result = products_df.select( # seleciona as colunas desejadas
            "id", "title", "category", "brand", "price", "rating", "stock", 
            spark_round(col("price") * (1 - col("discountPercentage") / 100), 2).alias("price_with_discount") 
        )
        
        # Salvar CSV único na pasta processed
        logger.info(f"Salvando CSV em: {output_path}") 
        
        # Criar diretório se não existir
        output_dir = os.path.dirname(output_path) # verifica o diretório de saída
        if output_dir: # verifica se o diretório existe
            os.makedirs(output_dir, exist_ok=True) # cria o diretório se não existir
        
        # Salvar em diretório temporário
        temp_dir = f"{output_path}_temp" # cria um diretório temporário para salvar o CSV
        result.coalesce(1).write.mode("overwrite").option("header", "true").csv(temp_dir) # salva o resultado em um CSV com cabeçalho
        
        csv_files = glob.glob(f"{temp_dir}/part-*.csv") # busca arquivos CSV no diretório temporário
        if csv_files: # verifica se existem arquivos CSV
            # Remover arquivo se já existe (idempotência)
            if os.path.exists(output_path): # verifica se o arquivo de saída já existe
                os.remove(output_path) # remove o arquivo existente
            
            shutil.move(csv_files[0], output_path) # move o primeiro arquivo CSV encontrado para o caminho de saída
            shutil.rmtree(temp_dir) # remove o diretório temporário
            logger.info(f"CSV salvo com sucesso: {output_path}") # log do caminho onde o CSV foi salvo
        
        logger.info(f"Linhas processadas: {result.count()}") # log do numero de linhas processadas
        
    finally:
        spark.stop() # fechado a sessão Spark


if __name__ == "__main__":
    INPUT_PATH = os.getenv("INPUT_PATH", "/opt/airflow/data/raw/products.json") # puxa o caminho do arquivo JSON de entrada
    OUTPUT_PATH = os.getenv("OUTPUT_PATH", "/opt/airflow/data/processed/products.csv") # puxa o caminho do arquivo CSV de saída
    
    transform_products(INPUT_PATH, OUTPUT_PATH) # chama a funcao para transformar os produtos e salvar o CSV