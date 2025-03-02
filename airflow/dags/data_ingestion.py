import pandas as pd
import shutil
from airflow.models import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from random import choice
import os

def read_data(**kwargs):
    raw_data_folder = '/opt/airflow/raw_data'
    tot_dir_files = os.listdir(raw_data_folder)
    
    if not tot_dir_files:
        raise ValueError("No files in the folder")
    
    file_name = choice(tot_dir_files)
    file_path = os.path.join(raw_data_folder, file_name)
    df = pd.read_csv(file_path)
    
    ti = kwargs['ti']
    ti.xcom_push(key='file_path', value=file_path)
    ti.xcom_push(key='file_name', value=file_name)
    
    return df

def save_data(**kwargs):
    ti = kwargs['ti']
    file_path = ti.xcom_pull(key='file_path')
    file_name = ti.xcom_pull(key='file_name')

    processed_data_folder = '/opt/airflow/processed_data'
    destination_path = os.path.join(processed_data_folder,file_name)
    shutil.move(file_path, destination_path)

    ti.xcom_push(key='processed_data_data', value=destination_path)



with DAG(
    dag_id="Read_data_and_move_data",
    description="Reading data from raw data folder",
    schedule_interval="*/10 * * * *",
    start_date=datetime(2024, 9, 15),
    catchup=False,
) as dag:
    
    Reading_file = PythonOperator(
        task_id="Read_dataset_files",
        python_callable=read_data,
        provide_context=True
    )

    moving_file = PythonOperator(
        task_id = "Move_data_to_processed_folder",
        python_callable=save_data,
        provide_context=True
    )

    Reading_file >> moving_file




