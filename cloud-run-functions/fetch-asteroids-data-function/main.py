from dotenv import load_dotenv
import requests
import pandas as pd
import os
from datetime import datetime, timedelta
from google.cloud import storage  

# Carregando variáveis de ambiente
load_dotenv()

# Obtendo valores sensíveis do .env
NASA_API_KEY = os.getenv("NASA_API_KEY")
GCP_BUCKET_NAME = os.getenv("GCP_BUCKET_NAME")


def fetch_asteroids_data(request):
    url = "https://api.nasa.gov/neo/rest/v1/feed"
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # Parâmetros da requisição
    params = {
        "start_date": yesterday,  
        "end_date": yesterday,    
        "api_key": NASA_API_KEY           
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json() 
        asteroids = []

        # Iterando sobre as datas retornadas
        for date, asteroid_list in data["near_earth_objects"].items():
            for asteroid in asteroid_list:
                asteroids.append({
                    "name": asteroid["name"],
                    "date": date,
                    "id": asteroid["id"],
                    "is_hazardous": asteroid["is_potentially_hazardous_asteroid"],
                    "diameter_min_km": asteroid["estimated_diameter"]["kilometers"]["estimated_diameter_min"],
                    "diameter_max_km": asteroid["estimated_diameter"]["kilometers"]["estimated_diameter_max"],
                    "close_approach_date": asteroid["close_approach_data"][0]["close_approach_date"],
                    "velocity_km_s": asteroid["close_approach_data"][0]["relative_velocity"]["kilometers_per_second"],
                    "miss_distance_km": asteroid["close_approach_data"][0]["miss_distance"]["kilometers"]
                })

        # Criando um DataFrame
        df = pd.DataFrame(asteroids)
        file_name = f"raw-asteroids-{yesterday}.csv"

        # Salvando o DataFrame em um arquivo CSV localmente
        df.to_csv(file_name, index=False)

        # Conectando ao Cloud Storage e fazendo o upload
        client = storage.Client()  
        bucket = client.get_bucket(GCP_BUCKET_NAME)
        blob = bucket.blob(file_name)  

        # Enviando o arquivo para o bucket
        blob.upload_from_filename(file_name)
        return f"Arquivo {file_name} enviado para o bucket {GCP_BUCKET_NAME} com sucesso!", 200
    else:
        return f"Erro ao fazer a requisição: {response.status_code}", 500
