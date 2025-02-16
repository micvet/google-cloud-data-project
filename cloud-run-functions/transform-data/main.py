from google.cloud import storage, bigquery
import pandas as pd
from datetime import datetime, timedelta
import io
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Obter valores sensíveis do .env
GCP_RAW_BUCKET_NAME = os.getenv("GCP_RAW_BUCKET_NAME")
GCP_TRANSFORMED_BUCKET_NAME = os.getenv("GCP_TRANSFORMED_BUCKET_NAME")

def transform_data(request):
    try:
        # Definição da data de ontem
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        raw_file_name = f"raw-asteroids-{yesterday}.csv"
        transformed_file_name = f"transformed-asteroids-{yesterday}.csv"

        # Inicializa o cliente do Google Cloud Storage
        client = storage.Client()

        # Acessa o bucket RAW e baixa o arquivo
        raw_bucket = client.get_bucket(GCP_RAW_BUCKET_NAME)
        blob = raw_bucket.blob(raw_file_name)

        # Faz o download do conteúdo para um DataFrame
        raw_data = blob.download_as_text()
        df = pd.read_csv(io.StringIO(raw_data))

        # Aplicando as transformações nos dados
        df["velocity_km_s"] = df["velocity_km_s"].astype(float).round(2)
        df["miss_distance_km"] = df["miss_distance_km"].astype(float).round(0)
        df["diameter_min_km"] = df["diameter_min_km"].astype(float).round(3)
        df["diameter_max_km"] = df["diameter_max_km"].astype(float).round(3)
        df["date"] = pd.to_datetime(df["date"])
        df["close_approach_date"] = pd.to_datetime(df["close_approach_date"])
        df["name"] = df["name"].astype(str)
        df["id"] = df["id"].astype(str)

        # Salva o arquivo transformado temporariamente
        df.to_csv(transformed_file_name, index=False)

        # Acessa o bucket transformado e faz o upload do arquivo
        transformed_bucket = client.get_bucket(GCP_TRANSFORMED_BUCKET_NAME)
        transformed_blob = transformed_bucket.blob(transformed_file_name)
        transformed_blob.upload_from_filename(transformed_file_name)

        return {"message": f"Arquivo {transformed_file_name} enviado para o bucket {GCP_TRANSFORMED_BUCKET_NAME}."}, 200

    except Exception as e:
        return {"error": str(e)}, 500
