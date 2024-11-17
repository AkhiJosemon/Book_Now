import json
from channels.generic.websocket import AsyncWebsocketConsumer

class BookingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("booking_seats", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("booking_seats", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        seat_number = data['seatNumber']
        action = data['action']

        # Send message to the group
        await self.channel_layer.group_send(
            "booking_seats",
            {
                'type': 'seat_selection',
                'seatNumber': seat_number,
                'action': action
            }
        )

    async def seat_selection(self, event):
        seat_number = event['seatNumber']
        action = event['action']

        await self.send(text_data=json.dumps({
            'seatNumber': seat_number,
            'action': action
        }))
