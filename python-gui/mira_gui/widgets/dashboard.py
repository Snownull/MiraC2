"""
Dashboard widget showing system statistics and overview
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

from ..config import get_color, get_font

class DashboardWidget:
    """Dashboard showing system overview and statistics"""
    
    def __init__(self, parent, config: Dict[str, Any], backend_client):
        self.parent = parent
        self.config = config
        self.backend_client = backend_client
        self.stats_labels = {}
        
        self._create_interface()
        self._update_stats_periodically()
    
    def _create_interface(self):
        """Create the dashboard interface"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame, style='Card.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, 
                              text="📊 System Dashboard",
                              style='Header.TLabel')
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Status indicator
        self.status_frame = ttk.Frame(header_frame)
        self.status_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        self.status_label = ttk.Label(self.status_frame,
                                    text="🔴 System Online",
                                    style='Success.TLabel')
        self.status_label.pack()
        
        # Create grid of stats cards
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        self._create_stats_grid(stats_frame)
    
    def _create_stats_grid(self, parent):
        """Create grid of statistics cards"""
        # Configure grid weights
        for i in range(3):
            parent.grid_columnconfigure(i, weight=1)
        for i in range(3):
            parent.grid_rowconfigure(i, weight=1)
        
        # Client Statistics
        self._create_stat_card(parent, 0, 0, "👥 Total Clients", "total_clients", "0")
        self._create_stat_card(parent, 0, 1, "🟢 Active (24h)", "active_24h", "0")
        self._create_stat_card(parent, 0, 2, "📅 Active (7d)", "active_7d", "0")
        
        # Data Statistics  
        self._create_stat_card(parent, 1, 0, "🔑 Passwords", "passwords", "0")
        self._create_stat_card(parent, 1, 1, "📁 Files", "files", "0")
        self._create_stat_card(parent, 1, 2, "💾 Storage", "storage", "0 MB")
        
        # Top Countries (placeholder for now)
        self._create_country_card(parent, 2, 0)
        self._create_activity_card(parent, 2, 1)
        self._create_system_info_card(parent, 2, 2)
    
    def _create_stat_card(self, parent, row: int, col: int, title: str, key: str, initial_value: str):
        """Create a statistics card"""
        card_frame = ttk.Frame(parent, style='Card.TFrame')
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        # Title
        title_label = ttk.Label(card_frame, text=title, style='Header.TLabel')
        title_label.pack(pady=(15, 5))
        
        # Value
        value_label = ttk.Label(card_frame, 
                              text=initial_value,
                              font=get_font(self.config, "primary", "large"))
        value_label.pack(pady=(0, 15))
        
        # Store reference for updates
        self.stats_labels[key] = value_label
    
    def _create_country_card(self, parent, row: int, col: int):
        """Create top countries card"""
        card_frame = ttk.Frame(parent, style='Card.TFrame')
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        title_label = ttk.Label(card_frame, text="🌍 Top Countries", style='Header.TLabel')
        title_label.pack(pady=(15, 10))
        
        # Country list frame
        countries_frame = ttk.Frame(card_frame)
        countries_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Sample countries (will be updated with real data)
        countries = [
            ("🇺🇸 USA", "0"),
            ("🇩🇪 Germany", "0"),
            ("🇫🇷 France", "0"),
            ("🇬🇧 UK", "0"),
            ("🇨🇳 China", "0")
        ]
        
        self.country_labels = {}
        for i, (country, count) in enumerate(countries):
            country_frame = ttk.Frame(countries_frame)
            country_frame.pack(fill=tk.X, pady=2)
            
            name_label = ttk.Label(country_frame, text=country)
            name_label.pack(side=tk.LEFT)
            
            count_label = ttk.Label(country_frame, text=count)
            count_label.pack(side=tk.RIGHT)
            
            self.country_labels[country] = count_label
    
    def _create_activity_card(self, parent, row: int, col: int):
        """Create recent activity card"""
        card_frame = ttk.Frame(parent, style='Card.TFrame')
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        title_label = ttk.Label(card_frame, text="📈 Recent Activity", style='Header.TLabel')
        title_label.pack(pady=(15, 10))
        
        # Activity list frame
        activity_frame = ttk.Frame(card_frame)
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Sample activities
        activities = [
            "🔗 Client connected: 192.168.1.100",
            "📁 File received: data.zip",
            "🔑 Passwords extracted: 15",
            "🔧 Build completed: client.exe",
            "⚙️  System started"
        ]
        
        for activity in activities:
            activity_label = ttk.Label(activity_frame, 
                                     text=activity,
                                     wraplength=200)
            activity_label.pack(anchor='w', pady=2)
    
    def _create_system_info_card(self, parent, row: int, col: int):
        """Create system information card"""
        card_frame = ttk.Frame(parent, style='Card.TFrame')
        card_frame.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        title_label = ttk.Label(card_frame, text="🖥️ System Info", style='Header.TLabel')
        title_label.pack(pady=(15, 10))
        
        # System info frame
        info_frame = ttk.Frame(card_frame)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # System information
        import platform
        info_items = [
            ("Platform:", platform.system()),
            ("Python:", platform.python_version()),
            ("Architecture:", platform.machine()),
            ("Theme:", "Cyberpunk"),
            ("Encryption:", "AES-256-GCM")
        ]
        
        for label, value in info_items:
            info_item_frame = ttk.Frame(info_frame)
            info_item_frame.pack(fill=tk.X, pady=2)
            
            label_widget = ttk.Label(info_item_frame, text=label)
            label_widget.pack(side=tk.LEFT)
            
            value_widget = ttk.Label(info_item_frame, text=value)
            value_widget.pack(side=tk.RIGHT)
    
    def update_stats(self):
        """Update statistics from backend"""
        try:
            stats = self.backend_client.get_stats()
            
            # Update stat labels
            if 'total_clients' in self.stats_labels:
                self.stats_labels['total_clients'].config(text=str(stats.total_clients))
            if 'active_24h' in self.stats_labels:
                self.stats_labels['active_24h'].config(text=str(stats.active_clients_24h))
            if 'active_7d' in self.stats_labels:
                self.stats_labels['active_7d'].config(text=str(stats.active_clients_7d))
            if 'passwords' in self.stats_labels:
                self.stats_labels['passwords'].config(text=str(stats.total_passwords))
            if 'files' in self.stats_labels:
                self.stats_labels['files'].config(text=str(stats.total_files))
            
            # Update country stats
            for country, count in stats.country_stats.items():
                if country in self.country_labels:
                    self.country_labels[country].config(text=str(count))
                    
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    def _update_stats_periodically(self):
        """Update stats periodically"""
        self.update_stats()
        # Schedule next update in 5 seconds
        self.parent.after(5000, self._update_stats_periodically)