from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room, send
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

connected_clients = set()

rooms=[]
'''
rooms=[
    {
        'roomid':roomid,
        'brains':[{
            'name': username,
            'id': usersid
            }]
    }
]
'''

# Root route
@app.route('/')
def index():
    return "WebSocket server is running. Use a Socket.IO client to connect."

# API route
@app.route('/rooms/create', methods=['POST'])
def api_message_createRoom():
    return jsonify({'roomCode': '1234'})

@app.route('/rooms/join', methods=['POST'])
def api_message_joinRoom():
    return jsonify({'roomName': 'bite'})

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    connected_clients.add(request.sid)
    print(f'Client connected. Total clients: {len(connected_clients)}')
    emit('response', {'message': 'Connected successfully'})
    

@socketio.on('brainData')
def handle_brainData(data):
    added = False
    print(data)
    roomId = data['roomId']
    name = data['name']
    id = request.sid
    emit('newData', {
        'type': 'newBrain',
        'brains':[{
            'id': id,
            'name': name
        }]
    })
    for i in rooms:
        if i['roomId'] == roomId:
            i['brains'].append({
                'name': name,
                'id': id
            })
            added = True
    if added == False:
        rooms.append(
            {'roomId':roomId,
             'brains':[{
                 'name': name,
                 'id': id
                 }]
             }
        )
            
    
@socketio.on('disconnect')
def handle_disconnect():
    connected_clients.remove(request.sid)
    print(f'Client disconnected. Total clients: {len(connected_clients)}')

@socketio.on('message')
def handle_message(data):
    print('Received message:', data)
    ids=[]
    for i in rooms:
        if i['roomId'] == data['roomId']:
            for j in i['brains']:
                ids.append(j['id'])
    for i in ids:
        emit('roomMessage', {'message': f'Client {data['name']}: {data['message']}'}, to=i)
    print(ids)
    print(rooms)
    
@socketio.on('join', namespace='/chat')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ' has entered the room.', to=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    send(username + ' has left the room.', to=room)

@socketio.on('event', namespace='/chat')
def handle_chat_message(data):
    print('Received message:', data)
    # You can process the message here and emit a response if needed
    # For example, broadcasting the message to all clients in the room
    emit('chat_message', data, broadcast=True)



if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)