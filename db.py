from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

from user import User

clinet = MongoClient("mongodb+srv://test:test@cluster0.vel6spq.mongodb.net/?retryWrites=true&w=majority")

chat_db = clinet.get_database('chatDB')
users_collection = chat_db.get_collection('users')


def save_user(username, email, password):
    password_hash = generate_password_hash(password)
    users_collection.insert_one({"_id": username, "email": email, 'password': password_hash})

def get_user(username):
    user_data = users_collection.find_one({"_id": username})
    return User(user_data['_id'], user_data['email'], user_data['password'])
