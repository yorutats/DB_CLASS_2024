import psycopg2

connection = psycopg2.connect(
    user='db_ta',
    password='nsysu@3024',
    host='140.117.68.66',
    port='5432',
    dbname='postgres'  # PostgreSQL 的資料庫名稱
)
cursor = connection.cursor()

