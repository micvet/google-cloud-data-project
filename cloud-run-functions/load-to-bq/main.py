from google.cloud import storage, bigquery
import pandas as pd
from datetime import datetime, timedelta
import io
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Obter valores sensíveis do .env
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")
BQ_TABLE = os.getenv("BQ_TABLE")

def load_to_bigquery(request):
    try:
        # Data de ontem
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        file_name = f"transformed-asteroids-{yesterday}.csv"

        # Cliente do Cloud Storage
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(GCP_BUCKET_NAME)
        blob = bucket.blob(file_name)

        # Baixar o conteúdo do arquivo
        csv_data = blob.download_as_text()
        df = pd.read_csv(io.StringIO(csv_data))

        # Cliente do BigQuery
        bq_client = bigquery.Client()

        # Configuração da tabela no BigQuery
        job_config = bigquery.LoadJobConfig(
            autodetect=True,  # Detecta os tipos de dados automaticamente
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND
        )

        # Enviar os dados para o BigQuery
        job = bq_client.load_table_from_dataframe(df, BQ_TABLE, job_config=job_config)
        job.result()  # Aguarda o job ser concluído

        return {
            "message": f"Arquivo {file_name} carregado no BigQuery em {BQ_TABLE} com sucesso!"
        }, 200

    except Exception as e:
        return {
            "error": str(e)
        }, 500
