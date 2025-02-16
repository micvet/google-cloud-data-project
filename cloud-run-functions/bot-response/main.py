import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.cloud import bigquery
import logging

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Configuração de logging
logging.basicConfig(level=logging.INFO)

# Variáveis de ambiente
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
BQ_TABLE = os.getenv("BQ_TABLE")
MODEL = "gemini-2.0-flash-001"

def generate_query(user_question):
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

    text = types.Part.from_text(text=f"""Você é um assistente que gera queries SQL para consultar dados de asteroides. Não responda mais nada além da query.
    A tabela possui os seguintes campos:
    - name (STRING): Nome do asteroide
    - date (DATE): Data da observação
    - id (STRING): ID do asteroide
    - is_hazardous (BOOLEAN): Indica se o asteroide é perigoso
    - diameter_min_km (FLOAT): Diâmetro mínimo em km
    - diameter_max_km (FLOAT): Diâmetro máximo em km
    - velocity_km_s (FLOAT): Velocidade em km/s
    - miss_distance_km (FLOAT): Distância da Terra em km
    - close_approach_date (DATE): Data da maior aproximação

    Gere uma query SQL para responder adequadamente a seguinte pergunta:
    {user_question}.

    Exemplo: Se a pergunta for "qual o asteroide mais rápido de 2024?", gere uma query que retorne o nome do asteroide e sua velocidade.
    
    Use a tabela {BQ_TABLE}.
    """)

    contents = [types.Content(role="user", parts=[text])]

    generate_content_config = types.GenerateContentConfig(
        temperature=0.2,
        top_p=0.95,
        max_output_tokens=1024,
        response_modalities=["TEXT"],
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF")
        ],
        system_instruction=[types.Part.from_text(text="Gere apenas a query SQL solicitada.")]
    )

    result = ""
    for chunk in client.models.generate_content_stream(
        model=MODEL, contents=contents, config=generate_content_config
    ):
        result += chunk.text

    query = result.replace("```sql", "").replace("```", "").strip()
    return query


def execute_query(query):
    client = bigquery.Client()
    query_job = client.query(query)
    results = query_job.result()
    return [dict(row) for row in results]


def generate_response(result, user_question):
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=LOCATION)

    text = types.Part.from_text(text=f"""Você é um assistente que responde perguntas sobre asteroides com base em resultados de consultas SQL.
    Pergunta: {user_question}
    Resultado da consulta: {result}

    Formule uma resposta clara com base nesses dados.
    """)

    contents = [types.Content(role="user", parts=[text])]

    generate_content_config = types.GenerateContentConfig(
        temperature=0.2,
        top_p=0.95,
        max_output_tokens=512,
        response_modalities=["TEXT"]
    )

    response = ""
    for chunk in client.models.generate_content_stream(
        model=MODEL, contents=contents, config=generate_content_config
    ):
        response += chunk.text

    return response.strip()


def banco_dados(request):
    try:
        data = request.get_json()
        user_question = data.get("question")
        logging.info(f"Received question: {user_question}")

        query = generate_query(user_question)
        logging.info(f"Generated query: {query}")

        results = execute_query(query)
        response = generate_response(results, user_question)

        return {"answer": response}

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {"error": str(e)}, 500
