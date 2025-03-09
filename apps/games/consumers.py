import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from .models import GameRoom, GamePlayer, GameChat

class GameRoomConsumer(AsyncWebsocketConsumer):
    """Oyun odası WebSocket consumer'ı"""

    async def connect(self):
        """WebSocket bağlantısı kurulduğunda"""
        self.room_pk = self.scope['url_route']['kwargs']['room_pk']
        self.room_group_name = f'room_{self.room_pk}'

        # Odayı ve oyuncuyu kontrol et
        try:
            room = await self.get_room()
            player = await self.get_player()
            if not room or not player:
                await self.close()
                return
        except ObjectDoesNotExist:
            await self.close()
            return

        # Odaya katıl
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Diğer oyunculara bildir
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_joined',
                'message': f'{player.user.username} odaya katıldı.'
            }
        )

    async def disconnect(self, close_code):
        """WebSocket bağlantısı kesildiğinde"""
        try:
            player = await self.get_player()
            if player:
                # Diğer oyunculara bildir
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'player_left',
                        'message': f'{player.user.username} odadan ayrıldı.'
                    }
                )
        except ObjectDoesNotExist:
            pass

        # Odadan ayrıl
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """İstemciden mesaj alındığında"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'drawing_update':
                await self.handle_drawing_update(data)
            elif message_type == 'guess':
                await self.handle_guess(data)
            elif message_type == 'ready_status':
                await self.handle_ready_status(data)
        except json.JSONDecodeError:
            pass

    async def handle_chat_message(self, data):
        """Sohbet mesajı işleme"""
        player = await self.get_player()
        if not player:
            return

        message = data.get('message', '').strip()
        if not message:
            return

        # Mesajı kaydet
        await self.save_chat_message(player, message)

        # Diğer oyunculara ilet
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'player': player.user.username,
                'message': message
            }
        )

    async def handle_drawing_update(self, data):
        """Çizim güncellemesi işleme"""
        player = await self.get_player()
        if not player:
            return

        room = await self.get_room()
        current_round = await self.get_current_round(room)
        
        if not current_round or current_round.current_player != player:
            return

        # Çizim verilerini güncelle
        drawing_data = data.get('drawing_data')
        if drawing_data:
            await self.update_drawing(current_round, drawing_data)

            # Diğer oyunculara ilet
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'drawing_updated',
                    'drawing_data': drawing_data
                }
            )

    async def handle_guess(self, data):
        """Tahmin işleme"""
        player = await self.get_player()
        if not player:
            return

        room = await self.get_room()
        current_round = await self.get_current_round(room)
        
        if not current_round or current_round.current_player == player:
            return

        guess = data.get('guess', '').strip().lower()
        if not guess:
            return

        # Tahmini kaydet ve kontrol et
        is_correct = await self.check_guess(current_round, player, guess)

        # Diğer oyunculara ilet
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'guess_made',
                'player': player.user.username,
                'guess': guess,
                'is_correct': is_correct
            }
        )

    async def handle_ready_status(self, data):
        """Hazır durumu işleme"""
        player = await self.get_player()
        if not player:
            return

        is_ready = data.get('is_ready', False)
        await self.update_ready_status(player, is_ready)

        # Diğer oyunculara ilet
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'ready_status_changed',
                'player': player.user.username,
                'is_ready': is_ready
            }
        )

    # Event handlers
    async def chat_message(self, event):
        """Sohbet mesajı gönderme"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'player': event['player'],
            'message': event['message']
        }))

    async def drawing_updated(self, event):
        """Çizim güncellemesi gönderme"""
        await self.send(text_data=json.dumps({
            'type': 'drawing_updated',
            'drawing_data': event['drawing_data']
        }))

    async def guess_made(self, event):
        """Tahmin gönderme"""
        await self.send(text_data=json.dumps({
            'type': 'guess_made',
            'player': event['player'],
            'guess': event['guess'],
            'is_correct': event['is_correct']
        }))

    async def ready_status_changed(self, event):
        """Hazır durumu gönderme"""
        await self.send(text_data=json.dumps({
            'type': 'ready_status_changed',
            'player': event['player'],
            'is_ready': event['is_ready']
        }))

    async def player_joined(self, event):
        """Oyuncu katılma bildirimi gönderme"""
        await self.send(text_data=json.dumps({
            'type': 'player_joined',
            'message': event['message']
        }))

    async def player_left(self, event):
        """Oyuncu ayrılma bildirimi gönderme"""
        await self.send(text_data=json.dumps({
            'type': 'player_left',
            'message': event['message']
        }))

    async def game_started(self, event):
        """Oyun başlama bildirimi gönderme"""
        await self.send(text_data=json.dumps({
            'type': 'game_started',
            'message': event['message']
        }))

    async def game_ended(self, event):
        """Oyun bitme bildirimi gönderme"""
        await self.send(text_data=json.dumps({
            'type': 'game_ended',
            'message': event['message']
        }))

    # Database operations
    @database_sync_to_async
    def get_room(self):
        """Oda bilgisini getir"""
        try:
            return GameRoom.objects.get(pk=self.room_pk)
        except GameRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def get_player(self):
        """Oyuncu bilgisini getir"""
        try:
            return GamePlayer.objects.get(
                room_id=self.room_pk,
                user=self.scope['user']
            )
        except GamePlayer.DoesNotExist:
            return None

    @database_sync_to_async
    def get_current_round(self, room):
        """Mevcut turu getir"""
        return room.rounds.filter(finished_at__isnull=True).first()

    @database_sync_to_async
    def save_chat_message(self, player, message):
        """Sohbet mesajını kaydet"""
        GameChat.objects.create(
            room_id=self.room_pk,
            player=player,
            message=message
        )

    @database_sync_to_async
    def update_drawing(self, round, drawing_data):
        """Çizim verilerini güncelle"""
        round.drawing_data = drawing_data
        round.save(update_fields=['drawing_data'])

    @database_sync_to_async
    def check_guess(self, round, player, guess):
        """Tahmini kontrol et"""
        is_correct = guess == round.word.lower()
        if is_correct:
            # Doğru tahmin işlemleri burada yapılacak
            pass
        return is_correct

    @database_sync_to_async
    def update_ready_status(self, player, is_ready):
        """Hazır durumunu güncelle"""
        player.is_ready = is_ready
        player.save(update_fields=['is_ready']) 