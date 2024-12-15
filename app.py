from flask import Flask, Response, request, jsonify, redirect, url_for, render_template, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask import session
import requests
import os

app = Flask(__name__)
app.secret_key = 'key_@kuriyama9590'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    todos = db.relationship('Todo', backref='user', lazy=True)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# 初始化测试用户数据
def init_db():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='kuriyama9590').first():
            test_user = User(username='kuriyama9590', password='040310qyc')
            db.session.add(test_user)
            db.session.commit()

init_db()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

CORS(app)

WINDOWS_PC_URL = "http://10.151.1.72:5001/videos"

# 添加视频文件的存储路径配置
VIDEO_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'videos')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            session['login_status'] = True
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('login_status',None)#清除会话
    return redirect(url_for('index'))

@app.route('/')
def index():
    login_status = session.get('login_status', False)
    username = current_user.username if login_status and hasattr(current_user, 'username') else ''  # 获取用户名
    title = f'{username},欢迎回来!' if login_status else '请先登录'
    return render_template('index.html', login_status=login_status, title=title)

@app.route('/about')
@login_required
def about():
    return render_template('about.html')

@app.route('/video_zone')
@login_required
def video_zone():
    return render_template('video_zone.html')

@app.route('/player/<video_name>/<video_page>')
def player(video_name, video_page):
    # 从请求参数中获取总集数，确保转换为整数
    pages_number = request.args.get('pages_number', '0')
    try:
        pages_number = int(pages_number)
    except ValueError:
        pages_number = 0
    
    return render_template('player.html', 
                           video_name=video_name, 
                           video_page=video_page, 
                           pages_number=pages_number)

# 路由：提供视频流
@app.route('/stream/<video_name>/<video_page>')
def stream_video(video_name, video_page):
    video_url = f"{WINDOWS_PC_URL}/{video_name}/{video_page}"
    try:
        # 转发请求到视频服务器，包括Range头
        headers = {}
        if request.headers.get('Range'):
            headers['Range'] = request.headers.get('Range')
        
        response = requests.get(video_url, headers=headers, stream=True)
        
        def generate():
            buffer_size = 0
            max_buffer_size = 1024 * 1024 * 100  # 100MB
            for chunk in response.iter_content(chunk_size=1024 * 1024):  # 每次读取1MB
                if not chunk:
                    break
                
                buffer_size += len(chunk)
                
                if buffer_size >= max_buffer_size:
                    print("CLEAR BUFFER")
                    # 如果缓冲区达到最大值，则停止读取并清除缓存
                    yield chunk[:max_buffer_size - (buffer_size - len(chunk))]
                    buffer_size = len(chunk) - (max_buffer_size - (buffer_size - len(chunk)))
                else:
                    yield chunk
            
            response.close()  # 确保关闭连接
        
        # 构建响应
        flask_response = Response(
            generate(),
            status=response.status_code,
            content_type=response.headers.get('content-type')
        )
        
        # 转发重要的响应头
        if response.headers.get('Content-Range'):
            flask_response.headers['Content-Range'] = response.headers['Content-Range']
        if response.headers.get('Accept-Ranges'):
            flask_response.headers['Accept-Ranges'] = response.headers['Accept-Ranges']
        if response.headers.get('Content-Length'):
            flask_response.headers['Content-Length'] = response.headers['Content-Length']
        
        return flask_response
    
    except Exception as e:
        app.logger.error(f"Error streaming video: {str(e)}")
        return str(e), 404

@app.route('/todo')
@login_required
def todo():
    login_status = session.get('login_status', False)
    username = current_user.username if login_status else ''
    title = f'{username}的TODO空间' if login_status else '请先登录'
    todos = Todo.query.filter_by(user_id=current_user.id).all()
    return render_template('todo.html', title=title, todos=todos)

@app.route('/api/todos', methods=['GET', 'POST', 'DELETE'])
@login_required
def handle_todos():
    if request.method == 'GET':
        todos = Todo.query.filter_by(user_id=current_user.id).all()
        return jsonify([{'id': todo.id, 'content': todo.content, 'completed': todo.completed} for todo in todos])
    
    elif request.method == 'POST':
        data = request.get_json()
        new_todo = Todo(content=data['content'], user_id=current_user.id)
        db.session.add(new_todo)
        db.session.commit()
        return jsonify({'id': new_todo.id, 'content': new_todo.content, 'completed': new_todo.completed})
    
    elif request.method == 'DELETE':
        todo_id = request.args.get('id')
        todo = Todo.query.get_or_404(todo_id)
        if todo.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        db.session.delete(todo)
        db.session.commit()
        return '', 204

@app.route('/api/todos/<int:todo_id>/toggle', methods=['POST'])
@login_required
def toggle_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if todo.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    todo.completed = not todo.completed
    db.session.commit()
    return jsonify({'id': todo.id, 'content': todo.content, 'completed': todo.completed})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)