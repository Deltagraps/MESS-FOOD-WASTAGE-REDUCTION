import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from server import features



def machine_data_processor(message):
      data = json.loads(message)
      machine_type = data['id'][0]
      match machine_type:
            case 'R':
                  return features.reg_handler(data)
            case 'L':
                  return features.plate_handler(data)
            case 'W':
                  return features.weight_handler(data)
            case 'E':
                  pass




class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_group_name = 'hostel5'
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        # text_data_json = json.loads(text_data)
        # message = text_data_json["message"]
        message = text_data
        print(message)
        reply = machine_data_processor(message)
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "chat_message", "message": reply}
        )

    # Receive message from room group
    def chat_message(self, event):
        reply = event["message"]
        # Send message to WebSocket
        self.send(text_data=json.dumps(reply))