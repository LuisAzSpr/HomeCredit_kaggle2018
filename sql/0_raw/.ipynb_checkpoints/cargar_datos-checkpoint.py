from google.cloud import bigquery
import pandas as pd
import numpy as np
from google.api_core.exceptions import NotFound


def cargar_csv_a_bigquery(uri, dataset_id, tabla_id, autodetect=True):
    client = bigquery.Client()
    
    tabla_ref = client.dataset(dataset_id).table(tabla_id)
    
    # verificamos si la tabla existe previamente ...
    try:
        client.get_table(tabla_ref)
        print(f"⚠️ La tabla {dataset_id}.{tabla_id} ya existe. Saltando carga.")
        return
    except NotFound:
        # la tabla no existe → procedemos a cargar
        pass
    
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
    
if __name__=='__main__':
    uri = 'gs://home-credit-risk-data-bucket/data/{}.csv'
    tablas = [
        'application_train','bureau','bureau_balance',
        'installments_payments','previous_application',
        'POS_CASH_balance','credit_card_balance'
    ]
    
    for tabla in tablas:
        uri_bucket = uri.format(tabla)
        dataset_id = 'homecredit_raw'
        cargar_csv_a_bigquery(uri_bucket, dataset_id, tabla)

    
    