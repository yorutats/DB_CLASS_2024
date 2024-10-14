import psycopg2

connection = psycopg2.connect(
    user='your_account',
    password='password',
    host='140.117.68.66',
    port='5432',
    dbname='DB_name'  # PostgreSQL 的資料庫名稱
)
cursor = connection.cursor()

