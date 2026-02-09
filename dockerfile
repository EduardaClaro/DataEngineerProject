FROM apache/airflow:3.1.0

USER root

# Instalar Java (necessário para PySpark)
# - Atualiza lista de pacotes
# - Instala OpenJDK 17 sem pacotes recomendados adicionais para economizar espaço
# - Limpa cache do apt para reduzir tamanho da imagem final
RUN apt-get update && \
    apt-get install -y --no-install-recommends openjdk-17-jdk-headless && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Configura variável de ambiente JAVA_HOME apontando para instalação do Java
# Necessário para que o PySpark encontre o Java
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-arm64

USER airflow

# Instala PySpark versão 3.5.1
# --no-cache-dir: não mantém cache de instalação para economizar espaço
RUN pip install --no-cache-dir pyspark==3.5.1