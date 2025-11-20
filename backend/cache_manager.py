import json
import os
from datetime import datetime, timedelta
from typing import Any, Optional

try:
    import redis.asyncio as redis  # type: ignore
except ImportError:  # pragma: no cover - Redis opcional no ambiente local
    redis = None


class CacheManager:
    """
    Fornece cache distribuído opcional com Redis e fallback automático em memória.
    Todas as operações expõem uma API assíncrona para evitar bloquear o event loop.
    """

    def __init__(self, namespace: str = "tazeai"):
        self.namespace = namespace
        self.redis_url = os.getenv("REDIS_URL")
        self._redis_client = None
        self._redis_available = False

        if self.redis_url and redis is not None:
            try:
                self._redis_client = redis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
            except Exception as exc:  # pragma: no cover
                print(f"[CACHE] Erro ao configurar Redis: {exc}. Usando apenas memória local.")
                self._redis_client = None

        # Estrutura do fallback: {chave: {"value": Any, "expires_at": datetime | None}}
        self._memory_store: dict[str, dict[str, Any]] = {}

    async def _is_redis_ready(self) -> bool:
        if not self._redis_client:
            return False

        if self._redis_available:
            return True

        try:
            await self._redis_client.ping()
            self._redis_available = True
            print("[CACHE] Redis detectado. Cache distribuído habilitado.")
            return True
        except Exception as exc:
            print(f"[CACHE] Redis indisponível ({exc}). Mantendo fallback em memória.")
            self._redis_available = False
            return False

    def _format_key(self, key: str) -> str:
        return f"{self.namespace}:{key}"

    async def get(self, key: str) -> Optional[Any]:
        """
        Retorna valor armazenado (ou None).
        """
        namespaced_key = self._format_key(key)

        if await self._is_redis_ready():
            try:
                raw_value = await self._redis_client.get(namespaced_key)  # type: ignore[union-attr]
                if raw_value is not None:
                    return json.loads(raw_value)
            except Exception as exc:
                print(f"[CACHE] Falha ao obter chave {key} do Redis: {exc}. Usando fallback.")
                self._redis_available = False

        entry = self._memory_store.get(namespaced_key)
        if not entry:
            return None

        expires_at: Optional[datetime] = entry.get("expires_at")
        if expires_at and expires_at < datetime.now():
            self._memory_store.pop(namespaced_key, None)
            return None

        return entry.get("value")

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Salva valor com TTL opcional.
        """
        namespaced_key = self._format_key(key)

        if await self._is_redis_ready():
            try:
                payload = json.dumps(value, ensure_ascii=False)
                await self._redis_client.set(  # type: ignore[union-attr]
                    namespaced_key,
                    payload,
                    ex=ttl_seconds,
                )
                return
            except Exception as exc:
                print(f"[CACHE] Falha ao salvar chave {key} no Redis: {exc}. Usando fallback.")
                self._redis_available = False

        expires_at = (
            datetime.now() + timedelta(seconds=ttl_seconds)
            if ttl_seconds
            else None
        )
        self._memory_store[namespaced_key] = {
            "value": value,
            "expires_at": expires_at,
        }

    async def delete(self, key: str) -> None:
        """
        Remove chave específica do cache.
        """
        namespaced_key = self._format_key(key)

        if await self._is_redis_ready():
            try:
                await self._redis_client.delete(namespaced_key)  # type: ignore[union-attr]
            except Exception as exc:
                print(f"[CACHE] Falha ao remover chave {key} no Redis: {exc}.")

        self._memory_store.pop(namespaced_key, None)
