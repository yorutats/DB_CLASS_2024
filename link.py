import oracledb 
connection = oracledb.connect(user='account', password='password', host='140.117.69.60', port=1521, service_name='ORCLPDB1') 
cursor = connection.cursor()
