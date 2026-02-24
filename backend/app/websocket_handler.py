"""
Example WebSocket handler structure for quiz sessions
This shows how to handle real-time communication between host and participants
"""
from fastapi import WebSocket, WebSocketDisconnect
import json

class ConnectionManager:
    """Manages WebSocket connections for quiz sessions"""
    
    def __init__(self):
        # session_code -> { "host": WebSocket, "participants": { participant_id: WebSocket } }
        self.sessions: dict[str, dict] = {}
    
    async def connect_host(self, session_code: str, websocket: WebSocket):
        """Connect quiz host"""
        await websocket.accept()
        if session_code not in self.sessions:
            self.sessions[session_code] = {"host": None, "participants": {}}
        self.sessions[session_code]["host"] = websocket
    
    async def connect_participant(
        self, 
        session_code: str, 
        participant_id: str, 
        websocket: WebSocket
    ):
        """Connect participant to quiz session"""
        await websocket.accept()
        if session_code not in self.sessions:
            self.sessions[session_code] = {"host": None, "participants": {}}
        self.sessions[session_code]["participants"][participant_id] = websocket
        
        # Notify host of new participant
        if self.sessions[session_code]["host"]:
            await self.send_to_host(session_code, {
                "type": "participant_joined",
                "participant_id": participant_id
            })
    
    def disconnect(self, session_code: str, participant_id: str = None):
        """Disconnect a participant or host"""
        if session_code in self.sessions:
            if participant_id:
                self.sessions[session_code]["participants"].pop(participant_id, None)
            else:
                # Host disconnected - clean up session
                self.sessions.pop(session_code, None)
    
    async def send_to_host(self, session_code: str, message: dict):
        """Send message to host"""
        if session_code in self.sessions and self.sessions[session_code]["host"]:
            try:
                await self.sessions[session_code]["host"].send_json(message)
            except:
                pass
    
    async def send_to_participant(
        self, 
        session_code: str, 
        participant_id: str, 
        message: dict
    ):
        """Send message to specific participant"""
        if session_code in self.sessions:
            websocket = self.sessions[session_code]["participants"].get(participant_id)
            if websocket:
                try:
                    await websocket.send_json(message)
                except:
                    pass
    
    async def broadcast_to_participants(self, session_code: str, message: dict):
        """Broadcast message to all participants"""
        if session_code in self.sessions:
            for websocket in self.sessions[session_code]["participants"].values():
                try:
                    await websocket.send_json(message)
                except:
                    pass
    
    async def broadcast_to_all(self, session_code: str, message: dict):
        """Broadcast to host and all participants"""
        await self.send_to_host(session_code, message)
        await self.broadcast_to_participants(session_code, message)


# Global connection manager instance
manager = ConnectionManager()


async def handle_host_message(session_code: str, message: dict):
    """Process messages from host"""
    msg_type = message.get("type")
    
    if msg_type == "next_question":
        # Broadcast next question to all participants
        question_data = message.get("question")
        await manager.broadcast_to_participants(session_code, {
            "type": "question_start",
            "question": question_data
        })
    
    elif msg_type == "end_session":
        # End the session
        await manager.broadcast_to_all(session_code, {
            "type": "session_ended"
        })
    
    elif msg_type == "score_answer":
        # Manual scoring for open-ended questions
        participant_id = message.get("participant_id")
        score = message.get("score")
        # Update score in database
        # Send updated leaderboard to all
        await manager.broadcast_to_all(session_code, {
            "type": "leaderboard_update",
            "leaderboard": []  # Fetch from database
        })


async def handle_participant_message(
    session_code: str, 
    participant_id: str, 
    message: dict
):
    """Process messages from participant"""
    msg_type = message.get("type")
    
    if msg_type == "submit_answer":
        # Save answer to database
        answer = message.get("answer")
        question_id = message.get("question_id")
        
        # Calculate score for auto-gradable questions
        # score = calculate_score(question_id, answer)
        
        # Notify host
        await manager.send_to_host(session_code, {
            "type": "answer_submitted",
            "participant_id": participant_id,
            "question_id": question_id
        })
        
        # Send confirmation to participant
        await manager.send_to_participant(session_code, participant_id, {
            "type": "answer_received",
            "question_id": question_id
        })


# Example router implementation
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

# router = APIRouter()
#
# @router.websocket("/session/{session_code}")
# async def websocket_endpoint(
#     websocket: WebSocket,
#     session_code: str,
#     token: Optional[str] = None,
#     name: Optional[str] = None
# ):
#     is_host = bool(token)
#
#     try:
#         if is_host:
#             # Authenticate and connect host
#             user = await authenticate_user(token)
#             await manager.connect_host(session_code, websocket)
#
#             while True:
#                 data = await websocket.receive_json()
#                 await handle_host_message(session_code, data)
#
#         else:
#             # Connect participant
#             # Register participant in database
#             participant_id = await register_participant(session_code, name)
#             await manager.connect_participant(session_code, participant_id, websocket)
#
#             while True:
#                 data = await websocket.receive_json()
#                 await handle_participant_message(session_code, participant_id, data)
#
#     except WebSocketDisconnect:
#         if is_host:
#             manager.disconnect(session_code)
#         else:
#             manager.disconnect(session_code, participant_id)

