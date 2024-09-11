import uuid
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", engineio_logger=True)
# socketio = SocketIO(logger=True, engineio_logger=True)
# In-memory storage (replace with a database in a production environment)
rooms = {}
messages = {}
online_users = {}
uploaded_data = {}
import random
import string

def generate_alphanumeric_string():
    characters = string.ascii_lowercase + string.digits
    def generate_group():
        return ''.join(random.choices(characters, k=3))
    group1 = generate_group()
    group2 = generate_group()
    group3 = generate_group()
    return f"{group1}{group2}{group3}"

@app.route('/api/rooms/create', methods=['POST'])
def create_room():
    # Receives: { roomName: string, geminiKey: string, pineconeKey: string }
    # Returns: { roomCode: string } or { message: string } on error
    data = request.json
    room_name = data.get('roomName')
    gemini_key = data.get('geminiKey')
    pinecone_key = data.get('pineconeKey')
    
    # Validate keys (implement your validation logic here)
    if not validate_keys(gemini_key, pinecone_key):
        return jsonify({"message": "Invalid Gemini or Pinecone key"}), 400

    room_code = generate_alphanumeric_string()
    print(room_code, room_name, gemini_key, pinecone_key)
    rooms[room_code] = {"name": room_name, "gemini_key": gemini_key, "pinecone_key": pinecone_key}
    return jsonify({"roomCode": room_code})

@app.route('/api/rooms/join', methods=['POST'])
def join_room_api():
    # Receives: { roomCode: string }
    # Returns: { roomName: string } or { message: string } on error
    data = request.json
    room_code = data.get('roomCode')

    if room_code not in rooms:
        return jsonify({"message": "Room not found"}), 404

    return jsonify({"roomName": rooms[room_code]["name"]})

@app.route('/api/messages/', methods=['GET'])
def get_messages():
    # Receives: roomCode as query parameter
    # Returns: [{ id: string, content: string, sender: string, timestamp: string }]
    room_code = request.args.get('roomCode')
    return jsonify(messages.get(room_code, []))

@app.route('/api/send-message', methods=['POST'])
def send_message():
    # Receives: { roomCode: string, content: string }
    # Returns: { success: boolean }
    data = request.json
    room_code = data.get('roomCode')
    content = data.get('content')
    
    if room_code not in messages:
        messages[room_code] = []
    
    new_message = {
        "id": generate_alphanumeric_string(),
        "content": content,
        "sender": "User",  # Replace with actual user identification
        "timestamp": datetime.now().isoformat()
    }
    messages[room_code].append(new_message)
    
    # Emit the new message to all clients in the room
    socketio.emit('chat_message', new_message, room=room_code)
    
    return jsonify({"success": True})

@app.route('/api/online-users', methods=['GET'])
def get_online_users():
    print("online user requested")
    # Receives: roomCode as query parameter
    # Returns: [{ id: string, name: string }]
    room_code = request.args.get('roomCode')
    return jsonify(online_users.get(room_code, []))

@app.route('/api/uploaded-data', methods=['GET'])
def get_uploaded_data():
    # Receives: roomCode as query parameter
    # Returns: [{ id: string, filename: string }]
    room_code = request.args.get('roomCode')
    return jsonify(uploaded_data.get(room_code, []))

@app.route('/api/upload', methods=['POST'])
def upload_file():
    # Receives: file in form-data, roomCode in form-data
    # Returns: { success: boolean }
    room_code = request.form.get('roomCode')
    file = request.files.get('file')
    
    if not file:
        return jsonify({"success": False, "message": "No file provided"}), 400
    
    if room_code not in uploaded_data:
        uploaded_data[room_code] = []
    
    file_data = {
        "id": generate_alphanumeric_string(),
        "filename": file.filename
    }
    uploaded_data[room_code].append(file_data)
    
    # Save the file (implement your file saving logic here)
    # file.save(os.path.join(upload_folder, file.filename))
    
    # Notify all clients in the room about the new file
    socketio.emit('uploaded_data_update', uploaded_data[room_code], room=room_code)
    
    return jsonify({"success": True})

@app.route('/api/export-room', methods=['GET'])
def export_room():
    # Receives: roomCode as query parameter
    # Returns: JSON file with room data
    room_code = request.args.get('roomCode')
    if room_code not in rooms:
        return jsonify({"message": "Room not found"}), 404
    
    room_data = {
        "room": rooms[room_code],
        "messages": messages.get(room_code, []),
        "uploaded_data": uploaded_data.get(room_code, [])
    }
    
    return jsonify(room_data)

@socketio.on('chat_message')
def handle_chat_message(data):
    print('Received message:', data)
    
    room_code = data.get('roomCode')
    content = data.get('content')

    if not room_code or not content:
        print('Error: Missing roomCode or content')
        return

    # Add message to the room's message list
    if room_code not in messages:
        messages[room_code] = []

    new_message = {
        "id": uuid.uuid4().hex,
        "content": content,
        "sender": "User",  # You can replace this with actual user identification
        "timestamp": datetime.now().isoformat()
    }
    
    messages[room_code].append(new_message)

    # Emit the new message to all clients in the room
    print(f'Emitting message to room {room_code}:', new_message)
    emit('chat_message', new_message, room=room_code)

@socketio.on('join_room')
def on_join_room(data):
    # Receives: { roomCode: string }
    room_code = data['roomCode']
    print(f"User {request.sid} joined room: {room_code}")
    room_code = data['roomCode']
    join_room(room_code)
    if room_code not in online_users:
        online_users[room_code] = []
    user = {"id": request.sid, "name": "User"}  # Replace with actual user name
    online_users[room_code].append(user)
    emit('online_users_update', online_users[room_code], room=room_code)
    emit('update_online_count', len(online_users[room_code]), room=room_code)

@socketio.on('leave_room')
def on_leave_room(data):
    # Receives: { roomCode: string }
    room_code = data['roomCode']
    leave_room(room_code)
    if room_code in online_users:
        online_users[room_code] = [user for user in online_users[room_code] if user['id'] != request.sid]
        emit('online_users_update', online_users[room_code], room=room_code)
        emit('update_online_count', len(online_users[room_code]), room=room_code)

@socketio.on('disconnect')
def on_disconnect():
    for room_code, users in online_users.items():
        users = [user for user in users if user['id'] != request.sid]
        online_users[room_code] = users
        emit('online_users_update', users, room=room_code)
        emit('update_online_count', len(users), room=room_code)

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