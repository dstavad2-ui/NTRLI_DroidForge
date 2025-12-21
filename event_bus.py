"""
DroidForge Event Bus
====================
Decoupled event-driven communication system for inter-component messaging.
Enables loose coupling between modules while maintaining deterministic behavior.
"""

import threading
from typing import Dict, List, Callable, Any, Optional
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
import queue

from utils.logger import get_logger


@dataclass
class Event:
    """Represents an event in the system."""
    name: str
    args: tuple
    kwargs: dict
    timestamp: datetime
    source: Optional[str] = None


class EventBus:
    """
    Central Event Bus for DroidForge.
    
    Features:
    - Publish/subscribe pattern
    - Synchronous and asynchronous event handling
    - Event history for debugging
    - Thread-safe operations
    - Wildcard subscriptions
    """
    
    def __init__(self, async_mode: bool = False, history_size: int = 100):
        self.logger = get_logger("EventBus")
        self.async_mode = async_mode
        self.history_size = history_size
        
        # Subscriber storage
        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._once_subscribers: Dict[str, List[Callable]] = defaultdict(list)
        
        # Event history
        self._history: List[Event] = []
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Async queue (if enabled)
        self._event_queue: Optional[queue.Queue] = None
        self._worker_thread: Optional[threading.Thread] = None
        
        if async_mode:
            self._start_async_worker()
        
        self.logger.info(f"EventBus initialized (async={async_mode})")
    
    def _start_async_worker(self):
        """Start async event processing worker."""
        self._event_queue = queue.Queue()
        self._worker_thread = threading.Thread(
            target=self._async_worker_loop,
            daemon=True,
            name="EventBus-Worker"
        )
        self._worker_thread.start()
    
    def _async_worker_loop(self):
        """Process events asynchronously."""
        while True:
            try:
                event = self._event_queue.get()
                if event is None:  # Shutdown signal
                    break
                self._dispatch_event(event)
            except Exception as e:
                self.logger.error(f"Async worker error: {e}")
    
    def subscribe(self, event_name: str, callback: Callable):
        """
        Subscribe to an event.
        
        Args:
            event_name: Name of the event (supports wildcards like "build.*")
            callback: Function to call when event is emitted
        """
        with self._lock:
            self._subscribers[event_name].append(callback)
        self.logger.debug(f"Subscribed to: {event_name}")
    
    def subscribe_once(self, event_name: str, callback: Callable):
        """
        Subscribe to an event for one-time handling.
        
        Args:
            event_name: Name of the event
            callback: Function to call once
        """
        with self._lock:
            self._once_subscribers[event_name].append(callback)
        self.logger.debug(f"Subscribed once to: {event_name}")
    
    def unsubscribe(self, event_name: str, callback: Callable):
        """
        Unsubscribe from an event.
        
        Args:
            event_name: Name of the event
            callback: Function to remove
        """
        with self._lock:
            if event_name in self._subscribers:
                try:
                    self._subscribers[event_name].remove(callback)
                except ValueError:
                    pass
    
    def emit(self, event_name: str, *args, source: str = None, **kwargs):
        """
        Emit an event.
        
        Args:
            event_name: Name of the event
            *args: Positional arguments for handlers
            source: Optional source identifier
            **kwargs: Keyword arguments for handlers
        """
        event = Event(
            name=event_name,
            args=args,
            kwargs=kwargs,
            timestamp=datetime.now(),
            source=source
        )
        
        # Add to history
        self._add_to_history(event)
        
        if self.async_mode and self._event_queue:
            self._event_queue.put(event)
        else:
            self._dispatch_event(event)
    
    def _dispatch_event(self, event: Event):
        """Dispatch event to all matching subscribers."""
        with self._lock:
            # Get exact match subscribers
            handlers = list(self._subscribers.get(event.name, []))
            
            # Get wildcard subscribers
            for pattern, callbacks in self._subscribers.items():
                if self._matches_pattern(event.name, pattern):
                    handlers.extend(callbacks)
            
            # Get once subscribers
            once_handlers = self._once_subscribers.pop(event.name, [])
            handlers.extend(once_handlers)
        
        # Dispatch to handlers
        for handler in handlers:
            try:
                handler(*event.args, **event.kwargs)
            except Exception as e:
                self.logger.error(
                    f"Handler error for {event.name}: {e}",
                    exc_info=True
                )
        
        self.logger.debug(
            f"Dispatched {event.name} to {len(handlers)} handlers"
        )
    
    def _matches_pattern(self, event_name: str, pattern: str) -> bool:
        """Check if event name matches a pattern (supports * wildcard)."""
        if pattern == event_name:
            return False  # Avoid duplicate dispatch for exact match
        
        if pattern.endswith(".*"):
            prefix = pattern[:-2]
            return event_name.startswith(prefix + ".")
        
        if pattern == "*":
            return True
        
        return False
    
    def _add_to_history(self, event: Event):
        """Add event to history, maintaining size limit."""
        with self._lock:
            self._history.append(event)
            if len(self._history) > self.history_size:
                self._history = self._history[-self.history_size:]
    
    def get_history(self, event_name: str = None, limit: int = 50) -> List[Event]:
        """
        Get event history.
        
        Args:
            event_name: Filter by event name (optional)
            limit: Maximum events to return
            
        Returns:
            List of Event objects
        """
        with self._lock:
            if event_name:
                events = [e for e in self._history if e.name == event_name]
            else:
                events = list(self._history)
            return events[-limit:]
    
    def clear_history(self):
        """Clear event history."""
        with self._lock:
            self._history.clear()
    
    def get_subscribers(self, event_name: str = None) -> Dict[str, int]:
        """
        Get subscriber counts.
        
        Args:
            event_name: Specific event, or None for all
            
        Returns:
            Dictionary of event names to subscriber counts
        """
        with self._lock:
            if event_name:
                return {event_name: len(self._subscribers.get(event_name, []))}
            return {k: len(v) for k, v in self._subscribers.items()}
    
    def wait_for(self, event_name: str, timeout: float = None) -> Optional[Event]:
        """
        Wait for a specific event (blocking).
        
        Args:
            event_name: Event to wait for
            timeout: Maximum wait time in seconds
            
        Returns:
            Event object if received, None if timeout
        """
        result_queue = queue.Queue()
        
        def handler(*args, **kwargs):
            result_queue.put(Event(
                name=event_name,
                args=args,
                kwargs=kwargs,
                timestamp=datetime.now()
            ))
        
        self.subscribe_once(event_name, handler)
        
        try:
            return result_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def shutdown(self):
        """Shutdown the event bus."""
        if self._event_queue:
            self._event_queue.put(None)
        if self._worker_thread:
            self._worker_thread.join(timeout=2.0)
        self.logger.info("EventBus shutdown complete")


# Convenience functions for global event bus
_global_bus: Optional[EventBus] = None


def get_global_bus() -> EventBus:
    """Get or create global event bus."""
    global _global_bus
    if _global_bus is None:
        _global_bus = EventBus()
    return _global_bus


def emit(event_name: str, *args, **kwargs):
    """Emit event on global bus."""
    get_global_bus().emit(event_name, *args, **kwargs)


def subscribe(event_name: str, callback: Callable):
    """Subscribe on global bus."""
    get_global_bus().subscribe(event_name, callback)
