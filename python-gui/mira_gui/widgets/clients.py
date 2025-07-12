"""
Clients widget for managing connected clients
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, List

from ..config import get_color, get_font

class ClientsWidget:
    """Widget for displaying and managing connected clients"""
    
    def __init__(self, parent, config: Dict[str, Any], backend_client):
        self.parent = parent
        self.config = config
        self.backend_client = backend_client
        self.clients = []
        
        self._create_interface()
    
    def _create_interface(self):
        """Create the clients interface"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame, style='Card.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, 
                              text="🌐 Connected Clients",
                              style='Header.TLabel')
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Controls
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        refresh_button = ttk.Button(controls_frame,
                                  text="Refresh",
                                  command=self._refresh_clients)
        refresh_button.pack(side=tk.RIGHT)
        
        # Clients table
        table_frame = ttk.Frame(main_frame, style='Card.TFrame')
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for clients
        columns = ('IP', 'Country', 'OS', 'Wallets', 'First Seen', 'Last Seen')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.tree.heading('IP', text='IP Address')
        self.tree.heading('Country', text='Country')
        self.tree.heading('OS', text='Operating System')
        self.tree.heading('Wallets', text='Crypto Wallets')
        self.tree.heading('First Seen', text='First Seen')
        self.tree.heading('Last Seen', text='Last Seen')
        
        self.tree.column('IP', width=120)
        self.tree.column('Country', width=100)
        self.tree.column('OS', width=200)
        self.tree.column('Wallets', width=150)
        self.tree.column('First Seen', width=150)
        self.tree.column('Last Seen', width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add sample data
        self._add_sample_data()
    
    def _add_sample_data(self):
        """Add sample client data for demonstration"""
        sample_clients = [
            {
                'ip': '192.168.1.100',
                'country': 'USA',
                'os': 'Windows 10 Pro',
                'wallets': 'Exodus, MetaMask',
                'first_seen': '2024-01-15 10:30:00',
                'last_seen': '2024-01-15 14:25:00'
            },
            {
                'ip': '10.0.0.50',
                'country': 'Germany',
                'os': 'Windows 11 Home',
                'wallets': 'Atomic',
                'first_seen': '2024-01-15 09:15:00',
                'last_seen': '2024-01-15 14:20:00'
            }
        ]
        
        for client in sample_clients:
            self.tree.insert('', tk.END, values=(
                client['ip'],
                client['country'],
                client['os'],
                client['wallets'],
                client['first_seen'],
                client['last_seen']
            ))
    
    def add_client(self, client_data: Dict[str, Any]):
        """Add a new client to the list"""
        try:
            # Format wallet information
            wallets = []
            if client_data.get('wallet_exodus', False):
                wallets.append('Exodus')
            if client_data.get('wallet_atomic', False):
                wallets.append('Atomic')
            if client_data.get('wallet_metamask', False):
                wallets.append('MetaMask')
            
            wallet_str = ', '.join(wallets) if wallets else 'None'
            
            # Insert into tree
            self.tree.insert('', tk.END, values=(
                client_data.get('ip', ''),
                client_data.get('country', ''),
                client_data.get('os', ''),
                wallet_str,
                client_data.get('first_seen', ''),
                client_data.get('last_seen', '')
            ))
            
        except Exception as e:
            print(f"Error adding client: {e}")
    
    def _refresh_clients(self):
        """Refresh the clients list"""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get clients from backend
        try:
            clients = self.backend_client.get_clients()
            for client in clients:
                self.add_client(client)
        except Exception as e:
            print(f"Error refreshing clients: {e}")
            # Re-add sample data if backend fails
            self._add_sample_data()