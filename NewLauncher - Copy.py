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
        try:
            args = [account.gwpath]
            if account.email and account.password:
                args.extend(['-email', account.email, '-password', account.password])
            if account.character:
                args.extend(['-character', account.character])
            if account.extraargs:
                args.extend(account.extraargs.split())
                
            # Add unique identifier for multi-client
            args.extend([f'-clientport:{account.guid}'])
            
            env = os.environ.copy()
            env['GUILD_WARS_INSTANCE_ID'] = account.guid
            
            self.debug_window.log(f"Launching {account.name} with args: {args}")
            
            if account.elevated:
                # Launch with admin rights
                subprocess.run(['runas', '/user:Administrator'] + args)
            else:
                subprocess.Popen(args, env=env)
                
            account.active = True
            account.state = "Active"
            self.refresh_list()
            
        except Exception as e:
            self.debug_window.log(f"Error launching {account.name}: {str(e)}", logging.ERROR)
            messagebox.showerror("Launch Error", f"Failed to launch {account.name}: {str(e)}")

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

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    launcher = GWLauncher()
    launcher.run() 