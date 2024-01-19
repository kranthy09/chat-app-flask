from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from pymongo import errors
from db import get_user, save_user


app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = "my secret"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
 
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    if request.method == 'POST':
        username = request.form.get('username')
        password_input = request.form.get('password')
        user = get_user(username)
        if user and user.check_password(password_input):
            login_user(user)
            return redirect(url_for('home', username=username))
        else:
            message = 'Failed to login'
            return render_template('login.html', message=message)

    return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password_input = request.form.get('password')
        try:

            save_user(username=username, password=password_input, email=email)
            return redirect(url_for('login'))
        except errors.DuplicateKeyError:
            message = "User already exists!"
    return render_template('signup.html', message=message)

@app.route('/chat')
def chat():
    username = request.args.get('username')
    room = request.args.get('room')
    app.logger.info("{} values {} ".format(request.args['username'], request.args['room']))
    if username and room:
        return render_template('chat.html', username=username, room=room)
    else:
        return redirect(url_for('home'))

@socketio.on('join_room')
def handle_join_room(data):
    app.logger.info("{} has joined the room {} ".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announcement', data=data, room=data['room'])

@socketio.on('leave_room')
def handle_leave_room(data):
    leave_room(data['room'])
    socketio.emit('leave_room_announcement', data=data, room=data['room'])

@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}: {} ".format(data['username'], data['room'], data['message']))
    socketio.emit('receive_message', data, room=data['room'])

@login_manager.user_loader
def load_user(username):
    return get_user(username)

if __name__ == '__main__':
    socketio.run(app, debug=True)
