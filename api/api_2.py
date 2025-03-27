import imp
from flask import render_template, Blueprint, redirect, request, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from link import *
from api.sql import *

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

@api.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        
        user_username = request.form['username']
        user_account = request.form['account']

        exist_username = Member.get_all_username()
        exist_account = Member.get_all_account()
        
        username_list = [i[0] for i in exist_username]
        account_list = [i[0] for i in exist_account]

        errors = False  # 用來標記是否有錯誤發生

        # 檢查暱稱是否存在
        if user_username in username_list:
            flash('*已經有相同的暱稱', 'name_exists')
            errors = True
        
        # 檢查帳號是否存在
        if user_account in account_list:
            flash('*已經有相同的Email', 'account_exists')
            errors = True
        
        # 如果有錯誤，返回註冊頁面
        if errors:
            return redirect(url_for('api.register'))

        # 如果沒有錯誤，則繼續進行註冊
        input_data = { 
            'name': user_username, 
            'account': user_account, 
            'password': request.form.get('password'), 
            'identity': request.form.get('identity')
        }
        
        Member.create_member(input_data)
        return redirect(url_for('api.login'))

    return render_template('register.html')

@api.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


