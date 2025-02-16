# Cloud Composer <br>

Este diretório contém a configuração do Cloud Composer, serviço gerenciado do Apache Airflow usado para orquestrar o pipeline de dados do projeto. O Composer agenda e executa as funções de coleta, transformação e carregamento dos dados diariamente.

## Estrutura
- dags_asteroid-data-airflow.py → DAG principal que define a sequência de execução das funções.
- airflow-monitoring.py → Script gerado automaticamente para monitoramento do Airflow.
- README.md → Documentação da configuração e uso do Composer.

## Configuração

### Via command line: 

1. Criar um Ambiente no Cloud Composer pode ser feito via front ou via command line. Via command line: 

```
gcloud composer environments create meu-composer \
  --location us-central1 \
  --image-version composer-2.0.25-airflow-2.5.1
```
O nome e a região podem ser ajustados conforme necessário.

2. Enviar o arquivo com o DAG para o Composer
Após configurar o ambiente, envie o arquivo da DAG para o Composer:
```
gcloud composer environments storage dags import \
  --environment meu-composer \
  --location us-central1 \
  --source dags_asteroid-data-airflow.py
```
3. Acessar a Interface do Airflow
Para monitorar e gerenciar as execuções:
```
gcloud composer environments describe meu-composer \
  --location us-central1 \
  --format="value(config.airflowUri)"
```
O comando retorna a URL do Airflow, onde as DAGs podem ser visualizadas e controladas.

### Via front 

1. <br> <img src="https://github.com/user-attachments/assets/41ee9e08-e6ff-42f4-aa6b-ef8d763a533a" width="900"/> <br> <br>

O ambiente é intuitivo. Faça o upload do arquivo DAG. Também há um link disponível para verificar a interface do Apache AirFlow e acompanhar a execução do pipeline.

## Funcionamento da DAG
A DAG dags_asteroid-data-airflow.py é responsável por:

1. Acionar a função fetch_asteroids_data para obter os dados da API da NASA e armazená-los no bucket RAW.
2. Executar a função transform_data, que processa os dados e os transfere para o bucket TRANSFORMED.
3. Acionar load_data_bq, que carrega os dados para o BigQuery.
4. Registrar logs e monitorar falhas automaticamente.
   
A DAG é configurada para rodar uma vez ao dia, garantindo a atualização contínua dos dados.

## Boas Práticas

Ative notificações de erro para monitoramento eficiente..
