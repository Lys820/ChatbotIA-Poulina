"""
Memory Service – Conversation memory avec Redis
Stocke historique questions/réponses par session utilisateur.

Redis structure:
  - conversation:{session_id} = liste JSON messages
  - session_metadata:{session_id} = info session
  - active_sessions = set session_ids actives
"""

import redis
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import uuid

log = logging.getLogger(__name__)


class RedisConversationMemory:
    """
    Gère mémoire conversation dans Redis.
    
    Chaque session = liste de messages (Q/A pairs).
    Messages = JSON avec timestamp, contexte, metadata.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379", ttl_hours: int = 24):
        """
        Init connexion Redis.
        
        Args:
            redis_url: URL Redis (défaut: localhost:6379)
            ttl_hours: Durée vie session avant expiration (heures)
        """
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # Test connexion
            self.redis_client.ping()
            log.info("✓ Redis connecté")
        except Exception as e:
            log.error(f"❌ Erreur connexion Redis: {e}")
            self.redis_client = None

        self.ttl_seconds = ttl_hours * 3600
        self.conversation_prefix = "conversation:"
        self.metadata_prefix = "session_metadata:"
        self.sessions_key = "active_sessions"

    def is_available(self) -> bool:
        """Vérifie si Redis est disponible"""
        return self.redis_client is not None

    def create_session(self) -> str:
        """Crée nouvelle session, retourne session_id"""
        if not self.is_available():
            log.warning("Redis indisponible, session en RAM seulement")
            return str(uuid.uuid4())

        session_id = str(uuid.uuid4())

        # Enregistre session metadata
        metadata = {
            "session_id": session_id,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "message_count": 0,
        }

        try:
            key = f"{self.metadata_prefix}{session_id}"
            self.redis_client.hset(
                key,
                mapping={k: json.dumps(v) if not isinstance(v, str) else v for k, v in metadata.items()}
            )
            self.redis_client.expire(key, self.ttl_seconds)

            # Ajoute à set sessions actives
            self.redis_client.sadd(self.sessions_key, session_id)

            log.info(f"✓ Session créée: {session_id}")
            return session_id
        except Exception as e:
            log.error(f"❌ Erreur création session: {e}")
            return session_id

    def add_exchange(
        self,
        session_id: str,
        question: str,
        answer: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Ajoute paire Q/A à historique session.
        
        Args:
            session_id: ID session
            question: Question utilisateur
            answer: Réponse IA
            metadata: Context additionnel (centres, labos, model, etc.)
        
        Returns:
            True si succès
        """
        if not self.is_available():
            log.warning("Redis indisponible, message non stocké")
            return False

        try:
            message = {
                "timestamp": datetime.utcnow().isoformat(),
                "question": question,
                "answer": answer,
                "metadata": metadata or {},
            }

            key = f"{self.conversation_prefix}{session_id}"

            # Ajoute message à liste (LPUSH = ajoute au début)
            self.redis_client.lpush(key, json.dumps(message))

            # Expire session
            self.redis_client.expire(key, self.ttl_seconds)

            # Met à jour timestamp last_activity
            meta_key = f"{self.metadata_prefix}{session_id}"
            self.redis_client.hset(
                meta_key,
                "last_activity",
                datetime.utcnow().isoformat()
            )

            # Incrémente counter
            self.redis_client.hincrby(meta_key, "message_count", 1)

            log.debug(f"✓ Message ajouté: session={session_id}")
            return True

        except Exception as e:
            log.error(f"❌ Erreur ajout message: {e}")
            return False

    def get_context_window(
        self,
        session_id: str,
        num_messages: int = 5,
        include_metadata: bool = True,
    ) -> str:
        """
        Récupère derniers messages pour enrichir LLM prompt.
        Format: "Q: ... A: ... Q: ... A: ..."
        
        Args:
            session_id: ID session
            num_messages: Nombre messages à récupérer
            include_metadata: Inclure contexte metadata
        
        Returns:
            String formaté pour prompt LLM
        """
        if not self.is_available():
            return ""

        try:
            key = f"{self.conversation_prefix}{session_id}"

            # Récupère derniers N messages (LRANGE 0 N-1 retourne du plus récent)
            messages_json = self.redis_client.lrange(key, 0, num_messages - 1)

            if not messages_json:
                return ""

            formatted = []
            for i, msg_json in enumerate(messages_json, 1):
                msg = json.loads(msg_json)

                # Format simple
                q = msg["question"][:100]
                a = msg["answer"][:150]

                formatted.append(f"Message {i}:")
                formatted.append(f"  Q: {q}")
                formatted.append(f"  A: {a}...")

                # Ajouter metadata si demandé
                if include_metadata and msg.get("metadata"):
                    meta = msg["metadata"]
                    if meta.get("model_used"):
                        formatted.append(f"  [Model: {meta['model_used']}]")
                    if meta.get("centres_count"):
                        formatted.append(f"  [Centres trouvés: {meta['centres_count']}]")

            context = "\n".join(formatted)
            log.debug(f"✓ Context window: {len(messages_json)} messages")
            return context

        except Exception as e:
            log.error(f"❌ Erreur context window: {e}")
            return ""

    def get_full_history(
        self,
        session_id: str,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Récupère historique complet session (toutes messages).
        
        Args:
            session_id: ID session
            limit: Max messages à retourner
        
        Returns:
            List dictionnaires messages
        """
        if not self.is_available():
            return []

        try:
            key = f"{self.conversation_prefix}{session_id}"
            messages_json = self.redis_client.lrange(key, 0, limit - 1)

            messages = [json.loads(msg) for msg in messages_json]
            return messages

        except Exception as e:
            log.error(f"❌ Erreur historique: {e}")
            return []

    def get_session_metadata(self, session_id: str) -> Dict[str, Any]:
        """Récupère metadata session (created_at, message_count, etc.)"""
        if not self.is_available():
            return {}

        try:
            key = f"{self.metadata_prefix}{session_id}"
            metadata = self.redis_client.hgetall(key)

            # Convertir JSON strings
            for k, v in metadata.items():
                try:
                    metadata[k] = json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    pass

            return metadata

        except Exception as e:
            log.error(f"❌ Erreur metadata: {e}")
            return {}

    def clear_session(self, session_id: str) -> bool:
        """Efface session (pour logout, etc.)"""
        if not self.is_available():
            return False

        try:
            self.redis_client.delete(f"{self.conversation_prefix}{session_id}")
            self.redis_client.delete(f"{self.metadata_prefix}{session_id}")
            self.redis_client.srem(self.sessions_key, session_id)

            log.info(f"✓ Session effacée: {session_id}")
            return True

        except Exception as e:
            log.error(f"❌ Erreur effacement session: {e}")
            return False

    def get_active_sessions(self) -> List[str]:
        """Retourne liste session_ids actives"""
        if not self.is_available():
            return []

        try:
            return list(self.redis_client.smembers(self.sessions_key))
        except Exception as e:
            log.error(f"❌ Erreur sessions actives: {e}")
            return []

    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Retourne stats session (durée, nb messages, etc.)"""
        try:
            metadata = self.get_session_metadata(session_id)

            created_at = datetime.fromisoformat(metadata.get("created_at", datetime.utcnow().isoformat()))
            last_activity = datetime.fromisoformat(metadata.get("last_activity", datetime.utcnow().isoformat()))

            duration_seconds = (last_activity - created_at).total_seconds()
            message_count = int(metadata.get("message_count", 0))

            return {
                "session_id": session_id,
                "created_at": metadata.get("created_at"),
                "last_activity": metadata.get("last_activity"),
                "duration_seconds": duration_seconds,
                "message_count": message_count,
                "messages_per_minute": (message_count / (duration_seconds / 60)) if duration_seconds > 0 else 0,
            }

        except Exception as e:
            log.error(f"❌ Erreur stats: {e}")
            return {}

    def cleanup_expired_sessions(self) -> int:
        """
        Nettoie sessions expirées (appel manuel ou cron).
        Redis expire automatiquement, mais cette fonction nettoie
        les orphelins du set active_sessions.
        """
        if not self.is_available():
            return 0

        try:
            active = self.get_active_sessions()
            cleaned = 0

            for session_id in active:
                meta_key = f"{self.metadata_prefix}{session_id}"
                # Si metadata n'existe plus, session a expiré
                if not self.redis_client.exists(meta_key):
                    self.redis_client.srem(self.sessions_key, session_id)
                    cleaned += 1

            if cleaned > 0:
                log.info(f"✓ {cleaned} sessions expirées nettoyées")

            return cleaned

        except Exception as e:
            log.error(f"❌ Erreur cleanup: {e}")
            return 0


# Singleton global
memory_service: Optional[RedisConversationMemory] = None


def init_memory_service(redis_url: str = "redis://localhost:6379") -> RedisConversationMemory:
    """Factory - initialise singleton"""
    global memory_service
    memory_service = RedisConversationMemory(redis_url)
    return memory_service


def get_memory_service() -> RedisConversationMemory:
    """Récupère singleton"""
    global memory_service
    if memory_service is None:
        memory_service = RedisConversationMemory()
    return memory_service