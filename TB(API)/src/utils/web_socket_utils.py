from typing import Dict
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}

    async def connect(self, conversation_id: int, email: str, websocket: WebSocket):
        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = {}

        if email in self.active_connections[conversation_id]:
            old_ws = self.active_connections[conversation_id][email]
            try:
                await old_ws.close()
            except:
                pass

        self.active_connections[conversation_id][email] = websocket
        print(f"[CONNECTED] {email} → conversation {conversation_id}")

    async def disconnect(self, conversation_id: int, email: str):
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].pop(email, None)
            print(f"[DISCONNECTED] {email} from conversation {conversation_id}")

    async def broadcast(self, conversation_id: int, message: dict, exclude_email: str = None):
        """
        Broadcast to all active participants in a conversation.
        Returns True if at least one recipient received the message.
        """
        delivered = False

        if conversation_id in self.active_connections:
            for email, ws in self.active_connections[conversation_id].items():
                if exclude_email and email == exclude_email:
                    continue
                try:
                    await ws.send_json(message)
                    delivered = True   
                except:
                    pass  

        return delivered  


    def is_connected(self, conversation_id: int, email: str):
        return email in self.active_connections.get(conversation_id, {})

manager = ConnectionManager()
