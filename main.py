import uuid
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, send  
from flask_cors import CORS
from datetime import datetime
import random
import string
from tinydb import TinyDB, Query
import CommandHandler as CH


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", engineio_logger=True)

db = TinyDB('db.json')  # You can use different JSON files for different collections
rooms_table = db.table('rooms')
messages_table = db.table('messages')
uploaded_data_table = db.table('uploaded_data')
online_users_table = db.table('online_users')



def generate_alphanumeric_string():
    characters = string.ascii_lowercase + string.digits
    def generate_group():
        return ''.join(random.choices(characters, k=2))
    group1 = generate_group()
    group2 = generate_group()
    group3 = generate_group()
    return f"{group1}{group2}{group3}"

@app.route('/api/rooms/create', methods=['POST'])
def create_room():
    data = request.json
    user_name = data.get('userName')
    room_name = data.get('roomName')
    gemini_key = data.get('geminiKey')
    pinecone_key = data.get('pineconeKey')
    
    if not validate_keys(gemini_key, pinecone_key):
        return jsonify({"message": "Invalid Gemini or Pinecone key"}), 400

    room_code = generate_alphanumeric_string()
    print(room_code, room_name, gemini_key, pinecone_key)
    print(f"Room has been created by: {user_name}")

    creation_time_utc = datetime.now().isoformat()
    
    rooms_table.insert({
        "code": room_code,
        "name": room_name,
        "gemini_key": gemini_key,
        "pinecone_key": pinecone_key,
        "users": [user_name],
        "creator": user_name,
        "creation_time_utc": creation_time_utc
    })
    return jsonify({"roomCode": room_code})


@app.route('/api/rooms/join', methods=['POST'])
def join_room_api():
    data = request.json
    user_name = data.get('userName')
    room_code = data.get('roomCode')

    room = rooms_table.get(Query().code == room_code)
    if not room:
        return jsonify({"message": "Room not found"}), 404
    rooms_table.update({"users": room["users"] + [user_name]}, Query().code == room_code)
    return jsonify({"roomName": room["name"]})

@app.route('/api/rooms/name', methods=['POST'])
def get_name():
    data = request.json
    room_code = data.get('roomCode')
    room = rooms_table.get(Query().code == room_code)
    return jsonify(room['name'])

    

@app.route('/api/messages/', methods=['POST'])
def get_messages():
    data = request.json
    room_code = data.get('roomCode')
    room_messages = messages_table.search(Query().roomCode == room_code)
    return jsonify([msg for msg in room_messages])


# @app.route('/api/online-users', methods=['POST'])
# def get_online_users():
#     data = request.json
#     print("online user requested")
#     room_code = data.get('roomCode')
#     users = online_users_table.search(Query().roomCode == room_code)
#     return jsonify([user for user in users])

# @app.route('/api/uploaded-data', methods=['GET'])
# def get_uploaded_data():
#     room_code = request.args.get('roomCode')
#     data = uploaded_data_table.search(Query().roomCode == room_code)
#     return jsonify(data)


@app.route('/api/upload', methods=['POST'])
def upload_file():
    room_code = request.form.get('roomCode')
    file = request.files.get('file')
    
    if not file:
        return jsonify({"success": False, "message": "No file provided"}), 400
    
    file_data = {
        "id": generate_alphanumeric_string(),
        "filename": file.filename
    }
    uploaded_data_table.insert({"roomCode": room_code, **file_data})
    
    socketio.emit('uploaded_data_update', uploaded_data_table.search(Query().roomCode == room_code), room=room_code)
    
    return jsonify({"success": True})


@app.route('/api/export-room', methods=['GET'])
def export_room():
    room_code = request.args.get('roomCode')
    room = rooms_table.get(Query().code == room_code)
    if not room:
        return jsonify({"message": "Room not found"}), 404
    
    room_data = {
        "room": room,
        "messages": messages_table.search(Query().roomCode == room_code),
        "uploaded_data": uploaded_data_table.search(Query().roomCode == room_code)
    }
    
    return jsonify(room_data)


@socketio.on('chat_message')
def handle_chat_message(data):
    print('Received message:', data)
    
    room_code = data.get('roomCode')
    content = data.get('content')
    userName = data.get('userName')

    if not room_code or not content:
        print('Error: Missing roomCode or content')
        return

    new_message = {
        "id": uuid.uuid4().hex,
        "content": content,
        "sender": userName,
        "timestamp": datetime.now().isoformat(),
        "roomCode": room_code
    }
    
    messages_table.insert(new_message)

    print(f'Emitting message to room {room_code}:', new_message)
    emit('chat_message', new_message, room=room_code)
    
    if new_message['content'].startswith('!'):
        room = rooms_table.get(Query().code == room_code)
        messages = messages_table.search(Query().roomCode == room_code)
        uploaded_data = uploaded_data_table.search(Query().roomCode == room_code)
        online_users = online_users_table.get(Query().roomCode == room_code)

        command_data = {
            'room': room,
            'messages': messages,
            'uploaded_data': uploaded_data,
            'online_users': online_users['users'] if online_users else []
        }
        
        handler = CH.commandHandler(new_message, command_data)
        content, commandName= handler.analyzeCommand()
        new_message = {
            "id": uuid.uuid4().hex,
            "content": content,
            "sender": commandName,
            "timestamp": datetime.now().isoformat(),
            "roomCode": room_code
            }
        
        emit('chat_message', new_message, room=room_code)
        


@socketio.on('join_room')
def on_join_room(data):
    room_code = data['roomCode']
    user_name = data['userName']
    join_room(room_code)
    if not online_users_table.get(Query().roomCode == room_code):
        online_users_table.insert({"roomCode": room_code, "users": []})
    new_message = {
        "id": uuid.uuid4().hex,
        "content": f"{user_name} has entered the room.",
        "sender": "System",
        "timestamp": datetime.now().isoformat(),
        "roomCode": room_code
    }
    emit('chat_message', new_message, to=room_code)
    user = {"id": request.sid, "name": "User"}  # Replace with actual user name
    online_users_table.update({"users": online_users_table.get(Query().roomCode == room_code)['users'] + [user]}, Query().roomCode == room_code)
    # emit('online_users_update', online_users_table.get(Query().roomCode == room_code)['users'], room=room_code)
    # emit('update_online_count', len(online_users_table.get(Query().roomCode == room_code)['users']), room=room_code)


@socketio.on('leave_room')
def on_leave_room(data):
    room_code = data['roomCode']
    leave_room(room_code)
    users = online_users_table.get(Query().roomCode == room_code)['users']
    users = [user for user in users if user['id'] != request.sid]
    online_users_table.update({"users": users}, Query().roomCode == room_code)
    # emit('online_users_update', users, room=room_code)
    # emit('update_online_count', len(users), room=room_code)


# @socketio.on('disconnect')
# def on_disconnect():
#     for room_code in online_users_table.all():
#         users = [user for user in room_code['users'] if user['id'] != request.sid]
#         online_users_table.update({"users": users}, Query().roomCode == room_code['roomCode'])
#         emit('online_users_update', users, room=room_code['roomCode'])
#         emit('update_online_count', len(users), room=room_code['roomCode'])


@socketio.on('user_activity')
def on_user_activity(data):
    # Receives: { roomCode: string }
    # This event is used to update the last activity time for the room
    # Implement your room expiry logic here
    pass

def validate_keys(gemini_key, pinecone_key):
    # Implement your key validation logic here
    return True  # Placeholder, always returns True
if __name__ == '__main__':
    socketio.run(app, allow_unsafe_werkzeug=True, host='0.0.0.0', port=5000)