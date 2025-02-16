from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import requests
import time

# Definir argumentos padrão
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": days_ago(1),  # Evita execuções retroativas
    "email": ["SEU E-MAIL PARA NOTIFICAÇÃO DE FALHA"],  # Notificação de falha #ALTERAR
    "email_on_failure": True,  # Envia e-mail somente em falhas
    "email_on_retry": False,  # Não envia e-mail em tentativas
    "retries": 3,  # Número máximo de tentativas
    "retry_delay": timedelta(minutes=1),  # Espera 1 min antes de tentar de novo
}

dag = DAG(
    "dag_nasa_pipeline",
    default_args=default_args,
    schedule_interval="0 9 * * *",  # Executa diariamente às 9h UTC
    catchup=False,  # Evita execução retroativa
)

# Função para chamar Cloud Functions via HTTP
def trigger_cloud_function(url, **kwargs):
    for attempt in range(3):  # Tenta até 3 vezes
        try:
            response = requests.post(url, json={})
            
            if response.status_code == 200:
                print(f"Sucesso ao chamar {url}")
                return
            else:
                print(f"Erro ao chamar {url}: {response.text}")
                time.sleep(60)  # Aguarda 1 minuto antes de tentar novamente
        except Exception as e:
            print(f"Falha na chamada de {url}: {str(e)}")
            time.sleep(60)  
            
    # Se falhar todas as tentativas, levanta um erro para o Airflow capturar
    raise Exception(f"Falha ao chamar {url} após 3 tentativas")

# Definir as tarefas
fetch_task = PythonOperator(
    task_id="fetch_asteroids_data",
    python_callable=trigger_cloud_function,
    op_kwargs={"url": "URL DA SUA FUNÇÃO DE COLETA DE DADOS RAW, VIA API. SE ESTIVER HOSPEDADA NO FUNCTIONS, USE A URL FORNECIDA"}, #ALTERAR
    dag=dag,
)

transform_task = PythonOperator(
    task_id="transform_data",
    python_callable=trigger_cloud_function,
    op_kwargs={"url": "URL DA SUA FUNÇÃO DE TRANSFORMAÇÃO DE DADOS. SE ESTIVER HOSPEDADA NO FUNCTIONS, USE A URL FORNECIDA"}, #ALTERAR
    dag=dag,
)

load_task = PythonOperator(
    task_id="load_to_bigquery",
    python_callable=trigger_cloud_function,
    op_kwargs={"url": "URL DA SUA FUNÇÃO DE CARREGAMENTO DOS DADOS NO BIG QUERY. SE ESTIVER HOSPEDADA NO FUNCTIONS, USE A URL FORNECIDA"}, #ALTERAR
    dag=dag,
)

# Tarefa para enviar e-mail em caso de falha
email_alert = EmailOperator(
    task_id="email_falha",
    to="SEU E-MAIL PARA NOTIFICAÇÃO DE FALHA", #ALTERAR
    subject="Falha na DAG NASA Pipeline",
    html_content="<p>A DAG <strong>dag_nasa_pipeline</strong> falhou.</p>",
    trigger_rule="one_failed",  # Só dispara se qualquer tarefa falhar
    dag=dag,
)

# Definir a ordem de execução
fetch_task >> transform_task >> load_task

# Se qualquer uma das tasks falhar, envia um e-mail
[fetch_task, transform_task, load_task] >> email_alert
