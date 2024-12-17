from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import json
from .models import *
import logging
logger = logging.getLogger(__name__)
class OrderProgress(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'order_{self.room_name}'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

        try:
            orders = order.giver_order_details(self.room_name)
            self.send(text_data=json.dumps({
                'payload': orders
            }))
            logger.info(f"Data sent to frontend: {orders}")
        except Exception as e:
            logger.error(f"Error fetching order details: {str(e)}")
            self.send(text_data=json.dumps({
                'error': "Failed to fetch order details."
            }))

    def disconnect(self, close_code):
        # Remove the WebSocket connection from the room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type' : "order_status",
                'payload' : text_data
            }
        )

    def order_status(self, event):
        print(event)
        orders = json.loads(event['value'])
        try:
            orders = order.giver_order_details(self.room_name)
            self.send(text_data=json.dumps({
                'payload': orders
            }))
            logger.info(f"Data sent to frontend: {orders}")
        except Exception as e:
            logger.error(f"Error fetching order details: {str(e)}")
            self.send(text_data=json.dumps({
                'error': "Failed to fetch order details."
            }))
