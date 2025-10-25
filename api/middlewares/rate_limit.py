"""
Rate limiting middleware
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from time import time
from typing import Dict, Tuple

from api.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware для ограничения количества запросов
    """
    
    def __init__(self, app):
        super().__init__(app)
        # Хранилище: {user_id: [(timestamp, count)]}
        self.requests: Dict[str, list[Tuple[float, int]]] = defaultdict(list)
    
    ADMIN_BYPASS_PREFIXES = (
        "/api/quizzes",
        "/api/users",
        "/api/analytics",
    )

    async def dispatch(self, request: Request, call_next):
        # Пропускаем health check и docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Пропускаем административные маршруты, где rate limit не нужен
        if request.url.path.startswith(self.ADMIN_BYPASS_PREFIXES):
            return await call_next(request)
        
        # Получаем идентификатор клиента (IP или user_id из headers)
        client_id = request.headers.get("X-User-ID") or request.client.host
        
        # Очищаем старые записи
        current_time = time()
        self.requests[client_id] = [
            (ts, count) for ts, count in self.requests[client_id]
            if current_time - ts < settings.RATE_LIMIT_PERIOD
        ]
        
        # Подсчитываем количество запросов
        total_requests = sum(count for _, count in self.requests[client_id])
        
        # Проверяем лимит
        if total_requests >= settings.RATE_LIMIT_REQUESTS:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_PERIOD} seconds."
            )
        
        # Добавляем текущий запрос
        self.requests[client_id].append((current_time, 1))
        
        # Обрабатываем запрос
        response = await call_next(request)
        
        # Добавляем заголовки с информацией о лимите
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(
            settings.RATE_LIMIT_REQUESTS - total_requests - 1
        )
        
        return response
