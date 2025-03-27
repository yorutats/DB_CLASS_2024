from typing import Optional
import psycopg2
from psycopg2 import pool
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
from flask import flash

DB_USER = os.getenv('USER')
DB_HOST = os.getenv('HOST')
DB_PORT = os.getenv('PORT')
DB_PASSWORD = os.getenv('PASSWORD')
DB_NAME = os.getenv('DB')


class DB:
    connection_pool = pool.SimpleConnectionPool(
        1, 100,  # 最小和最大連線數
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port= DB_PORT,
        dbname=DB_NAME
    )

    @staticmethod
    def connect():
        return DB.connection_pool.getconn()

    @staticmethod
    def release(connection):
        DB.connection_pool.putconn(connection)

    @staticmethod
    def execute_input(sql, input):
        if not isinstance(input, (tuple, list)):
            raise TypeError(f"Input should be a tuple or list, got: {type(input).__name__}")
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, input)
                connection.commit()
        except psycopg2.Error as e:
            print(f"Error executing SQL: {e}")
            connection.rollback()
            raise e
        finally:
            DB.release(connection)

    @staticmethod
    def execute(sql):
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql)
        except psycopg2.Error as e:
            print(f"Error executing SQL: {e}")
            connection.rollback()
            raise e
        finally:
            DB.release(connection)

    @staticmethod
    def fetchall(sql, input=None):
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, input)
                return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Error fetching data: {e}")
            raise e
        finally:
            DB.release(connection)

    @staticmethod
    def fetchone(sql, input=None):
        connection = DB.connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, input)
                return cursor.fetchone()
        except psycopg2.Error as e:
            print(f"Error fetching data: {e}")
            raise e
        finally:
            DB.release(connection)


class Member:
    @staticmethod
    def get_member(account):
        sql = "SELECT account, password, mid, identity, name FROM member WHERE account = %s"
        return DB.fetchall(sql, (account,))

    @staticmethod
    def get_all_account():
        sql = "SELECT account FROM member"
        return DB.fetchall(sql)
    
    @staticmethod
    def get_all_mid():
        sql = "SELECT MID FROM member"
        return DB.fetchall(sql)
    
    @staticmethod
    def get_all_username():
        sql = "SELECT name FROM member"
        return DB.fetchall(sql)

    @staticmethod
    def create_member(input_data):
        sql = 'INSERT INTO member (MID, name, account, password, identity) VALUES (%s, %s, %s, %s, %s)'
        DB.execute_input(sql, (input_data['mid'], input_data['name'], input_data['account'], input_data['password'], input_data['identity']))

    @staticmethod
    def delete_product(tno, pid):
        sql = 'DELETE FROM record WHERE tno = %s and pid = %s'
        DB.execute_input(sql, (tno, pid))

    @staticmethod
    def get_order(userid):
        sql = 'SELECT * FROM order_list WHERE mid = %s ORDER BY ordertime DESC'
        return DB.fetchall(sql, (userid,))

    @staticmethod
    def get_role(userid):
        sql = 'SELECT identity, name FROM member WHERE mid = %s'
        return DB.fetchone(sql, (userid,))


class Cart:
    @staticmethod
    def check(user_id):
        sql = '''SELECT * FROM cart, record 
                 WHERE cart.mid = %s::bigint 
                 AND cart.tno = record.tno::bigint'''
        return DB.fetchone(sql, (user_id,))

    @staticmethod
    def get_cart(user_id):
        sql = 'SELECT * FROM cart WHERE mid = %s'
        return DB.fetchone(sql, (user_id,))

    @staticmethod
    def add_cart(user_id, time):
        sql = 'INSERT INTO cart (mid, carttime, tno) VALUES (%s, %s, nextval(\'cart_tno_seq\'))'
        DB.execute_input(sql, (user_id, time))

    @staticmethod
    def clear_cart(user_id):
        sql = 'DELETE FROM cart WHERE mid = %s'
        DB.execute_input(sql, (user_id,))

class Customer:
    @staticmethod
    def add_customer(mid, userName, userPhone):
        sql = 'INSERT INTO customer (cId, cName, phone) VALUES (%s, %s, %s)'
        DB.execute_input(sql, (
            mid,
            userName, 
            userPhone,
        ))
    
    @staticmethod
    def get_all_customer():
        sql = 'SELECT * FROM customer'
        try:
            return DB.fetchall(sql)
        except:
            return "error"
    
    @staticmethod
    def delete_customer(cid):
        sql = 'DELETE FROM customer WHERE cId = %s'
        try:
            DB.execute_input(sql, (cid,))
        except:
            return "error"

    @staticmethod
    def get_order(cid):
        sql = 'SELECT * FROM "order" WHERE cid = %s ORDER BY ordertime DESC'
        return DB.fetchall(sql, (cid,))
        
class Supplier:
    @staticmethod
    def get_supplier(sId):
        sql = 'SELECT * FROM Supplier WHERE sId = %s'
        return DB.fetchone(sql, (sId,))
    
    @staticmethod
    def get_all_supplier():
        print("show")
        sql = 'SELECT * FROM supplier'
        return DB.fetchall(sql)
    
    @staticmethod
    def add_supplier(input_data):
        print("hihihihi")
        sql = 'INSERT INTO supplier (sId, sName, phone, rating) VALUES (%s, %s, %s, %s)'
        DB.execute_input(sql, (
            input_data['sId'],
            input_data['sName'], 
            input_data['phone'],
            input_data['rating'],
        ))
        
    @staticmethod
    def update_supplier(input_data):
        sql = 'UPDATE supplier SET sId = %s, sName = %s, phone = %s, rating = %s WHERE sId = %s'
        DB.execute_input(sql, (input_data['sId'], input_data['sName'], input_data['phone'], input_data['rating'], input_data['sId']))
                
    @staticmethod
    def delete_supplier(sid):
        sql = 'DELETE FROM supplier WHERE sId = %s'
        try:
            DB.execute_input(sql, (sid,))
        except:
            return "error"

class Bird:
    @staticmethod
    def count():
        sql = 'SELECT COUNT(*) FROM bird'
        return DB.fetchone(sql)

    @staticmethod
    def get_product(bid):
        sql = 'SELECT * FROM bird WHERE bid = %s'
        return DB.fetchone(sql, (bid,))

    @staticmethod
    def get_all_product():
        sql = 'SELECT * FROM bird'
        return DB.fetchall(sql)

    @staticmethod
    def get_species(bid):
        sql = 'SELECT species FROM bird WHERE bid = %s'
        return DB.fetchone(sql, (bid,))[0]

    @staticmethod
    def add_bird(input_data):
        sql = 'INSERT INTO bird (bId, sId, gId, bDesc, species, price, stock) VALUES (%s, %s, %s, %s, %s, %s, %s)'
        DB.execute_input(sql, (
            input_data['bId'],
            input_data['sId'], 
            input_data['gId'],
            input_data['bDesc'],
            input_data['species'],
            input_data['price'],
            input_data['stock']
        ))
        
    @staticmethod
    def delete_bird(bid):
        sql = 'DELETE FROM bird WHERE bid = %s'
        DB.execute_input(sql, (bid,))

    @staticmethod
    def update_bird(input_data):
        sql = 'UPDATE bird SET sId = %s, gId = %s, bDesc = %s, species = %s, price = %s, stock = %s WHERE bid = %s'
        DB.execute_input(sql, (input_data['sId'], input_data['gId'], input_data['bDesc'], input_data['species'], input_data['price'], input_data['stock'], input_data['bid']))


class Record:
    @staticmethod
    def get_total_money(tno):
        sql = 'SELECT SUM(total) FROM record WHERE tno = %s'
        return DB.fetchone(sql, (tno,))[0]

    @staticmethod
    def check_product(pid, tno):
        sql = 'SELECT * FROM record WHERE pid = %s and tno = %s'
        return DB.fetchone(sql, (pid, tno))

    @staticmethod
    def get_price(pid):
        sql = 'SELECT price FROM product WHERE pid = %s'
        return DB.fetchone(sql, (pid,))[0]

    @staticmethod
    def add_product(input_data):
        print("22")
        sql = 'INSERT INTO record (pid, tno, amount, saleprice, total) VALUES (%s, %s, 1, %s, %s)'
        print(sql)
        DB.execute_input(sql, (input_data['pid'], input_data['tno'], input_data['saleprice'], input_data['total']))

    @staticmethod
    def get_record(tno):
        sql = 'SELECT * FROM record WHERE tno = %s'
        return DB.fetchall(sql, (tno,))

    @staticmethod
    def get_amount(tno, pid):
        sql = 'SELECT amount FROM record WHERE tno = %s and pid = %s'
        return DB.fetchone(sql, (tno, pid))[0]

    @staticmethod
    def update_product(input_data):
        sql = 'UPDATE record SET amount = %s, total = %s WHERE pid = %s and tno = %s'
        DB.execute_input(sql, (input_data['amount'], input_data['total'], input_data['pid'], input_data['tno']))

    @staticmethod
    def delete_check(pid):
        sql = 'SELECT * FROM record WHERE pid = %s'
        return DB.fetchone(sql, (pid,))

    @staticmethod
    def get_total(tno):
        sql = 'SELECT SUM(total) FROM record WHERE tno = %s'
        return DB.fetchone(sql, (tno,))[0]


class Order:
    @staticmethod
    def add_order(input_data):
        sql = 'INSERT INTO "order" (cid, ordertime, totalAmount) VALUES (%s, TO_TIMESTAMP(%s, \'YYYY-MM-DD HH24:MI:SS\'), %s)'
        DB.execute_input(sql, (input_data['cid'], input_data['ordertime'], input_data['totalAmount']))

    @staticmethod
    def get_order():
        sql = '''
            SELECT 
                o.cId, 
                c.cName,
                o.totalAmount, 
                o.orderTime
            FROM "order" o
            JOIN Customer c 
                ON o.cId = c.cId
            ORDER BY o.orderTime DESC
        '''
        return DB.fetchall(sql)

    @staticmethod
    def get_orderdetail():
        sql = '''
        SELECT 
            o.cId, 
            o.orderTime, 
            b.species, 
            r.subAmount, 
            r.rNum
        FROM "order" o
        JOIN record r 
            ON o.cId = r.cId AND o.orderTime = r.orderTime
        JOIN bird b 
            ON r.bId = b.bId
        '''
        return DB.fetchall(sql)


class Analysis:
    @staticmethod
    def month_price(i):
        sql = 'SELECT EXTRACT(MONTH FROM ordertime), SUM(price) FROM order_list WHERE EXTRACT(MONTH FROM ordertime) = %s GROUP BY EXTRACT(MONTH FROM ordertime)'
        return DB.fetchall(sql, (i,))

    @staticmethod
    def month_count(i):
        sql = 'SELECT EXTRACT(MONTH FROM ordertime), COUNT(oid) FROM order_list WHERE EXTRACT(MONTH FROM ordertime) = %s GROUP BY EXTRACT(MONTH FROM ordertime)'
        return DB.fetchall(sql, (i,))

    @staticmethod
    def category_sale():
        sql = 'SELECT SUM(total), category FROM product, record WHERE product.pid = record.pid GROUP BY category'
        return DB.fetchall(sql)

    @staticmethod
    def member_sale():
        sql = 'SELECT SUM(price), member.mid, member.name FROM order_list, member WHERE order_list.mid = member.mid AND member.identity = %s GROUP BY member.mid, member.name ORDER BY SUM(price) DESC'
        return DB.fetchall(sql, ('user',))

    @staticmethod
    def member_sale_count():
        sql = 'SELECT COUNT(*), member.mid, member.name FROM order_list, member WHERE order_list.mid = member.mid AND member.identity = %s GROUP BY member.mid, member.name ORDER BY COUNT(*) DESC'
        return DB.fetchall(sql, ('user',))
