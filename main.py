from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, current_user, login_user, logout_user, UserMixin, login_required


app = Flask(__name__)
app.secret_key = 'someasdas dioepss'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zadanie.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
managers = LoginManager(app)



#БД - Таблицы - Записи
#Обьявления:
# id  title         desc                price       customer_found
# 1    имя заказа   описание заказа      1690р          имя пользователя
# 

#Пользователи:
# id   login    pass    cash    customer   executor
#  1    name    123     1999р       1          0

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False)
    password =  db.Column(db.String(50), nullable=False)
    cash = db.Column(db.Integer, default="0")
    customer = db.Column(db.Boolean, default=False)    
    
    
class Zakaz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    desc = db.Column(db.Text, nullable=False)
    price = db.Column(db.Integer)
    # customer_found = db.relationship('User', backref='zakaz', lazy=True)

@managers.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/profile/', methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        login = request.form['login']
        password = request.form['password']
        mail = request.form['mail']
        cash = request.form['cash']
        customer = bool(int(request.form['customer']))       

        hash_pwd = generate_password_hash(password) 
        user = User.query.filter_by(login=login).update({'login': login,'password':hash_pwd,'email':mail,'cash': cash,'customer': customer })
        db.session.commit()
        return redirect('/profile')       
    else:
        return render_template('profile.html')    
    
@app.route('/product/<int:id>', methods=["GET", "POST"])
def ProductProfile(id):
    data = Zakaz.query.filter_by(id=id).first()
    user = User.query.all()
    return render_template('productdesc.html', data=data, users=user)
    


@app.route('/')
def index():
    article = Zakaz.query.all()
    return render_template('index.html', data=article)

@app.route('/product/create', methods=["POST","GET"])
@login_required
def product_create():
    if request.method == "POST":
        title = request.form['title']
        desc = request.form['desc']
        price = request.form['price']        

        if not (title or desc or price):
            flash('Заполните все поля')       
        else:            
            product = Zakaz(title=title, desc=desc, price=price)
            db.session.add(product)
            db.session.commit()
            return redirect(url_for('index'))       
    else:
        return render_template('zakaz.html')
    


@app.route('/login' , methods=["POST","GET"])    
def login():
    if request.method == "POST":
        login = request.form.get('login')
        password = request.form.get('password')

        if login and password:
            user = User.query.filter_by(login=login).first()

            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect('index')
            else:
                flash('логин или пароль не коректны')
        else:
            flash('проверьте введенные данные')
            
    return render_template('login.html')

@app.route('/logout', methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=["POST","GET"])
def register():
    if request.method == "POST":
        login = request.form['login']
        email = request.form['E-mail']
        password = request.form['password']
        password1 = request.form['password1']

        if not (login or password or password2 or email):
            flash('Заполните все поля')
        elif password != password1:
            flash('пароли не совпадают')
        else:
            hash_pwd = generate_password_hash(password) 
            user = User(login=login, email=email, password=hash_pwd)
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('login'))       
    else:
        return render_template("register.html")

    


if __name__ == "__main__":
    app.run(debug=True)