from CommandHandler import commandHandler
sample_data = {
  "room": {
    "code": "ab12cd34",
    "name": "General Discussion",
    "gemini_key": "sample-gemini-key",
    "pinecone_key": "sample-pinecone-key",
    "users": ["alice", "bob"],
    "creator": "alice",
    "creation_time_utc": "2024-09-15T10:00:00Z"
  },
  "messages": [
    {
      "id": "1a2b3c4d5e",
      "content": "<p>Hello everyone!</p>",
      "sender": "alice",
      "timestamp": "2024-09-15T10:05:00Z",
      "roomCode": "ab12cd34"
    },
    {
      "id": "6f7g8h9i0j",
      "content": "<p>Hi Alice!</p>",
      "sender": "bob",
      "timestamp": "2024-09-15T10:06:00Z",
      "roomCode": "ab12cd34"
    }
  ],
  "uploaded_data": [
    {
      "id": "123abc456",
      "filename": "file1.txt",
      "roomCode": "ab12cd34"
    },
    {
      "id": "789def012",
      "filename": "image.png",
      "roomCode": "ab12cd34"
    }
  ],
  "online_users": {
    "users": [
      {
        "id": "user3",
        "name": "charlie"
      },
      {
        "id": "user2",
        "name": "bob"
      },
      {
        "id": "user2",
        "name": "alice"
      }
      ]
  }
}


sample_message = {
    "id": "0987654321",
    "content": "!info lmao",
    "sender": "system",
    "timestamp": "2024-09-15T10:07:00Z",
    "roomCode": "ab12cd34"
}


ch = commandHandler(sample_message,sample_data)
content, commandName = ch.analyzeCommand()
print(commandName)
print(content)
