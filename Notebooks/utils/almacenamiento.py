
from google.cloud import bigquery
import pandas as pd
import numpy as np

def cargar_csv_a_bigquery(uri, dataset_id, tabla_id, autodetect=True):
    client = bigquery.Client()
    
    tabla_ref = client.dataset(dataset_id).table(tabla_id)
    
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        autodetect=autodetect,
        skip_leading_rows=1
    )
    
    load_job = client.load_table_from_uri(
        uri,
        tabla_ref,
        job_config=job_config
    )

    print(f"Cargando {uri} en {dataset_id}.{tabla_id}...")
    load_job.result()  # Espera a que termine
    print("✅ ¡Carga completa!")
    
def leer_csv_desde_gcs(bucket: str = "home-credit-risk-data-bucket", 
                       carpeta: str = "data",
                       archivo: str = "",
                       encoding = "latin") -> pd.DataFrame:
    ruta_gcs = f'gs://{bucket}/{carpeta}/{archivo}'
    print(f"Leyendo archivo desde: {ruta_gcs}")
    return pd.read_csv(ruta_gcs, encoding=encoding)