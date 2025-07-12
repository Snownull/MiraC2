"""
Passwords widget for viewing extracted passwords
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

class PasswordsWidget:
    """Widget for displaying extracted passwords"""
    
    def __init__(self, parent, config: Dict[str, Any], backend_client):
        self.parent = parent
        self.config = config
        self.backend_client = backend_client
        
        self._create_interface()
    
    def _create_interface(self):
        """Create the passwords interface"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame, style='Card.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, 
                              text="🔑 Extracted Passwords",
                              style='Header.TLabel')
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Search and controls
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        search_label = ttk.Label(controls_frame, text="Search:")
        search_label.pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(controls_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind('<KeyRelease>', self._on_search)
        
        refresh_button = ttk.Button(controls_frame,
                                  text="Refresh",
                                  command=self._refresh_passwords)
        refresh_button.pack(side=tk.LEFT)
        
        # Passwords table
        table_frame = ttk.Frame(main_frame, style='Card.TFrame')
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for passwords
        columns = ('URL', 'Browser', 'Username', 'Password', 'Strength', 'Client IP')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.tree.heading('URL', text='Website URL')
        self.tree.heading('Browser', text='Browser')
        self.tree.heading('Username', text='Username')
        self.tree.heading('Password', text='Password')
        self.tree.heading('Strength', text='Strength')
        self.tree.heading('Client IP', text='Client IP')
        
        self.tree.column('URL', width=200)
        self.tree.column('Browser', width=80)
        self.tree.column('Username', width=150)
        self.tree.column('Password', width=150)
        self.tree.column('Strength', width=100)
        self.tree.column('Client IP', width=120)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add sample data
        self._add_sample_data()
    
    def _add_sample_data(self):
        """Add sample password data for demonstration"""
        sample_passwords = [
            {
                'url': 'https://facebook.com',
                'browser': 'Chrome',
                'username': 'john.doe@email.com',
                'password': 'password123',
                'strength': 'Weak',
                'client_ip': '192.168.1.100'
            },
            {
                'url': 'https://gmail.com',
                'browser': 'Firefox',
                'username': 'jane.smith@gmail.com', 
                'password': 'MyStr0ngP@ssw0rd!',
                'strength': 'Strong',
                'client_ip': '192.168.1.100'
            },
            {
                'url': 'https://github.com',
                'browser': 'Chrome',
                'username': 'developer',
                'password': 'dev123456',
                'strength': 'Medium',
                'client_ip': '10.0.0.50'
            }
        ]
        
        for password in sample_passwords:
            self.tree.insert('', tk.END, values=(
                password['url'],
                password['browser'],
                password['username'],
                password['password'],
                password['strength'],
                password['client_ip']
            ))
    
    def _on_search(self, event=None):
        """Handle search input"""
        search_term = self.search_var.get().lower()
        
        # Clear current selection
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Re-add filtered items
        try:
            passwords = self.backend_client.get_passwords()
            for password in passwords:
                # Check if search term matches any field
                if (search_term in password.get('url', '').lower() or
                    search_term in password.get('username', '').lower() or
                    search_term in password.get('client_ip', '').lower()):
                    
                    self.tree.insert('', tk.END, values=(
                        password.get('url', ''),
                        password.get('browser', ''),
                        password.get('username', ''),
                        password.get('password', ''),
                        password.get('strength', ''),
                        password.get('client_ip', '')
                    ))
        except:
            # Fallback to sample data with filtering
            sample_passwords = [
                {
                    'url': 'https://facebook.com',
                    'browser': 'Chrome',
                    'username': 'john.doe@email.com',
                    'password': 'password123',
                    'strength': 'Weak',
                    'client_ip': '192.168.1.100'
                },
                {
                    'url': 'https://gmail.com',
                    'browser': 'Firefox',
                    'username': 'jane.smith@gmail.com', 
                    'password': 'MyStr0ngP@ssw0rd!',
                    'strength': 'Strong',
                    'client_ip': '192.168.1.100'
                },
                {
                    'url': 'https://github.com',
                    'browser': 'Chrome',
                    'username': 'developer',
                    'password': 'dev123456',
                    'strength': 'Medium',
                    'client_ip': '10.0.0.50'
                }
            ]
            
            for password in sample_passwords:
                if (search_term in password['url'].lower() or
                    search_term in password['username'].lower() or
                    search_term in password['client_ip'].lower()):
                    
                    self.tree.insert('', tk.END, values=(
                        password['url'],
                        password['browser'],
                        password['username'],
                        password['password'],
                        password['strength'],
                        password['client_ip']
                    ))
    
    def _refresh_passwords(self):
        """Refresh the passwords list"""
        self.search_var.set("")
        self._on_search()