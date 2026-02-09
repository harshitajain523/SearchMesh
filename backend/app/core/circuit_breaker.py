"""
Circuit Breaker Pattern Implementation

Prevents cascading failures by tracking API health and temporarily
disabling calls to failing services.
"""
import asyncio
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable, Any, Optional
import logging

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreaker:
    """
    Circuit breaker for external API calls.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: API is failing, reject requests immediately
    - HALF_OPEN: Testing if API has recovered
    
    Transitions:
    - CLOSED -> OPEN: failure_count >= threshold
    - OPEN -> HALF_OPEN: after timeout_duration
    - HALF_OPEN -> CLOSED: successful request
    - HALF_OPEN -> OPEN: failed request
    """
    name: str
    failure_threshold: int = 5
    timeout_duration: int = 30  # seconds
    
    state: CircuitState = field(default=CircuitState.CLOSED)
    failure_count: int = field(default=0)
    last_failure_time: Optional[datetime] = field(default=None)
    success_count: int = field(default=0)
    
    def __post_init__(self):
        self._lock = asyncio.Lock()
    
    @property
    def is_open(self) -> bool:
        """Check if circuit is open (blocking requests)."""
        return self.state == CircuitState.OPEN
    
    @property
    def should_allow_request(self) -> bool:
        """Determine if a request should be allowed."""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if timeout has passed
            if self.last_failure_time:
                elapsed = datetime.now() - self.last_failure_time
                if elapsed >= timedelta(seconds=self.timeout_duration):
                    return True  # Allow one test request
            return False
        
        # HALF_OPEN: allow one request to test
        return True
    
    async def record_success(self) -> None:
        """Record a successful request."""
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                logger.info(f"Circuit {self.name}: HALF_OPEN -> CLOSED (recovered)")
            
            self.success_count += 1
    
    async def record_failure(self) -> None:
        """Record a failed request."""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                logger.warning(f"Circuit {self.name}: HALF_OPEN -> OPEN (still failing)")
            
            elif self.state == CircuitState.CLOSED:
                if self.failure_count >= self.failure_threshold:
                    self.state = CircuitState.OPEN
                    logger.warning(
                        f"Circuit {self.name}: CLOSED -> OPEN "
                        f"(failures: {self.failure_count})"
                    )
    
    async def try_acquire(self) -> bool:
        """Try to acquire permission to make a request."""
        async with self._lock:
            if not self.should_allow_request:
                return False
            
            if self.state == CircuitState.OPEN:
                # Transition to half-open for test
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit {self.name}: OPEN -> HALF_OPEN (testing)")
            
            return True
    
    def get_stats(self) -> dict:
        """Get circuit breaker statistics."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
        }


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers."""
    
    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}
    
    def get_or_create(
        self, 
        name: str, 
        failure_threshold: int = 5,
        timeout_duration: int = 30
    ) -> CircuitBreaker:
        """Get existing or create new circuit breaker."""
        if name not in self._breakers:
            self._breakers[name] = CircuitBreaker(
                name=name,
                failure_threshold=failure_threshold,
                timeout_duration=timeout_duration
            )
        return self._breakers[name]
    
    def get_all_stats(self) -> list[dict]:
        """Get stats for all circuit breakers."""
        return [cb.get_stats() for cb in self._breakers.values()]


# Global registry
circuit_registry = CircuitBreakerRegistry()
