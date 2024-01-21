from bson import ObjectId
from pymongo import MongoClient
from datetime import datetime


from user import User

clinet = MongoClient(
    "mongodb+srv://test:test@cluster0.vel6spq.mongodb.net/?retryWrites=true&w=majority"
)

chat_db = clinet.get_database("chatDB")
users_collection = chat_db.get_collection("users")
rooms_collection = chat_db.get_collection("rooms")
room_members_collection = chat_db.get_collection("room_members")


def save_user(username, email, password):
    password_hash = generate_password_hash(password)
    users_collection.insert_one(
        {"_id": username, "email": email, "password": password_hash}
    )


def get_user(username):
    user_data = users_collection.find_one({"_id": username})
    return User(user_data["_id"], user_data["email"], user_data["password"])


def save_room(room_name, created_by):
    room_id = rooms_collection.insert_one(
        {"room_name": room_name, "created_by": created_by, "created_at": datetime.now()}
    )
    add_room_member(room_id, room_name, created_by, created_by, is_admin=True)
    return room_id


def add_room_member(room_id, room_name, username, added_by, is_room_admin=False):
    rooms_collection.insert_one(
        {
            "_id": {"room_id": ObjectId(room_id), "username": username},
            "room_name": room_name,
            "added_by": added_by,
            "added_at": datetime.now(),
            "is_room_admin": is_room_admin,
        }
    )


def add_room_members(room_id, room_name, usernames, added_by):
    rooms_collection.insert_many(
        [
            {
                "_id": {"room_id": ObjectId(room_id), "username": username},
                "room_name": room_name,
                "added_by": added_by,
                "added_at": datetime.now(),
                "is_room_admin": False,
            }
        ]
        for username in usernames
    )


def get_room(room_id):
    # ObjectId will convert str of room_id to of type '_id'
    rooms_collection.find_one({"_id": ObjectId(room_id)})


def update_room(room_id, room_name):
    rooms_collection.update_one(
        {"_id": ObjectId(room_id)}, {"$set": {"name": room_name}}
    )


def get_room_members(room_id):
    room_members_collection.find({"_id.room_id": ObjectId(room_id)})


def remove_room_members(room_id, usernames):
    room_members_collection.delete_many(
        {
            "_id": {
                "$in": [
                    {"room_id": room_id, "username": username} for username in usernames
                ]
            }
        }
    )


def get_rooms_for_user(username):
    room_members_collection.find({"_id.username": ObjectId(username)})


def is_room_member(room_id, username):
    room_members_collection.count_documents(
        {"_id": {"room_id": room_id, "username": username}}
    )


def is_room_admin(room_id, username):
    room_members_collection.count_documents(
        {"_id": {"room_id": room_id, "username": username}, "is_room_admin": True}
    )
