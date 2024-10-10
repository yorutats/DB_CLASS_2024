from typing import Optional
import psycopg2
from psycopg2 import pool


class DB:
    connection_pool = pool.SimpleConnectionPool(
        1, 20,  # 最小和最大連線數
        user='db_ta',
        password='nsysu@3024',
        host='140.117.68.66',
        port='5432',
        dbname='postgres'
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
        sql = "SELECT account, password, mid, identity, name FROM public.member WHERE account = %s"
        return DB.fetchall(sql, (account,))

    @staticmethod
    def get_all_account():
        sql = "SELECT account FROM public.member"
        return DB.fetchall(sql)

    @staticmethod
    def create_member(input_data):
        sql = 'INSERT INTO public.member (name, account, password, identity) VALUES (%s, %s, %s, %s)'
        DB.execute_input(sql, (input_data['name'], input_data['account'], input_data['password'], input_data['identity']))

    @staticmethod
    def delete_product(tno, pid):
        sql = 'DELETE FROM public.record WHERE tno = %s and pid = %s'
        DB.execute_input(sql, (tno, pid))

    @staticmethod
    def get_order(userid):
        sql = 'SELECT * FROM public.order_list WHERE mid = %s ORDER BY ordertime DESC'
        return DB.fetchall(sql, (userid,))

    @staticmethod
    def get_role(userid):
        sql = 'SELECT identity, name FROM public.member WHERE mid = %s'
        return DB.fetchone(sql, (userid,))


class Cart:
    @staticmethod
    def check(user_id):
        sql = '''SELECT * FROM public.cart, public.record 
                 WHERE public.cart.mid = %s::bigint 
                 AND public.cart.tno = public.record.tno::bigint'''
        return DB.fetchone(sql, (user_id,))

    @staticmethod
    def get_cart(user_id):
        sql = 'SELECT * FROM public.cart WHERE mid = %s'
        return DB.fetchone(sql, (user_id,))

    @staticmethod
    def add_cart(user_id, time):
        sql = 'INSERT INTO public.cart (mid, carttime, tno) VALUES (%s, %s, nextval(\'public.cart_tno_seq\'))'
        DB.execute_input(sql, (user_id, time))

    @staticmethod
    def clear_cart(user_id):
        sql = 'DELETE FROM public.cart WHERE mid = %s'
        DB.execute_input(sql, (user_id,))


class Product:
    @staticmethod
    def count():
        sql = 'SELECT COUNT(*) FROM public.product'
        return DB.fetchone(sql)

    @staticmethod
    def get_product(pid):
        sql = 'SELECT * FROM public.product WHERE pid = %s'
        return DB.fetchone(sql, (pid,))

    @staticmethod
    def get_all_product():
        sql = 'SELECT * FROM public.product'
        return DB.fetchall(sql)

    @staticmethod
    def get_name(pid):
        sql = 'SELECT pname FROM public.product WHERE pid = %s'
        return DB.fetchone(sql, (pid,))[0]

    @staticmethod
    def add_product(input_data):
        sql = 'INSERT INTO public.product (pid, pname, price, category, pdesc) VALUES (%s, %s, %s, %s, %s)'
        DB.execute_input(sql, (input_data['pid'], input_data['pname'], input_data['price'], input_data['category'], input_data['pdesc']))

    @staticmethod
    def delete_product(pid):
        sql = 'DELETE FROM public.product WHERE pid = %s'
        DB.execute_input(sql, (pid,))

    @staticmethod
    def update_product(input_data):
        sql = 'UPDATE public.product SET pname = %s, price = %s, category = %s, pdesc = %s WHERE pid = %s'
        DB.execute_input(sql, (input_data['pname'], input_data['price'], input_data['category'], input_data['pdesc'], input_data['pid']))


class Record:
    @staticmethod
    def get_total_money(tno):
        sql = 'SELECT SUM(total) FROM public.record WHERE tno = %s'
        return DB.fetchone(sql, (tno,))[0]

    @staticmethod
    def check_product(pid, tno):
        sql = 'SELECT * FROM public.record WHERE pid = %s and tno = %s'
        return DB.fetchone(sql, (pid, tno))

    @staticmethod
    def get_price(pid):
        sql = 'SELECT price FROM public.product WHERE pid = %s'
        return DB.fetchone(sql, (pid,))[0]

    @staticmethod
    def add_product(input_data):
        sql = 'INSERT INTO public.record (pid, tno, amount, saleprice, total) VALUES (%s, %s, 1, %s, %s)'
        DB.execute_input(sql, (input_data['pid'], input_data['tno'], input_data['saleprice'], input_data['total']))

    @staticmethod
    def get_record(tno):
        sql = 'SELECT * FROM public.record WHERE tno = %s'
        return DB.fetchall(sql, (tno,))

    @staticmethod
    def get_amount(tno, pid):
        sql = 'SELECT amount FROM public.record WHERE tno = %s and pid = %s'
        return DB.fetchone(sql, (tno, pid))[0]

    @staticmethod
    def update_product(input_data):
        sql = 'UPDATE public.record SET amount = %s, total = %s WHERE pid = %s and tno = %s'
        DB.execute_input(sql, (input_data['amount'], input_data['total'], input_data['pid'], input_data['tno']))

    @staticmethod
    def delete_check(pid):
        sql = 'SELECT * FROM public.record WHERE pid = %s'
        return DB.fetchone(sql, (pid,))

    @staticmethod
    def get_total(tno):
        sql = 'SELECT SUM(total) FROM public.record WHERE tno = %s'
        return DB.fetchone(sql, (tno,))[0]


class Order_List:
    @staticmethod
    def add_order(input_data):
        sql = 'INSERT INTO public.order_list (oid, mid, ordertime, price, tno) VALUES (DEFAULT, %s, TO_TIMESTAMP(%s, %s), %s, %s)'
        DB.execute_input(sql, (input_data['mid'], input_data['ordertime'], input_data['format'], input_data['total'], input_data['tno']))

    @staticmethod
    def get_order():
        sql = '''
            SELECT o.oid, m.name, o.price, o.ordertime
            FROM public.order_list o
            NATURAL JOIN public.member m
            ORDER BY o.ordertime DESC
        '''
        return DB.fetchall(sql)

    @staticmethod
    def get_orderdetail():
        sql = '''
        SELECT o.oid, p.pname, r.saleprice, r.amount
        FROM public.order_list o
        JOIN public.record r ON o.tno = r.tno -- 確保兩者都是 bigint 類型
        JOIN public.product p ON r.pid = p.pid
        '''
        return DB.fetchall(sql)


class Analysis:
    @staticmethod
    def month_price(i):
        sql = 'SELECT EXTRACT(MONTH FROM ordertime), SUM(price) FROM public.order_list WHERE EXTRACT(MONTH FROM ordertime) = %s GROUP BY EXTRACT(MONTH FROM ordertime)'
        return DB.fetchall(sql, (i,))

    @staticmethod
    def month_count(i):
        sql = 'SELECT EXTRACT(MONTH FROM ordertime), COUNT(oid) FROM public.order_list WHERE EXTRACT(MONTH FROM ordertime) = %s GROUP BY EXTRACT(MONTH FROM ordertime)'
        return DB.fetchall(sql, (i,))

    @staticmethod
    def category_sale():
        sql = 'SELECT SUM(total), category FROM public.product, public.record WHERE public.product.pid = public.record.pid GROUP BY category'
        return DB.fetchall(sql)

    @staticmethod
    def member_sale():
        sql = 'SELECT SUM(price), public.member.mid, public.member.name FROM public.order_list, public.member WHERE public.order_list.mid = public.member.mid AND public.member.identity = %s GROUP BY public.member.mid, public.member.name ORDER BY SUM(price) DESC'
        return DB.fetchall(sql, ('user',))

    @staticmethod
    def member_sale_count():
        sql = 'SELECT COUNT(*), public.member.mid, public.member.name FROM public.order_list, public.member WHERE public.order_list.mid = public.member.mid AND public.member.identity = %s GROUP BY public.member.mid, public.member.name ORDER BY COUNT(*) DESC'
        return DB.fetchall(sql, ('user',))
