import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import os
import json
import subprocess
import uuid
import logging
from datetime import datetime
from typing import Optional, List
from pathlib import Path
import random
import sys
import win32event
import win32api
import win32con
import win32process
import win32security

class Account:
    def __init__(self):
        self.character: str = ""
        self.email: str = ""
        self.gwpath: str = ""
        self.password: str = ""
        self.extraargs: str = ""
        self.elevated: bool = False
        self.title: str = ""
        self.active: bool = False
        self.state: str = "Inactive"
        self.guid: str = str(uuid.uuid4())

    @property
    def name(self) -> str:
        if self.title:
            return self.title
        if self.character:
            return self.character
        return self.email if self.email else self.character

class AddAccountWindow:
    def __init__(self, parent, account: Optional[Account] = None):
        self.window = tk.Toplevel(parent)
        self.window.title("Add Account")
        self.window.geometry("400x500")
        self.account = account if account else Account()
        
        # Title
        tk.Label(self.window, text="Title:").pack(pady=5)
        self.title_entry = tk.Entry(self.window)
        self.title_entry.pack(fill=tk.X, padx=5)
        if self.account.title:
            self.title_entry.insert(0, self.account.title)

        # Email
        tk.Label(self.window, text="Email:").pack(pady=5)
        self.email_entry = tk.Entry(self.window)
        self.email_entry.pack(fill=tk.X, padx=5)
        if self.account.email:
            self.email_entry.insert(0, self.account.email)

        # Password
        tk.Label(self.window, text="Password:").pack(pady=5)
        self.password_frame = tk.Frame(self.window)
        self.password_frame.pack(fill=tk.X, padx=5)
        
        self.password_entry = tk.Entry(self.password_frame, show="*")
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        if self.account.password:
            self.password_entry.insert(0, self.account.password)
            
        self.show_password_btn = tk.Button(self.password_frame, text="👁", command=self.toggle_password)
        self.show_password_btn.pack(side=tk.RIGHT)

        # Character
        tk.Label(self.window, text="Character:").pack(pady=5)
        self.character_entry = tk.Entry(self.window)
        self.character_entry.pack(fill=tk.X, padx=5)
        if self.account.character:
            self.character_entry.insert(0, self.account.character)

        # GW Path
        tk.Label(self.window, text="Guild Wars Path:").pack(pady=5)
        self.path_frame = tk.Frame(self.window)
        self.path_frame.pack(fill=tk.X, padx=5)
        
        self.path_entry = tk.Entry(self.path_frame)
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        if self.account.gwpath:
            self.path_entry.insert(0, self.account.gwpath)
            
        self.browse_btn = tk.Button(self.path_frame, text="Browse", command=self.browse_gw)
        self.browse_btn.pack(side=tk.RIGHT)

        # Extra Arguments
        tk.Label(self.window, text="Extra Arguments:").pack(pady=5)
        self.args_entry = tk.Entry(self.window)
        self.args_entry.pack(fill=tk.X, padx=5)
        if self.account.extraargs:
            self.args_entry.insert(0, self.account.extraargs)

        # Elevated checkbox
        self.elevated_var = tk.BooleanVar(value=self.account.elevated)
        self.elevated_check = tk.Checkbutton(self.window, text="Run as Administrator", 
                                           variable=self.elevated_var)
        self.elevated_check.pack(pady=5)

        # Save button
        self.save_btn = tk.Button(self.window, text="Save", command=self.save_account)
        self.save_btn.pack(pady=10)

    def toggle_password(self):
        current = self.password_entry['show']
        self.password_entry['show'] = '' if current else '*'

    def browse_gw(self):
        path = filedialog.askopenfilename(
            title="Select Guild Wars Executable",
            filetypes=[("Guild Wars", "Gw.exe"), ("All files", "*.*")]
        )
        if path:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, path)

    def save_account(self):
        self.account.title = self.title_entry.get()
        self.account.email = self.email_entry.get()
        self.account.password = self.password_entry.get()
        self.account.character = self.character_entry.get()
        self.account.gwpath = self.path_entry.get()
        self.account.extraargs = self.args_entry.get()
        self.account.elevated = self.elevated_var.get()
        self.window.destroy()

class DebugWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Debug Console")
        self.window.geometry("600x400")
        
        # Create text widget
        self.text_widget = scrolledtext.ScrolledText(self.window, wrap=tk.WORD)
        self.text_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initially hide the window
        self.window.withdraw()
        
    def log(self, message: str, level: int = logging.INFO):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level_str = logging.getLevelName(level)
        formatted_message = f"[{timestamp}] [{level_str}] {message}\n"
        
        self.text_widget.insert(tk.END, formatted_message)
        self.text_widget.see(tk.END)  # Auto-scroll to bottom

class GWLauncher:
    GW_MUTEX_NAME = "Global\\{0B63E23D-9E1E-452C-B15F-2E76526BC5CF}"
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Guild Wars Multi-Launcher")
        self.window.geometry("800x600")
        
        # Accounts list
        self.accounts: List[Account] = []
        
        # Create main list view
        self.create_list_view()
        
        # Create buttons
        self.create_buttons()
        
        # Create debug window
        self.debug_window = DebugWindow(self.window)
        
        # Load saved accounts
        self.load_accounts()
        
        # Add new DLL path property
        self.dll_path = ""
        
        # Load saved DLL path
        self.load_dll_path()

    def create_list_view(self):
        columns = ("Name", "Status", "Character", "Email")
        self.tree = ttk.Treeview(self.window, columns=columns, show='headings')
        
        # Define headings
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
            
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_buttons(self):
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add new Select DLL button
        tk.Button(btn_frame, text="Select DLL", command=self.select_dll).pack(side=tk.LEFT, padx=2)
        
        tk.Button(btn_frame, text="Add Account", command=self.add_account).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Edit Account", command=self.edit_account).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Remove Account", command=self.remove_account).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Launch Selected", command=self.launch_selected).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Launch All", command=self.launch_all).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="Debug Console", command=self.show_debug).pack(side=tk.RIGHT, padx=2)

    def add_account(self):
        dialog = AddAccountWindow(self.window)
        self.window.wait_window(dialog.window)
        if dialog.account.gwpath:  # Only add if a path was selected
            self.accounts.append(dialog.account)
            self.refresh_list()
            self.save_accounts()

    def edit_account(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        index = self.tree.index(selected[0])
        dialog = AddAccountWindow(self.window, self.accounts[index])
        self.window.wait_window(dialog.window)
        self.refresh_list()
        self.save_accounts()

    def remove_account(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        index = self.tree.index(selected[0])
        self.accounts.pop(index)
        self.refresh_list()
        self.save_accounts()

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for account in self.accounts:
            self.tree.insert('', tk.END, values=(
                account.name,
                account.state,
                account.character,
                account.email
            ))

    def launch_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        for item in selected:
            index = self.tree.index(item)
            self.launch_account(self.accounts[index])

    def launch_all(self):
        for account in self.accounts:
            self.launch_account(account)

    def launch_account(self, account: Account):
        # Create unique process environment
        env = os.environ.copy()
        env['GUILD_WARS_INSTANCE'] = str(account.guid)
        
        # Build command with all necessary arguments
        cmd = [
            f'"{account.gwpath}"',  # Wrap path in quotes to handle spaces
            f'-email "{account.email}"',
            f'-password "{account.password}"',
            f'-character "{account.character}"'
        ]
        
        if account.extraargs:
            cmd.extend(account.extraargs.split())
        
        command_line = ' '.join(cmd)
        self.debug_window.log(f"Launching with command: {command_line}")
        
        try:
            # Create process with specific security attributes to handle mutex
            sa = win32security.SECURITY_ATTRIBUTES()
            sa.bInheritHandle = True
            
            self.debug_window.log("Creating process with suspended state...")
            
            # Create process with suspended state
            startupinfo = win32process.STARTUPINFO()
            flags = win32con.CREATE_SUSPENDED
            if account.elevated:
                flags |= win32con.CREATE_NEW_PROCESS_GROUP
                self.debug_window.log("Process will run with elevated privileges")
            
            proc_handle, thread_handle, pid, tid = win32process.CreateProcess(
                account.gwpath,  # Application name
                command_line,    # Command line args as single string
                sa,  # Process security attributes
                sa,  # Thread security attributes
                True,  # Inherit handles
                flags,  # Creation flags
                env,  # Environment
                os.path.dirname(account.gwpath),  # Working directory
                startupinfo  # Startup info
            )
            
            self.debug_window.log(f"Process created with PID: {pid}")
            
            # Resume the process
            win32process.ResumeThread(thread_handle)
            self.debug_window.log("Process resumed from suspended state")
            
            # Add DLL injection here
            if self.dll_path:
                self.debug_window.log("Waiting 5 seconds before DLL injection...")
                win32api.Sleep(5000)  # Changed from 1000 to 5000 ms (5 seconds)
                if self.inject_dll(pid):
                    self.debug_window.log("DLL injection completed successfully")
                else:
                    self.debug_window.log("DLL injection failed", logging.WARNING)
            
            # Close handles
            win32api.CloseHandle(proc_handle)
            win32api.CloseHandle(thread_handle)
            self.debug_window.log("Process handles closed")
            
            account.active = True
            account.state = "Active"
            self.debug_window.log(f"Account {account.name} launched successfully")
            return True
            
        except Exception as e:
            self.debug_window.log(f"Failed to launch account {account.name}: {str(e)}", logging.ERROR)
            account.state = f"Error: {str(e)}"
            return False

    def save_accounts(self):
        data = []
        for account in self.accounts:
            data.append({
                'title': account.title,
                'email': account.email,
                'password': account.password,  # Consider encryption
                'character': account.character,
                'gwpath': account.gwpath,
                'extraargs': account.extraargs,
                'elevated': account.elevated
            })
            
        with open('accounts.json', 'w') as f:
            json.dump(data, f, indent=4)
            
        self.debug_window.log(f"Saved {len(data)} accounts")

    def load_accounts(self):
        try:
            with open('accounts.json', 'r') as f:
                data = json.load(f)
                
            self.accounts = []
            for item in data:
                account = Account()
                account.title = item.get('title', '')
                account.email = item.get('email', '')
                account.password = item.get('password', '')
                account.character = item.get('character', '')
                account.gwpath = item.get('gwpath', '')
                account.extraargs = item.get('extraargs', '')
                account.elevated = item.get('elevated', False)
                self.accounts.append(account)
                
            self.refresh_list()
            self.debug_window.log(f"Loaded {len(self.accounts)} accounts")
            
        except FileNotFoundError:
            self.debug_window.log("No saved accounts found")
            pass

    def show_debug(self):
        self.debug_window.window.deiconify()

    def select_dll(self):
        path = filedialog.askopenfilename(
            title="Select DLL File",
            filetypes=[("DLL files", "*.dll"), ("All files", "*.*")]
        )
        if path:
            self.dll_path = path
            self.save_dll_path()
            self.debug_window.log(f"Selected DLL: {path}")

    def save_dll_path(self):
        config = {}
        try:
            # Load existing config if it exists
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    config = json.load(f)
        except Exception as e:
            self.debug_window.log(f"Error loading config: {str(e)}", logging.ERROR)

        # Update DLL path
        config['dll_path'] = self.dll_path

        # Save config
        try:
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            self.debug_window.log(f"Error saving config: {str(e)}", logging.ERROR)

    def load_dll_path(self):
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    config = json.load(f)
                    self.dll_path = config.get('dll_path', '')
                    if self.dll_path:
                        self.debug_window.log(f"Loaded DLL path: {self.dll_path}")
        except Exception as e:
            self.debug_window.log(f"Error loading DLL path: {str(e)}", logging.ERROR)

    def inject_dll(self, pid: int) -> bool:
        if not self.dll_path:
            self.debug_window.log("No DLL selected. Please select a DLL file first.", logging.ERROR)
            return False
            
        if not os.path.exists(self.dll_path):
            self.debug_window.log("Selected DLL file does not exist.", logging.ERROR)
            return False

        try:
            # Use selected DLL path instead of hardcoded path
            dll_path = self.dll_path
            
            # Get process handle
            process = win32api.OpenProcess(
                win32con.PROCESS_ALL_ACCESS,
                False,
                pid
            )
            
            # Allocate memory for DLL path
            dll_path_address = win32process.VirtualAllocEx(
                process,
                0,
                len(dll_path) + 1,
                win32con.MEM_COMMIT,
                win32con.PAGE_READWRITE
            )
            
            # Write DLL path to process memory
            win32process.WriteProcessMemory(
                process,
                dll_path_address,
                dll_path.encode()
            )
            
            # Get LoadLibraryA address
            kernel32 = win32api.GetModuleHandle('kernel32.dll')
            load_library = win32api.GetProcAddress(kernel32, 'LoadLibraryA')
            
            # Create remote thread to load DLL
            thread_h = win32process.CreateRemoteThread(
                process,
                None,
                0,
                load_library,
                dll_path_address,
                0
            )
            
            # Wait for thread to complete
            win32event.WaitForSingleObject(thread_h, 5000)
            
            # Clean up
            win32api.CloseHandle(thread_h)
            win32api.CloseHandle(process)
            
            self.debug_window.log(f"Successfully injected DLL into process {pid}")
            return True
            
        except Exception as e:
            self.debug_window.log(f"Failed to inject DLL: {str(e)}", logging.ERROR)
            return False

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    launcher = GWLauncher()
    launcher.run() 