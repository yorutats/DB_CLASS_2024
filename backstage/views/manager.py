from flask import Blueprint, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from link import *
from api.sql import *
import imp, random, os, string
from werkzeug.utils import secure_filename
from flask import current_app

UPLOAD_FOLDER = 'static/product'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

manager = Blueprint('manager', __name__, template_folder='../templates')

def config():
    current_app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    config = current_app.config['UPLOAD_FOLDER'] 
    return config

@manager.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return redirect(url_for('manager.productManager'))

@manager.route('/productManager', methods=['GET', 'POST'])
@login_required
def productManager():
    if request.method == 'GET':
        if(current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('index'))
        
    if 'delete' in request.values:
        bid = request.values.get('delete')
        # data = Record.delete_check(bid)
        
        # if(data != None):
        #     flash('failed')
        # else:
        # data = Bird.get_product(bid)
        Bird.delete_bird(bid)
    
    elif 'edit' in request.values:
        bid = request.values.get('edit')
        return redirect(url_for('manager.edit', bid=bid))
    
    bird_data = get_all_birds()
    return render_template('productManager.html', bird_data = bird_data, user=current_user.name)

def get_all_birds():
    bird_list = Bird.get_all_product()
    bird_data = []
    for bird in bird_list:
        bird = {
            '鳥類編號': bird[0],
            '鳥類供應商': bird[1],
            '鳥類照護手冊': bird[2],
            '鳥類說明': bird[3],
            '鳥類品種': bird[4],
            '鳥類價格': bird[5]
        }
        bird_data.append(bird)
    return bird_data

@manager.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = ""
        while(data != None):
            bId = str(random.randrange( 0, 10000))
            data = Bird.get_product(bId)

        species = request.values.get('species')
        price = request.values.get('price')
        sId = request.values.get('sId')
        gId = request.values.get('gId')
        bDesc = request.values.get('bDesc')
        stock = request.values.get('stock')

        # 檢查是否正確獲取到所有欄位的數據
        if species is None or price is None or sId is None or gId is None or bDesc is None or stock is None:
            flash('所有欄位都是必填的，請確認輸入內容。')
            return redirect(url_for('manager.productManager'))

        # 檢查欄位的長度
        if len(species) < 1 or len(price) < 1:
            flash('商品名稱或價格不可為空。')
            return redirect(url_for('manager.productManager'))


        if (len(species) < 1 or len(price) < 1):
            return redirect(url_for('manager.productManager'))
        
        Bird.add_bird(
            {'bId' : bId,
             'species' : species,
             'sId' : sId,
             'gId' : gId,
             'bDesc' : bDesc,
             'price' : price,
             'stock' : stock,
            }
        )

        return redirect(url_for('manager.productManager'))

    return render_template('productManager.html')

@manager.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'GET':
        if(current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('bookstore'))

    if request.method == 'POST':
        Bird.update_bird(
            {
            'bid' : request.values.get('bid'),
            'species' : request.values.get('species'),
            'price' : request.values.get('price'),
            'sId' : request.values.get('sId'), 
            'gId' : request.values.get('gId'),
            'bDesc' : request.values.get('bDesc'),
            'stock' : request.values.get('stock'),
            }
        )
        
        return redirect(url_for('manager.productManager'))

    else:
        product = show_info()
        return render_template('edit.html', data=product)


def show_info():
    bid = request.args['bid']
    data = Bird.get_product(bid)
    sId = data[1]
    gId = data[2]
    bDesc = data[3]
    species = data[4]
    price = data[5]
    stock = data[6]

    product = {
        '鳥類編號': bid,
        '供應商編號': sId,
        '照顧手冊編號': gId,
        '鳥類描述': bDesc,
        '鳥類品種': species,
        '鳥類單價': price,
        '鳥類庫存': stock,
    }
    return product


@manager.route('/orderManager', methods=['GET', 'POST'])
@login_required
def orderManager():
    if request.method == 'POST':
        pass
    else:
        order_row = Order.get_order()
        order_data = []
        for i in order_row:
            order = {
                '訂購人編號': i[0],
                '訂購人': i[1],
                '訂單金額': i[2],
                '訂購時間': i[3]
            }
            order_data.append(order)

        return render_template('orderManager.html', order_data=order_data)


# =============Supplier=============

@manager.route('/supplierManager', methods=['GET', 'POST'])
@login_required
def supplierManager():
    if request.method == 'GET':
        if(current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('index'))
        
    if 'delete' in request.values:
        sid = request.values.get('delete')
        response = Supplier.delete_supplier(sid)
    
    elif 'edit' in request.values:
        sid = request.values.get('edit')
        print(f"================{sid}================")
        return redirect(url_for('manager.editSupplier', sid=sid))
    
    supplier_data = Supplier.get_all_supplier()
    return render_template('supplierManager.html', supplier_data = supplier_data, user=current_user.name)

@manager.route('/addSupplier', methods=['GET', 'POST'])
def addSupplier():
    if request.method == 'POST':
        data = ""
        while(data != None):
            sId = str(random.randrange( 0, 10000))
            data = Supplier.get_supplier(sId)
            sName = request.values.get('sName')
        phone = request.values.get('sPhone')
        rating = request.values.get('sRating')
        # 檢查是否正確獲取到所有欄位的數據
        if sName is None or phone is None or rating is None:
            flash('所有欄位都是必填的，請確認輸入內容。')
            return redirect(url_for('manager.supplierManager'))

        # 檢查欄位的長度
        if len(sName) < 1 or len(phone) < 1:
            flash('供應商名稱與連絡電話不可為空。')
            return redirect(url_for('manager.supplierManager'))

        Supplier.add_supplier(
            {
            'sId' : sId,
            'sName' : sName,
            'phone' : phone,
            'rating' : rating,
            }
        )
        return redirect(url_for('manager.supplierManager'))

    return render_template('supplierManager.html')

@manager.route('/editSupplier', methods=['GET', 'POST'])
@login_required
def editSupplier():
    if request.method == 'GET':
        if(current_user.role == 'user'):
            flash('No permission')
            return redirect(url_for('bookstore'))

    if request.method == 'POST':
        Supplier.update_supplier(
            {
            'sId' : request.values.get('sId'),
            'sName' : request.values.get('sName'),
            'phone' : request.values.get('phone'),
            'rating' : request.values.get('rating'), 
            }
        )
        
        return redirect(url_for('manager.supplierManager'))

    else:
        suppiler = get_supplier()
        return render_template('editSupplier.html', data=suppiler)

def get_supplier():
    sid = request.args['sid']
    data = Supplier.get_supplier(sid)
    sId = data[0]
    sName = data[1]
    sPhone = data[2]
    sRating = data[3]

    supplier = {
        '供應商編號': sId,
        '供應商名稱': sName,
        '連絡電話': sPhone,
        '評分': sRating,
    }
    return supplier