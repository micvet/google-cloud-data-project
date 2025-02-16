# Cloud Functions

Este diretório contém as funções do Google Cloud Functions que executam o pipeline de dados do projeto. Elas são responsáveis pela coleta, transformação, armazenamento e por fim, consulta dos dados sobre asteroides.

## Estrutura das Funções

Cada subpasta representa uma função específica e contém:

1. main.py → Código-fonte principal da função. O nome da função principal define o ponto de entrada.
2. requirements.txt → Dependências necessárias para rodar a função.
3. .env → Arquivo de variáveis de ambiente para configuração.

## Configuração
1. Configurar as Variáveis de Ambiente
Antes de implantar as funções, defina as variáveis necessárias no arquivo .env.

Exemplo de .env:

```
PROJECT_ID=meu-projeto
NASA_API_KEY=sua_chave_api
RAW_BUCKET=meu-bucket-raw
TRANSFORMED_BUCKET=meu-bucket-transformed
BQ_DATASET=asteroids_dataset
```
2. Implantar Funções no GCP
Cada função deve ser implantada manualmente via gcloud. Você pode realizar o upload das pastas e usar o seguinte comando dentro da subpasta correspondente:

```
gcloud functions deploy <nome-da-funcao> \
  --runtime python39 \
  --trigger-http \
  --allow-unauthenticated \
  --set-env-vars $(cat .env | xargs)
```
<br>

As funções deste projeto foram provisionadas via front:

1. <br> <img src="https://github.com/user-attachments/assets/64eec587-cf4d-42ba-9b3c-4699251f9415" width="900"/> <br> <br>

## Funções Disponíveis <br>

### 1. fetch_asteroids_data
Descrição: Obtém dados da API da NASA e salva no bucket RAW.
Ponto de entrada: fetch_asteroids_data
Saída: CSV no Cloud Storage

**Fluxo de Execução:**

* Carregamento de Variáveis de Ambiente

O arquivo .env armazena credenciais sensíveis, como NASA_API_KEY e GCP_BUCKET_NAME.
A biblioteca dotenv é utilizada para carregar essas variáveis no ambiente de execução.

* Consulta à API da NASA

A função obtém asteroides detectados no dia anterior. 
Faz uma requisição à API da NASA no endpoint /neo/rest/v1/feed, enviando start_date, end_date e a chave da API como parâmetros. <br>

* Processamento dos Dados

Caso a resposta da API seja bem-sucedida (status_code == 200), os dados são extraídos e armazenados em uma lista de dicionários, cada um representando um asteroide. <br>

São extraídos os seguintes campos: <br>
* name: Nome do asteroide.
* date: Data da observação.
* id: Identificador único do asteroide.
* is_hazardous: Indica se é classificado como potencialmente perigoso.
* diameter_min_km e diameter_max_km: Diâmetro estimado em quilômetros.
* close_approach_date: Data da maior aproximação à Terra.
* velocity_km_s: Velocidade relativa em km/s.
* miss_distance_km: Distância mínima da Terra em km.

* Armazenamento no Cloud Storage

Os dados são convertidos em um DataFrame Pandas e salvos como um arquivo CSV (raw-asteroids-YYYY-MM-DD.csv).
O arquivo gerado é enviado para um Google Cloud Storage Bucket, onde ficará armazenado para processamento posterior.

### 2. transform-data
Descrição: Processa os dados e os armazena no bucket TRANSFORMED.
Ponto de entrada: transform_data
Saída: CSV transformado no Cloud Storage

**Fluxo de Execução**
Carregamento de Variáveis de Ambiente

O arquivo .env contém as credenciais e os nomes dos buckets do GCS:
- GCP_RAW_BUCKET_NAME: Bucket onde os dados brutos estão armazenados.
- GCP_TRANSFORMED_BUCKET_NAME: Bucket onde os dados transformados serão salvos.
A biblioteca dotenv é utilizada para carregar essas configurações.

* Definição da Data

A função processa os dados do dia anterior à execução, utilizando datetime.now() - timedelta(days=1).
Os arquivos seguem o padrão:
Bruto: raw-asteroids-YYYY-MM-DD.csv
Transformado: transformed-asteroids-YYYY-MM-DD.csv

* Download dos Dados do Bucket Bruto

A função inicializa um cliente do Google Cloud Storage e acessa o bucket de dados brutos.
O arquivo CSV correspondente à data de ontem é baixado e carregado em um DataFrame Pandas.

* Transformações Aplicadas

* Os dados passam por um refinamento antes de serem armazenados:

- Arredondamento:
velocity_km_s → 2 casas decimais.
miss_distance_km → Arredondado para número inteiro.
diameter_min_km e diameter_max_km → 3 casas decimais.
- Conversão de tipos:
date e close_approach_date → Convertidos para datetime.
name e id → Convertidos para string.

* Armazenamento dos Dados Transformados

O DataFrame é salvo localmente como um arquivo CSV temporário.
Esse arquivo é então enviado para o bucket de dados transformados (GCP_TRANSFORMED_BUCKET_NAME).

### 3. load_data_bq
Descrição: Carrega os dados processados para o BigQuery.
Ponto de entrada: load_to_bigquery
Saída: Dados na tabela do BigQuery

**Fluxo de Execução**

* Carregamento de Variáveis de Ambiente:

Utiliza a biblioteca dotenv para carregar variáveis sensíveis armazenadas em um arquivo .env, como o nome do bucket do Google Cloud Storage e a tabela do BigQuery.

* Processamento de Dados:

A função é configurada para ser executada levando em conta a data de "ontem"(yesterday) sendo calculada para nomear o arquivo a ser processado.
Um arquivo CSV gerado anteriormente, com os dados transformados dos asteroides, é baixado do bucket do Google Cloud Storage usando a biblioteca google.cloud.storage.

* Leitura e Transformação:

O conteúdo do arquivo CSV é lido em um DataFrame do Pandas, permitindo que os dados sejam manipulados ou validados antes de serem carregados.

* Carregamento para BigQuery:

A função cria uma configuração de trabalho (job_config) para carregar os dados no BigQuery, com a opção de detectar automaticamente os tipos de dados e permitir a escrita de dados de forma incremental na tabela (WRITE_APPEND).
A função load_table_from_dataframe é usada para carregar os dados diretamente do DataFrame do Pandas para a tabela BigQuery especificada.

* Tratamento de Erros:

Caso ocorra algum erro durante o processo, ele é capturado e a função retorna uma mensagem de erro com código 500. Em caso de sucesso, a função retorna uma mensagem de confirmação com código 200.

### 4. bot-response
Descrição: Responde perguntas do chatbot, gerando queries para o BigQuery, tudo via Vertex AI.
Ponto de entrada: banco_dados
Saída: Resposta formatada para o usuário

**Fluxo de Execução**

* Carregamento de Variáveis de Ambiente:
Utiliza a biblioteca dotenv para carregar variáveis de ambiente do arquivo .env, como o ID do projeto, a localização e a tabela do BigQuery.

* Função generate_query(user_question):

A função recebe uma pergunta do usuário (no presente projeto essa requisição é enviada pelo Dialog Flow CX) e utiliza o modelo gemini-2.0-flash-001 da Google Vertex AI para gerar uma consulta SQL.
O modelo é alimentado com um conjunto de instruções sobre a estrutura da tabela de asteroides e a pergunta do usuário, pedindo para gerar apenas a consulta SQL.
As perguntas podem ser sobre qualquer aspecto dos dados dos asteroides, como velocidade, distância de aproximação, etc.
A consulta SQL gerada é extraída do texto retornado pelo modelo e preparada para ser executada.

* Função execute_query(query):

Esta função executa a consulta SQL gerada usando a API do BigQuery.
A consulta é executada e os resultados são coletados e retornados no formato de uma lista de dicionários.

* Função generate_response(result, user_question):

Após a execução da consulta, o modelo Vertex AI é chamado novamente para gerar uma resposta natural baseada nos resultados obtidos.
O modelo é configurado para criar uma resposta clara, combinando os resultados da consulta com a pergunta original.

* Função banco_dados(request):

Esta é a função principal chamada pelo Google Cloud Functions quando o endpoint é acessado.
A função recebe a pergunta do usuário em formato JSON, chama as funções generate_query, execute_query e generate_response, e retorna uma resposta contendo a resposta gerada.
Se ocorrer algum erro durante o processo, ele é registrado e um erro é retornado ao usuário.

## Boas Práticas <br>
1. Utilizar arquivos .env para configurar credenciais e variáveis.
   
2. Mantenha as dependências organizadas no requirements.txt.
