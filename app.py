from flask import Flask, request, jsonify, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()
    print("db created successfully")
    print(User.query.all())

@app.route('/')
def index():
    login_status = session.get('login_status',False)
    return render_template('index.html',login_status = login_status)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()#创建用户对象
        if user and check_password_hash(user.password_hash, password):
            session['login_status'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html',error = '用户名或密码错误')
    return render_template('login.html',login_status = False)

@app.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    if not password or password != confirm_password:
        return render_template('register.html', error='密码不一致')

    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return render_template('register.html', error='用户名或邮箱已存在')

    password_hash = generate_password_hash(password)
    new_user = User(username=username, email=email, password_hash=password_hash)
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        print(e)
        return render_template('register.html', error='注册失败，请稍后再试')

    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)