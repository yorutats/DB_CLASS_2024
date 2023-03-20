import cx_Oracle
cx_Oracle.init_oracle_client(lib_dir="./instantclient_19_8") # init Oracle instant client 位置
connection = cx_Oracle.connect('ebookstore', 'ebookstore2022', cx_Oracle.makedsn('140.117.69.70', 1521, service_name='ORCLPDB1'))
cursor = connection.cursor()