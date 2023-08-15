from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.macros import ds_add
import pendulum
from os.path import join
import pandas as pd


with DAG(
    "dados_climaticos",
    start_date=pendulum.datetime(2022, 12, 31, tz="UTC"),
    schedule_interval='0 0 * * 1', # executar toda segunda feira
) as dag:

    tarefa_1 = BashOperator(
        task_id = 'cria_pasta_mes_ano',
        bash_command = 'mkdir -p "/home/guilherme/airflow/dados/semana={{data_interval_end.strftime("%Y-%m")}}"'
    )
    
    tarefa_2 = BashOperator(
        task_id = 'cria_pasta_semana',
        bash_command= 'mkdir -p "/home/guilherme/airflow/dados/semana={{data_interval_end.strftime("%Y-%m")}}/{{data_interval_end.strftime("%Y-%m-%d")}}"'
    )

    def extrai_dados(data_interval_end, data_intervel_year_month):
        city = 'SaoPaulo'
        key = 'T2XTZC7KHRQM67DA2VND5UV2U'

        URL = join('https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/',
            f'{city}/{data_interval_end}/{ds_add(data_interval_end, 7)}?unitGroup=metric&include=days&key={key}&contentType=csv')

        dados = pd.read_csv(URL)

        file_path = f'/home/guilherme/airflow/dados/semana={data_intervel_year_month}/{data_interval_end}/'

        dados.to_csv(file_path + 'dados_brutos.csv')
        dados[['datetime','tempmin', 'temp', 'tempmax']].to_csv(file_path + 'temperaturas.csv')
        dados[['datetime', 'description', 'icon']].to_csv(file_path + 'condicoes.csv')

    tarefa_2 = PythonOperator(
        task_id = 'extrai_dados',
        python_callable = extrai_dados,
        op_kwargs = {'data_interval_end': '{{data_interval_end.strftime("%Y-%m-%d")}}', 'data_intervel_year_month': '{{data_interval_end.strftime("%Y-%m")}}'}
    )

    tarefa_1 >> tarefa_2
