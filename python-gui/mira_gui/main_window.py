"""
Main window for MiraC2 GUI with cyberpunk styling
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import threading
import time
from typing import Dict, Any

from .backend_client import BackendClient
from .config import get_color, get_font
from .widgets.terminal import TerminalWidget
from .widgets.dashboard import DashboardWidget  
from .widgets.clients import ClientsWidget
from .widgets.passwords import PasswordsWidget
from .widgets.file_manager import FileManagerWidget
from .widgets.builder import BuilderWidget

class MiraMainWindow:
    """Main application window with cyberpunk theme"""
    
    def __init__(self, backend_client: BackendClient, config: Dict[str, Any]):
        self.backend_client = backend_client
        self.config = config
        self.root = None
        self.notebook = None
        self.widgets = {}
        self.update_thread = None
        self.running = False
        
    def run(self):
        """Run the main application"""
        self.root = tk.Tk()
        self.root.title("MiraC2 - Command & Control")
        
        # Set window properties
        window_config = self.config.get("window", {})
        width = window_config.get("width", 1400)
        height = window_config.get("height", 900)
        self.root.geometry(f"{width}x{height}")
        
        # Configure cyberpunk theme
        self._setup_theme()
        
        # Create the interface
        self._create_interface()
        
        # Connect to backend
        if self.backend_client.connect():
            self._setup_event_handlers()
            
        # Start update thread
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Start the GUI
        print("🚀 MiraC2 GUI Started")
        print("🎨 Theme: Cyberpunk (RED+BLACK+GREEN)")
        self.root.mainloop()
    
    def _setup_theme(self):
        """Setup the cyberpunk theme with RED+BLACK+GREEN colors"""
        style = ttk.Style()
        
        # Configure colors
        bg_color = get_color(self.config, "background")      # Black
        surface_color = get_color(self.config, "surface")    # Dark gray
        primary_color = get_color(self.config, "primary")    # Red
        secondary_color = get_color(self.config, "secondary") # Green
        text_color = get_color(self.config, "text")          # White
        
        # Configure root window
        self.root.configure(bg=bg_color)
        
        # Configure ttk styles
        style.theme_use('clam')
        
        # Notebook (tab container) style
        style.configure('TNotebook', 
                       background=bg_color,
                       borderwidth=0)
        style.configure('TNotebook.Tab',
                       background=surface_color,
                       foreground=text_color,
                       padding=[20, 10],
                       borderwidth=1,
                       relief='solid')
        style.map('TNotebook.Tab',
                 background=[('selected', primary_color),
                           ('active', surface_color)])
        
        # Frame styles
        style.configure('TFrame',
                       background=bg_color)
        style.configure('Card.TFrame',
                       background=surface_color,
                       relief='solid',
                       borderwidth=1)
        
        # Label styles
        style.configure('TLabel',
                       background=bg_color,
                       foreground=text_color)
        style.configure('Header.TLabel',
                       background=bg_color,
                       foreground=primary_color,
                       font=get_font(self.config, "primary", "header"))
        style.configure('Success.TLabel',
                       background=bg_color,
                       foreground=secondary_color)
        
        # Button styles
        style.configure('TButton',
                       background=surface_color,
                       foreground=text_color,
                       borderwidth=1,
                       relief='solid')
        style.map('TButton',
                 background=[('active', primary_color),
                           ('pressed', primary_color)])
        
        style.configure('Primary.TButton',
                       background=primary_color,
                       foreground=text_color)
        style.map('Primary.TButton',
                 background=[('active', '#ff2060'),
                           ('pressed', '#cc0030')])
        
        style.configure('Secondary.TButton',
                       background=secondary_color,
                       foreground=bg_color)
        style.map('Secondary.TButton',
                 background=[('active', '#20ff61'),
                           ('pressed', '#00cc31')])
    
    def _create_interface(self):
        """Create the main interface"""
        # Create main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create header
        self._create_header(main_frame)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create tabs
        self._create_tabs()
    
    def _create_header(self, parent):
        """Create the header section"""
        header_frame = ttk.Frame(parent, style='Card.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(header_frame, 
                              text="🔴 MiraC2 Command & Control", 
                              style='Header.TLabel')
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Status frame
        status_frame = ttk.Frame(header_frame)
        status_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Connection status
        self.status_label = ttk.Label(status_frame, 
                                    text="● Connected",
                                    style='Success.TLabel')
        self.status_label.pack(side=tk.RIGHT)
        
        # Server controls
        self.server_button = ttk.Button(status_frame,
                                      text="Start Server",
                                      style='Primary.TButton',
                                      command=self._toggle_server)
        self.server_button.pack(side=tk.RIGHT, padx=(0, 10))
    
    def _create_tabs(self):
        """Create all tabs in the notebook"""
        
        # Dashboard tab
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 Dashboard")
        self.widgets['dashboard'] = DashboardWidget(dashboard_frame, self.config, self.backend_client)
        
        # Clients tab
        clients_frame = ttk.Frame(self.notebook)
        self.notebook.add(clients_frame, text="🌐 Clients")
        self.widgets['clients'] = ClientsWidget(clients_frame, self.config, self.backend_client)
        
        # Passwords tab
        passwords_frame = ttk.Frame(self.notebook)
        self.notebook.add(passwords_frame, text="🔑 Passwords")
        self.widgets['passwords'] = PasswordsWidget(passwords_frame, self.config, self.backend_client)
        
        # File Manager tab
        files_frame = ttk.Frame(self.notebook)
        self.notebook.add(files_frame, text="📁 Files")
        self.widgets['file_manager'] = FileManagerWidget(files_frame, self.config, self.backend_client)
        
        # Builder tab
        builder_frame = ttk.Frame(self.notebook)
        self.notebook.add(builder_frame, text="🔧 Builder")
        self.widgets['builder'] = BuilderWidget(builder_frame, self.config, self.backend_client)
        
        # Terminal tab
        terminal_frame = ttk.Frame(self.notebook)
        self.notebook.add(terminal_frame, text="💻 Terminal")
        self.widgets['terminal'] = TerminalWidget(terminal_frame, self.config, self.backend_client)
    
    def _setup_event_handlers(self):
        """Setup event handlers for backend events"""
        self.backend_client.on("LogEntry", self._on_log_entry)
        self.backend_client.on("ClientConnected", self._on_client_connected)
        self.backend_client.on("ServerStarted", self._on_server_started)
        self.backend_client.on("ServerStopped", self._on_server_stopped)
    
    def _on_log_entry(self, log_data):
        """Handle log entry from backend"""
        if 'terminal' in self.widgets:
            self.widgets['terminal'].add_log_entry(log_data)
    
    def _on_client_connected(self, client_data):
        """Handle client connection"""
        if 'clients' in self.widgets:
            self.widgets['clients'].add_client(client_data)
        if 'dashboard' in self.widgets:
            self.widgets['dashboard'].update_stats()
    
    def _on_server_started(self, data):
        """Handle server started event"""
        self.root.after(0, lambda: self._update_server_status(True, data.get('port')))
    
    def _on_server_stopped(self, data):
        """Handle server stopped event"""
        self.root.after(0, lambda: self._update_server_status(False))
    
    def _update_server_status(self, running: bool, port: int = None):
        """Update server status in UI"""
        if running:
            self.status_label.config(text=f"● Server Running (Port {port})")
            self.server_button.config(text="Stop Server")
        else:
            self.status_label.config(text="○ Server Stopped")
            self.server_button.config(text="Start Server")
    
    def _toggle_server(self):
        """Toggle server start/stop"""
        current_text = self.server_button.cget('text')
        
        if current_text == "Start Server":
            # Get port from user or use default
            port = 8080  # In real implementation, show a dialog to get port
            if self.backend_client.start_server(port):
                self.server_button.config(text="Stop Server")
        else:
            if self.backend_client.stop_server():
                self.server_button.config(text="Start Server")
    
    def _update_loop(self):
        """Main update loop running in background thread"""
        while self.running:
            try:
                # Get events from backend
                events = self.backend_client.get_events()
                
                for event in events:
                    event_type = event.get('type')
                    data = event.get('data')
                    
                    # Schedule UI update on main thread
                    if event_type and data is not None:
                        self.root.after(0, lambda t=event_type, d=data: self.backend_client.emit_event(t, d))
                
                time.sleep(0.1)  # Check for events every 100ms
                
            except Exception as e:
                print(f"Error in update loop: {e}")
                time.sleep(1.0)
    
    def _on_closing(self):
        """Handle application closing"""
        self.running = False
        
        # Disconnect from backend
        self.backend_client.disconnect()
        
        # Wait for update thread to finish
        if self.update_thread and self.update_thread.is_alive():
            self.update_thread.join(timeout=1.0)
        
        # Destroy the window
        self.root.destroy()