import os # importacao p/ manipular arquivos e diretorios
import json # importacao p/ manipular arquivos json
import logging # importacao p/ configurar o logging
from datetime import datetime # importacao p/ manipular datas
import requests # importacao p/ fazer requisicoes HTTP

# Configuracao do logging
logging.basicConfig(level=logging.INFO) # logging para informar o progresso
logger = logging.getLogger(__name__) # logger para a configuracao atual

# Criando a funcao principal para extrair os dados
def extract_products(api_url, output_path, limit=100): # define a funcao com paramentros
# api_url: puxa a url da api
# output_path: caminho onde o json sera salvo
# limit: numero maximo de produtos a serem extraidos
    """Extrai produtos da API e salva em JSON"""
    
    url = f"{api_url}/products?limit={limit}" # construcao da url completa
    logger.info(f"Extraindo dados de: {url}") # log da url de onde os dados serao extraidos
    
    response = requests.get(url, timeout=30) # faz a requisicao HTTP
    response.raise_for_status() # verifica se houve erro na requisicao
    data = response.json() # converte a resposta para JSON
    
    products_count = len(data.get('products', [])) # conta o numero de produtos extraidos
    logger.info(f"Total de produtos extraídos: {products_count}") # log do numero de produtos extraidos
    
    # Criar diretório
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Salvar JSON
    with open(output_path, 'w', encoding='utf-8') as f: # abre o arquivo para escrita
        json.dump(data, f, ensure_ascii=False, indent=2) # salva os dados em formato JSON
    
    logger.info(f"JSON salvo: {output_path}") # log do caminho onde o json foi salvo
    return output_path # retorna o caminho do arquivo salvo


if __name__ == "__main__": 
    API_URL = os.getenv("API_URL", "https://dummyjson.com") # puxa a url da api do ambiente
    OUTPUT_PATH = os.getenv("OUTPUT_PATH", "/opt/airflow/data/raw/products.json") # puxa o caminho de saida do ambiente
    
    extract_products(API_URL, OUTPUT_PATH) # chama a funcao para extrair os produtos e salvar o json

