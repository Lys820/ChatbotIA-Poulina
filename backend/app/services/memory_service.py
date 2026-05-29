"""
Service de memoire conversationnelle.
Stocke et recupere l historique de session depuis SQL Server.
"""
from __future__ import annotations

import json
import logging
import uuid

log = logging.getLogger(__name__)

MAX_MESSAGES_IN_CONTEXT = 10


class MemoryService:

    def __init__(self, db):
        self._db = db

    def create_session(self, user_id: int) -> str:
        session_id = str(uuid.uuid4())
        self._db.create_session(session_id, user_id)
        return session_id

    def get_history(self, session_id: str) -> list[dict]:
        return self._db.get_messages(session_id, limit=MAX_MESSAGES_IN_CONTEXT * 2)

    def add_message(self, session_id: str, role: str, content: str) -> None:
        self._db.add_message(session_id, role, content)

    def close_session(self, session_id: str) -> None:
        self._db.update_session_inactive(session_id)

    def session_belongs_to_user(self, session_id: str, user_id: int) -> bool:
        session = self._db.get_session(session_id)
        if not session:
            return False
        return int(session["id_utilisateur"]) == user_id and bool(session["actif"])