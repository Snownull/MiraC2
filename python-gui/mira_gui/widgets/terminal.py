"""
Terminal widget for displaying logs with cyberpunk styling
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
from typing import Dict, Any

from ..config import get_color, get_font

class TerminalWidget:
    """Terminal-style log display widget"""
    
    def __init__(self, parent, config: Dict[str, Any], backend_client):
        self.parent = parent
        self.config = config
        self.backend_client = backend_client
        self.log_entries = []
        self.max_entries = config.get("logging", {}).get("max_entries", 1000)
        self.auto_scroll = config.get("logging", {}).get("auto_scroll", True)
        
        self._create_interface()
        self._add_welcome_message()
    
    def _create_interface(self):
        """Create the terminal interface"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame, style='Card.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, 
                              text="💻 Terminal Output",
                              style='Header.TLabel')
        title_label.pack(side=tk.LEFT, padx=20, pady=10)
        
        # Controls
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        self.auto_scroll_var = tk.BooleanVar(value=self.auto_scroll)
        auto_scroll_check = ttk.Checkbutton(controls_frame,
                                          text="Auto-scroll",
                                          variable=self.auto_scroll_var,
                                          command=self._toggle_auto_scroll)
        auto_scroll_check.pack(side=tk.RIGHT, padx=(0, 10))
        
        clear_button = ttk.Button(controls_frame,
                                text="Clear",
                                command=self._clear_terminal)
        clear_button.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Terminal display
        terminal_frame = ttk.Frame(main_frame, style='Card.TFrame')
        terminal_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create text widget with custom styling
        self.text_widget = tk.Text(terminal_frame,
                                 bg=get_color(self.config, "background"),
                                 fg=get_color(self.config, "text"),
                                 insertbackground=get_color(self.config, "primary"),
                                 selectbackground=get_color(self.config, "primary"),
                                 selectforeground=get_color(self.config, "background"),
                                 font=get_font(self.config, "monospace", "normal"),
                                 wrap=tk.WORD,
                                 state=tk.DISABLED,
                                 cursor="arrow")
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(terminal_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Pack widgets
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure text tags for different log types
        self._configure_text_tags()
    
    def _configure_text_tags(self):
        """Configure text tags for different log types"""
        # Error logs - Red
        self.text_widget.tag_configure("error", 
                                      foreground=get_color(self.config, "error"))
        
        # Warning logs - Orange/Yellow
        self.text_widget.tag_configure("warning", 
                                      foreground=get_color(self.config, "warning"))
        
        # Info logs - White (default)
        self.text_widget.tag_configure("info", 
                                      foreground=get_color(self.config, "text"))
        
        # Connection logs - Green
        self.text_widget.tag_configure("connection", 
                                      foreground=get_color(self.config, "secondary"))
        
        # Data transfer logs - Blue
        self.text_widget.tag_configure("datatransfer", 
                                      foreground=get_color(self.config, "info"))
        
        # Security logs - Yellow
        self.text_widget.tag_configure("security", 
                                      foreground=get_color(self.config, "warning"))
        
        # System logs - Cyan
        self.text_widget.tag_configure("system", 
                                      foreground="#00ffff")
        
        # Timestamp style
        self.text_widget.tag_configure("timestamp", 
                                      foreground=get_color(self.config, "text_secondary"))
    
    def _add_welcome_message(self):
        """Add welcome message to terminal"""
        welcome_messages = [
            "🔴 MiraC2 Terminal Initialized",
            "🎨 Cyberpunk Theme Active: RED+BLACK+GREEN",
            "🔐 Encryption: AES-256-GCM Ready",
            "📡 Waiting for backend connection...",
            ""
        ]
        
        for message in welcome_messages:
            self.add_log_entry({
                "timestamp": datetime.now().isoformat(),
                "message": message,
                "log_type": "System"
            })
    
    def add_log_entry(self, log_data: Dict[str, Any]):
        """Add a log entry to the terminal"""
        timestamp = log_data.get("timestamp", datetime.now().isoformat())
        message = log_data.get("message", "")
        log_type = log_data.get("log_type", "info").lower()
        
        # Parse timestamp for display
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds
        except:
            time_str = timestamp
        
        # Add entry to list
        self.log_entries.append({
            "timestamp": timestamp,
            "time_str": time_str,
            "message": message,
            "log_type": log_type
        })
        
        # Trim entries if too many
        if len(self.log_entries) > self.max_entries:
            self.log_entries = self.log_entries[-self.max_entries:]
            self._refresh_display()
        else:
            self._append_entry_to_display(time_str, message, log_type)
    
    def _append_entry_to_display(self, time_str: str, message: str, log_type: str):
        """Append a single entry to the display"""
        self.text_widget.config(state=tk.NORMAL)
        
        # Add timestamp
        self.text_widget.insert(tk.END, f"[{time_str}] ", "timestamp")
        
        # Add log type indicator
        indicators = {
            "error": "❌ ",
            "warning": "⚠️  ",
            "info": "ℹ️  ",
            "connection": "🔗 ",
            "datatransfer": "📁 ",
            "security": "🔐 ",
            "system": "⚙️  "
        }
        
        indicator = indicators.get(log_type, "   ")
        self.text_widget.insert(tk.END, indicator)
        
        # Add message
        self.text_widget.insert(tk.END, f"{message}\n", log_type)
        
        self.text_widget.config(state=tk.DISABLED)
        
        # Auto-scroll if enabled
        if self.auto_scroll:
            self.text_widget.see(tk.END)
    
    def _refresh_display(self):
        """Refresh the entire display"""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        
        for entry in self.log_entries:
            self._append_entry_to_display(
                entry["time_str"],
                entry["message"],
                entry["log_type"]
            )
        
        self.text_widget.config(state=tk.DISABLED)
    
    def _toggle_auto_scroll(self):
        """Toggle auto-scroll setting"""
        self.auto_scroll = self.auto_scroll_var.get()
    
    def _clear_terminal(self):
        """Clear all terminal output"""
        self.log_entries.clear()
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.config(state=tk.DISABLED)
        
        # Add clear message
        self.add_log_entry({
            "timestamp": datetime.now().isoformat(),
            "message": "Terminal cleared",
            "log_type": "System"
        })