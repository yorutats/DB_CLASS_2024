import re
from typing_extensions import Self
from flask import Flask, request, template_rendered, Blueprint
from flask import url_for, redirect, flash
from flask import render_template
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime
from numpy import identity, product
import random, string
from sqlalchemy import null
from link import *
import math
from base64 import b64encode
from api.sql import Member, Order, Bird, Record, Cart, Customer

store = Blueprint('bookstore', __name__, template_folder='../templates')

@store.route('/', methods=['GET', 'POST'])
@login_required
def bookstore():
    result = Bird.count()
    count = math.ceil(result[0]/9)
    flag = 0
    if request.method == 'GET':
        if(current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))

    if 'keyword' in request.args and 'page' in request.args:
        total = 0
        single = 1
        page = int(request.args['page'])
        start = (page - 1) * 9
        end = page * 9
        search = request.values.get('keyword')
        
        cursor.execute('SELECT * FROM bird WHERE species LIKE %s', ('%' + search + '%',))
        bird_row = cursor.fetchall()
        bird_data = []
        final_data = []
        
        for i in bird_row:
            print(i)
            bird = {
                '鳥類編號': i[0],
                '鳥類名稱': i[1],
                '鳥類價格': i[2]
            }
            bird_data.append(bird)
            total = total + 1
        
        if(len(bird_data) < end):
            end = len(bird_data)
            flag = 1
            
        for j in range(start, end):
            final_data.append(bird_data[j])
            
        count = math.ceil(total/9)
        
        return render_template('bookstore.html', single=single, keyword=search, bird_data=bird_data, user=current_user.name, page=1, flag=flag, count=count)    

    
    elif 'pid' in request.args:
        bid = request.args['pid']
        data = Bird.get_product(bid)
        
        pname = data[4]
        price = data[5]
        description = data[3]
        image = 'sdg.jpg'
        
        product = {
            '商品編號': bid,
            '商品名稱': pname,
            '單價': price,
            '商品敘述': description,
            '商品圖片': image
        }

        return render_template('product.html', data = product, user=current_user.name)
    
    elif 'page' in request.args:
        page = int(request.args['page'])
        start = (page - 1) * 9
        end = page * 9
        
        bird_row = Bird.get_all_product()
        bird_data = []
        final_data = []
        
        for i in bird_row:
            bird = {
                '鳥類編號': i[0],
                '鳥類名稱': i[4],
                '鳥類價格': i[5],
            }
            bird_data.append(bird)
            
        if(len(bird_data) < end):
            end = len(bird_data)
            flag = 1
            
        for j in range(start, end):
            final_data.append(bird_data[j])
        
        return render_template('bookstore.html', bird_data=final_data, user=current_user.name, page=page, flag=flag, count=count)    
    
    elif 'keyword' in request.args:
        single = 1
        search = request.values.get('keyword')
        keyword = search
        cursor.execute('SELECT * FROM bird WHERE species LIKE %s', ('%' + search + '%',))
        bird_row = cursor.fetchall()
        bird_data = []
        total = 0
        
        for i in bird_row:
            bird = {
                '鳥類編號': i[0],
                '鳥類名稱': i[4],
                '鳥類價格': i[5],
            }

            bird_data.append(bird)
            total = total + 1
            
        if(len(bird_data) < 9):
            flag = 1
        
        count = math.ceil(total/9)    
        
        return render_template('bookstore.html', keyword=search, single=single, bird_data=bird_data, user=current_user.name, page=1, flag=flag, count=count)    
    
    else:
        bird_row = Bird.get_all_product()
        bird_data = []
        for i in bird_row:
            bird = {
                '鳥類編號': i[0],
                '鳥類名稱': i[4],
                '鳥類價格': i[5],
            }
            if len(bird_data) < 9:
                bird_data.append(bird)
        
        return render_template('bookstore.html', bird_data=bird_data, user=current_user.name, page=1, flag=flag, count=count)

# 會員購物車
@store.route('/cart', methods=['GET', 'POST'])
@login_required # 使用者登入後才可以看
def cart():
    # 以防管理者誤闖
    if request.method == 'GET':
        if (current_user.role == 'manager'):
            flash('No permission')
            return redirect(url_for('manager.home'))

    # 回傳有 pid 代表要 加商品
    if request.method == 'POST':
        # if "pid" in request.form:
        #     print("bid")
        #     cId = current_user.id
        #     data = Cart.get_cart(cId)

        #     if data is None:  # 假如購物車裡面沒有他的資料
        #         time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #         Cart.add_cart(current_user.id, time)  # 幫他加一台購物車
        #         data = Cart.get_cart(current_user.id)

        #     tno = data[2]  # 取得交易編號
        #     pid = request.form.get('pid')  # 使用者想要購買的東西，使用 `request.form.get()` 來避免 KeyError
        #     if not pid:
        #         flash('Product ID is missing.')
        #         return redirect(url_for('bookstore.cart'))  # 返回購物車頁面並顯示錯誤信息

        #     # 檢查購物車裡面有沒有商品
        #     product = Record.check_product(pid, cid)
        #     # 取得商品價錢
        #     price = Bird.get_product(pid)[2]

        #     # 如果購物車裡面沒有的話，把它加一個進去
        #     if product is None:
        #         Record.add_product({'pid': pid, 'tno': tno, 'saleprice': price, 'total': price})
        #     else:
        #         # 如果購物車裡面有的話，就多加一個進去
        #         amount = Record.get_amount(tno, pid)
        #         total = (amount + 1) * int(price)
        #         Record.update_product({'amount': amount + 1, 'tno': tno, 'pid': pid, 'total': total})

        # elif "delete" in request.form:
        #     print("delete")
        #     pid = request.form.get('delete')
        #     tno = Cart.get_cart(current_user.id)[2]

        #     Member.delete_product(tno, pid)
        #     product_data = only_cart()

        # elif "user_edit" in request.form:
        #     print("user_edit")
        #     change_order()
        #     return redirect(url_for('bookstore.bookstore'))
        if "order" in request.form:
            bid = request.form.get('order')
            data = Bird.get_product(bid)
            amount = data[5]
            time = str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            Order.add_order({'cid': current_user.id, 'ordertime': time, 'totalAmount': amount})
            return render_template('complete.html', user=current_user.name)
    print("only")
    product_data = only_cart()

    if product_data == 0:
        return render_template('empty.html', user=current_user.name)
    else:
        return render_template('cart.html', data=product_data, user=current_user.name)


@store.route('/order')
def order():
    data = Cart.get_cart(current_user.id)
    tno = data[2]

    product_row = Record.get_record(tno)
    product_data = []

    for i in product_row:
        pname = Bird.get_species(i[1])
        product = {
            '商品編號': i[1],
            '商品名稱': pname,
            '商品價格': i[3],
            '數量': i[2]
        }
        product_data.append(product)
    
    total = float(Record.get_total(tno))  # 將 Decimal 轉換為 float


    return render_template('order.html', data=product_data, total=total, user=current_user.name)

@store.route('/orderlist', methods=['GET', 'POST'])
@login_required
def orderlist():
    order_row = Order.get_order()
    
    order_data = []
    for i in order_row:
        if len(i) >= 4: 
            order = {
                '訂單編號': i[0],
                '訂購人': i[1],
                '訂單日期': i[2],
                '訂單總價': i[3],
            }
            order_data.append(order)
        else:
            print(f"Unexpected data format: {i}") 
            continue  
    
    return render_template('orderlist.html', orders=order_data)


def change_order():
    data = Cart.get_cart(current_user.id)
    tno = data[2] # 使用者有購物車了，購物車的交易編號是什麼
    product_row = Record.get_record(data[2])

    for i in product_row:
        
        # i[0]：交易編號 / i[1]：商品編號 / i[2]：數量 / i[3]：價格
        if int(request.form[i[1]]) != i[2]:
            Record.update_product({
                'amount':request.form[i[1]],
                'pid':i[1],
                'tno':tno,
                'total':int(request.form[i[1]])*int(i[3])
            })
            print('change')

    return 0


def only_cart():
    count = Cart.check(current_user.id)

    if count is None:
        return 0

    data = Cart.get_cart(current_user.id)
    tno = data[2]
    product_row = Record.get_record(tno)
    product_data = []

    for i in product_row:
        pid = i[1]
        pname = Bird.get_species(i[1])
        price = i[3]
        amount = i[2]

        product = {
            '商品編號': pid,
            '商品名稱': pname,
            '商品價格': price,
            '數量': amount
        }
        product_data.append(product)

    return product_data

@store.route('/birdcareguide/<int:pid>', methods=['GET'])
@login_required
def birdcareguide(pid):
    bird_data = {
        1: {"名稱": "鸚鵡", "護理指南": "每天定時餵食，保持清潔", "影片": "https://example.com/parrot-care"},
        2: {"名稱": "麻雀", "護理指南": "提供足夠的空間和水分", "影片": None},
    }

    if pid in bird_data:
        bird = bird_data[pid]
        return render_template('birdcareguide.html', bird=bird, user=current_user.name)
    else:
        flash("無法找到護理指南")
        return redirect(url_for('bookstore.bookstore'))
