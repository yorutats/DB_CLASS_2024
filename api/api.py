import imp
from flask import render_template, Blueprint, redirect, request, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from link import *
from api.sql import *
import random

api = Blueprint('api', __name__, template_folder='./templates')

login_manager = LoginManager(api)
login_manager.login_view = 'api.login'
login_manager.login_message = "請先登入"

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(userid):  
    user = User()
    user.id = userid
    data = Member.get_role(userid)
    try:
        user.role = data[0]
        user.name = data[1]
    except:
        pass
    return user

@api.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':

        account = request.form['account']
        password = request.form['password']
        data = Member.get_member(account) 

        try:
            DB_password = data[0][1]
            user_id = data[0][2]
            identity = data[0][3]

        except:
            flash('*沒有此帳號')
            return redirect(url_for('api.login'))

        if(DB_password == password ):
            user = User()
            user.id = user_id
            login_user(user)

            if( identity == 'user'):
                return redirect(url_for('bookstore.bookstore'))
            else:
                return redirect(url_for('manager.productManager'))
        
        else:
            flash('*密碼錯誤，請再試一次')
            return redirect(url_for('api.login'))

    
    return render_template('login.html')

def get_new_mid(mids):
    # 提取所有的 MID，從元組中取出第一個值
    mid_list = [mid[0] for mid in mids]
    
    # 找到第一個缺失的 MID
    for i in range(1, max(mid_list) + 1):
        if i not in mid_list:
            return i
    
    # 如果沒有缺失，返回下一個可用的 MID
    return max(mid_list) + 1

@api.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        # check email(account)
        user_email = request.form['email']
        exist_account = Member.get_all_account()
        account_list = []
        for i in exist_account:
            account_list.append(i[0])
        
        # check username
        user_name = request.form['username']
        exist_username = Member.get_all_username()
        username_list = []
        for i in exist_username:
            username_list.append(i[0])
        
        if(user_email in account_list and user_name in username_list):
            flash('both')
            return redirect(url_for('api.register'))
        elif (user_email in account_list):
            flash('user_email')
            return redirect(url_for('api.register'))
        elif (user_name in username_list):
            flash('user_name')
            return redirect(url_for('api.register'))
        else:
            mids = Member.get_all_mid()
            mid = get_new_mid(mids)
            input = {
                'mid': mid,
                'name': user_name, 
                'account':user_email, 
                'password':request.form['password'], 
                'identity':request.form['identity']
            }
            Member.create_member(input)
            phone_number = "09" + "".join([str(random.randint(0, 9)) for _ in range(8)])
            Customer.add_customer(mid, user_name, phone_number)
            return redirect(url_for('api.login'))

    return render_template('register.html')

@api.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))