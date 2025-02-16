# GCP Data Project - Asteroid Data Pipeline

## Descrição

Este projeto tem como objetivo colocar em prática os conhecimentos adquiridos na trilha de estudos [Associate Data Practitioner Learning](https://partner.cloudskillsboost.google/paths/1337), para a certificação Data Practitioner do Google Cloud, e da trilha de estudos [Airflow 101](https://academy.astronomer.io/path/airflow-101), para a certificação Airflow Fundamentals. O objetivo foi, usando as ferramentas estudadas, criar um pipeline de dados capaz de coletar, processar e disponibilizar dados para o usuário final. Os dados no projeto foram consumidos por meio de uma API da NASA, que disponibiliza dados sobre asteroides próximos à Terra.

## Arquitetura

O projeto é composto por:

* Coleta de dados: Uma função no Cloud Functions chama a API da NASA e armazena os dados brutos (raw) em um bucket no Cloud Storage;

* Transformação de dados: Uma segunda função processa os dados (ajustes data type, arredondamento, etc.) e os armazena em outro bucket para dados tratados;

* Carregamento para BigQuery: Uma terceira função insere os dados processados em uma tabela criada no BigQuery;

* Orquestração: O Cloud Composer (Airflow) aciona as funções diariamente, realizando o ordenamento e o controle de sucesso/falha;

* Chatbot: Um chatbot foi criado utilizando o Vertex AI Agent Builder e sua ferramenta de Playbooks, permitindo interação natural com o usuário. Quando o usuário realiza questionamentos sobre o tema proposto, é enviada uma requisição API para um função hospedada no Cloud Functions, contruída com o objetivo de buscar a resposta. A resposta é então enviada para o Playbook, que a transmite em linguagem acessível para o usuário;

* Processamento do questionamento do usuário final: função no Cloud Functions que recebe perguntas do usuário realizadas em interações com o ChatBot e utiliza Vertex AI para interpretar o questionamento e gerar queries para o BigQuery, executa as consultas e utiliza novamente o Vertex AI para transcrever a resposta para uma linguagem amigável;

* Interface Web: Uma página simples para demonstrar o acesso ao chatbot.   

![image](https://github.com/user-attachments/assets/592d27e4-1798-46c8-970c-0bce286053f1)


### Tecnologias Utilizadas

* Google Cloud Platform: Cloud Functions, Cloud Storage, BigQuery, Cloud Composer (Apache AirFlow), Vertex AI Agent Builder: Para o chatbot, Vertex AI: Para gerar e interpretar queries do BigQuery;

* Python: Linguagem principal

* HTML/CSS: Interface web

## Estrutura do Repositório

```
/gcp-data-project
│── README.md                       # Documentação principal do projeto
│
├── chatbot
│   ├── exported_agent_asteroide-chatbot.blob         # Configuração do agente Dialogflow CX
│   ├── Asteroid-QueryAPI.yaml       # API utilizada como ferramenta no Playbook do chatbot
│   ├── README.md                    # Documentação específica do chatbot
│
├── cloud-functions
│   ├── fetch-asteroids-data-function
│   │   ├── main.py                  # Coleta os dados da API da NASA
│   │   ├── .env                     # Personaliza variáveis de ambiente, garantindo a correta configuração do projeto 
│   │   ├── requirements.txt
│   ├── transform-data
│   │   ├── main.py                  # Transforma os dados
│   │   ├── .env                     # Personaliza variáveis de ambiente, garantindo a correta configuração do projeto 
│   │   ├── requirements.txt
│   ├── load-to-bq
│   │   ├── main.py                  # Carrega os dados para o BigQuery
│   │   ├── .env.example             # Exemplo de configuração
│   │   ├── requirements.txt
│   ├── bot-response
│   │   ├── main.py                  # Gera resposta do chatbot usando Vertex AI e BigQuery
│   │   ├── .env                     # Personaliza variáveis de ambiente, garantindo a correta configuração do projeto 
│   │   ├── requirements.txt
│
├── composer
│   ├── dags_asteroid-data-airflow.py # DAGs do Airflow
│   ├── airflow-monitoring.py         # Monitoramento do Composer
│   ├── README.md                    # Documentação do Composer
│
├── web-application
│   ├── index.html                   # Interface do chatbot
│   ├── df-messenger-custom.css      # Estilização do chatbot
│   ├── README.md                    # Documentação do frontend
│
 \

```
## Configuração Inicial no Google Cloud

1. Antes de rodar o pipeline, você precisa de um projeto no GCP. Se ainda não tem um, crie um com o seguinte comando:
```
gcloud projects create meu-projeto-asteroides --set-as-default
```

2. Ative as APIs necessárias:

```
gcloud services enable cloudfunctions.googleapis.com \
    cloudbuild.googleapis.com \
    composer.googleapis.com \
    bigquery.googleapis.com \
    storage.googleapis.com \
    aiplatform.googleapis.com \
    dialogflow.googleapis.com
```

3. Criando Buckets no Cloud Storage
O pipeline usa dois buckets: um para os dados brutos e outro para os dados transformados. Crie-os com:

```
gsutil mb -l US gs://meu-bucket-raw  
gsutil mb -l US gs://meu-bucket-transformed
```

Os nomes devem ser únicos.

4. Crie o dataset no BigQuery:

```
bq --location=US mk -d MEU_PROJETO:asteroids_dataset
```

Depois, crie a tabela com a estrutura correta:

```
bq mk --table MEU_PROJETO:asteroids_dataset.asteroids_table \
    name:STRING,date:DATE,id:STRING,is_hazardous:BOOLEAN, \
    diameter_min_km:FLOAT,diameter_max_km:FLOAT,velocity_km_s:FLOAT, \
    miss_distance_km:FLOAT,close_approach_date:DATE
```

**Consulte o README.md das demais aplicações para verificar as respectivas configurações.** <br>

## Visualização do Pipeline e Chatbot <br>

### Visão geral buckets <br>

1. <br> <img src="https://github.com/user-attachments/assets/16c1d1da-681b-4acb-bd0c-9fa7777adf5c" width="900"/> <br> <br>

2. <br> <img src="https://github.com/user-attachments/assets/97f5eb40-f02b-4f79-9163-151d1e4e19ab" width="900"/> <br> <br>

### Visão geral BigQuery <br>

1. <br> <img src="https://github.com/user-attachments/assets/935ba314-c099-41ef-b34a-fb794950a32e" width="900"/> <br> <br>

2. <br> <img src="https://github.com/user-attachments/assets/562b22ad-b0a3-4fdc-a3f4-25566c4dc387" width="900"/> <br> <br>

### Visão geral Cloud Functions <br>

1. <br> <img src="https://github.com/user-attachments/assets/fd101265-9027-49f8-a28d-f50482dddb86" width="900"/> <br> <br>

2. <br> <img src="https://github.com/user-attachments/assets/9dacdbc2-ab02-483d-a3af-cfe4a89e76a6" width="900"/> <br>


### Visão geral do ambiente Cloud Composer em funcionamento <br>

1. <br> <img src="https://github.com/user-attachments/assets/2a753ef6-c8ee-4abb-a32a-3c10f3bfc212" width="900"/> <br> <br>

2. <br> <img src="https://github.com/user-attachments/assets/d380ba29-7cb7-4276-ae1f-c0bac3c77b49" width="900"/> <br> <br>

3. <br> <img src="https://github.com/user-attachments/assets/263fc63e-3e44-4f4d-bca0-58d73d0d75db" width="900"/> <br> <br>

4. <br> <img src="https://github.com/user-attachments/assets/09610197-3af2-4278-9fb6-13e4a46c6c39" width="900"/> <br><br>

5. <br> <img src="https://github.com/user-attachments/assets/0f881773-7a4e-404e-a50b-cb17ea31b594" width="900"/> <br> <br>

6. <br> <img src="https://github.com/user-attachments/assets/07957583-c6ee-4643-a476-e4e042548431" width="900"/> <br> <br>

7. <br> <img src="https://github.com/user-attachments/assets/bea3aa91-9fa4-406f-a620-c6bcfc2dd5a6" width="900"/> <br> <br>


### Visão Dialog Flox CX <br>

1. <br> <img src="https://github.com/user-attachments/assets/ce9331ec-69eb-4ac3-a582-a4d5fec4239f" width="900"/> <br> <br>

2. <br> <img src="https://github.com/user-attachments/assets/72c0fee6-5b56-4797-ad62-f9f417cf3617" width="900"/> <br> <br>

3. <br> <img src="https://github.com/user-attachments/assets/d1789d54-340e-474a-90b5-1d1d77cb0529" width="900"/> <br> <br>

4. <br> <img src="https://github.com/user-attachments/assets/dc2cae31-0374-482a-9274-a102082041d9" width="900"/> <br> <br>

5. <br> <img src="https://github.com/user-attachments/assets/4cdcfb9f-f6d4-4b3f-a10c-c27e41dd9e13" width="900"/> <br> <br>

6. <br> <img src="https://github.com/user-attachments/assets/b1c39678-d479-42cf-bcef-b13b1b4b4ead" width="900"/> <br> <br>


### Visão geral da interface Web do ChatBot <br>

1. <br> <img src="https://github.com/user-attachments/assets/63aa89a1-43cb-4061-977d-10af27947d54" width="900"/> <br> <br>











