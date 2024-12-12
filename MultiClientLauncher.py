#!/usr/bin/env python3

"""
    Guild Wars 1 multiaccount launcher and multiboxer.
    Requires administrator mode.
    Multiboxing works by closing the "AN-Mutex-Window-Guild Wars" handle of
        each game instance and making Local.dat a symbolic link to the .dat
        file connected to the intended account.
    Script stores all variables using JSON format in a file named data.json
        which is located in the same directory as the script.

    Global Variables:
    - handle: path to handle.exe file
        https://technet.microsoft.com/en-us/sysinternals/handle.aspx
    - localPath: the path to the directory where the Local.dat file is located
        default: "%AppData%\Guild Wars"
    - exePath: path to the Guild Wars executable file
        default: "%ProgramFiles%\Guild Wars\Gw.exe"
    - params: Guild Wars launch parameters for single instance
    - multiparams: Guild Wars launch parameters for multibox launch
    - datLocal: Path to Local.dat file. Set automatically using localPath
"""

import os
import re
import subprocess
import shutil
import time
import json
from glob import glob
from sys import exit
import msvcrt
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# This file's location
__location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))


class GuildWarsLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Guild Wars Launcher")
        self.root.geometry("600x400")
        
        # Load saved data
        self.load_data()
        
        # Create main notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Create tabs
        self.create_launcher_tab()
        self.create_settings_tab()
        
        # Style
        self.style = ttk.Style()
        self.style.configure('Launch.TButton', padding=10, font=('Arial', 10, 'bold'))
        
    def load_data(self):
        """Load settings from data.json"""
        self.data = {
            "handle": "",
            "localPath": os.path.join(os.getenv("APPDATA"), "Guild Wars"),
            "exePath": os.path.join(os.getenv("PROGRAMFILES"), "Guild Wars", "Gw.exe"),
            "params": [],
            "multiparams": []
        }
        
        try:
            with open("data.json") as f:
                self.data.update(json.load(f))
        except FileNotFoundError:
            self.save_data()
            
    def save_data(self):
        """Save settings to data.json"""
        with open("data.json", "w") as f:
            json.dump(self.data, f, indent=4)
            
    def create_launcher_tab(self):
        """Create the main launcher tab"""
        launch_frame = ttk.Frame(self.notebook)
        self.notebook.add(launch_frame, text="Launcher")
        
        # Account list
        accounts_frame = ttk.LabelFrame(launch_frame, text="Accounts", padding=10)
        accounts_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Account listbox with scrollbar
        self.account_listbox = tk.Listbox(accounts_frame, selectmode=tk.MULTIPLE)
        scrollbar = ttk.Scrollbar(accounts_frame, orient="vertical", command=self.account_listbox.yview)
        self.account_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.account_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Account management buttons
        account_buttons_frame = ttk.Frame(launch_frame)
        account_buttons_frame.pack(fill='x', padx=5)
        
        ttk.Button(account_buttons_frame, text="Add Account", 
                  command=self.add_account).pack(side='left', padx=5)
        ttk.Button(account_buttons_frame, text="Remove Selected",
                  command=self.remove_account).pack(side='left', padx=5)
        
        # Launch buttons frame
        button_frame = ttk.Frame(launch_frame)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(button_frame, text="Launch Single", style='Launch.TButton',
                  command=self.launch_single).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Launch Multiple", style='Launch.TButton',
                  command=self.launch_multiple).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Refresh Accounts", style='Launch.TButton',
                  command=self.refresh_accounts).pack(side='left', padx=5)
        
        self.refresh_accounts()
        
    def create_settings_tab(self):
        """Create the settings tab"""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="Settings")
        
        # Settings fields
        ttk.Label(settings_frame, text="Handle.exe Path:").pack(anchor='w', padx=5, pady=2)
        handle_frame = ttk.Frame(settings_frame)
        handle_frame.pack(fill='x', padx=5)
        self.handle_var = tk.StringVar(value=self.data["handle"])
        ttk.Entry(handle_frame, textvariable=self.handle_var).pack(side='left', fill='x', expand=True)
        ttk.Button(handle_frame, text="Browse", command=lambda: self.browse_file("handle")).pack(side='right')
        
        ttk.Label(settings_frame, text="Local.dat Folder:").pack(anchor='w', padx=5, pady=2)
        local_frame = ttk.Frame(settings_frame)
        local_frame.pack(fill='x', padx=5)
        self.local_var = tk.StringVar(value=self.data["localPath"])
        ttk.Entry(local_frame, textvariable=self.local_var).pack(side='left', fill='x', expand=True)
        ttk.Button(local_frame, text="Browse", command=lambda: self.browse_directory("local")).pack(side='right')
        
        ttk.Label(settings_frame, text="GW.exe Path:").pack(anchor='w', padx=5, pady=2)
        exe_frame = ttk.Frame(settings_frame)
        exe_frame.pack(fill='x', padx=5)
        self.exe_var = tk.StringVar(value=self.data["exePath"])
        ttk.Entry(exe_frame, textvariable=self.exe_var).pack(side='left', fill='x', expand=True)
        ttk.Button(exe_frame, text="Browse", command=lambda: self.browse_file("exe")).pack(side='right')
        
        ttk.Label(settings_frame, text="Launch Parameters:").pack(anchor='w', padx=5, pady=2)
        self.params_var = tk.StringVar(value=' '.join(self.data["params"]))
        ttk.Entry(settings_frame, textvariable=self.params_var).pack(fill='x', padx=5)
        
        ttk.Label(settings_frame, text="Multibox Parameters:").pack(anchor='w', padx=5, pady=2)
        self.multiparams_var = tk.StringVar(value=' '.join(self.data["multiparams"]))
        ttk.Entry(settings_frame, textvariable=self.multiparams_var).pack(fill='x', padx=5)
        
        ttk.Button(settings_frame, text="Save Settings", command=self.save_settings).pack(pady=10)
        
    def browse_file(self, setting_type):
        """Browse for a file"""
        filetypes = [("Executable files", "*.exe")] if setting_type in ["handle", "exe"] else [("All files", "*.*")]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            if setting_type == "handle":
                self.handle_var.set(filename)
            elif setting_type == "exe":
                self.exe_var.set(filename)
                
    def browse_directory(self, setting_type):
        """Browse for a directory"""
        directory = filedialog.askdirectory()
        if directory:
            if setting_type == "local":
                self.local_var.set(directory)
                
    def save_settings(self):
        """Save current settings"""
        self.data.update({
            "handle": self.handle_var.get(),
            "localPath": self.local_var.get(),
            "exePath": self.exe_var.get(),
            "params": self.params_var.get().split(),
            "multiparams": self.multiparams_var.get().split()
        })
        self.save_data()
        messagebox.showinfo("Success", "Settings saved successfully!")
        
    def refresh_accounts(self):
        """Refresh the account list"""
        self.account_listbox.delete(0, tk.END)
        users = glob(os.path.join(self.data["localPath"], "*.dat"))
        try:
            users.remove(os.path.join(self.data["localPath"], "Local.dat"))
        except ValueError:
            pass
        
        for user in users:
            self.account_listbox.insert(tk.END, os.path.basename(user)[:-4])
            
    def launch_single(self):
        """Launch a single instance"""
        selection = self.account_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an account to launch")
            return
            
        account = self.account_listbox.get(selection[0])
        dat_file = os.path.join(self.data["localPath"], f"{account}.dat")
        self.link_dat(dat_file)
        self.start_single()
        
    def launch_multiple(self):
        """Launch multiple instances"""
        selection = self.account_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select accounts to launch")
            return
            
        for idx in selection:
            account = self.account_listbox.get(idx)
            dat_file = os.path.join(self.data["localPath"], f"{account}.dat")
            self.link_dat(dat_file)
            self.start_multi(dat_file)
            
    def link_dat(self, dat_file):
        """Create symbolic link for Local.dat"""
        local_dat = os.path.join(self.data["localPath"], "Local.dat")
        try:
            os.remove(local_dat)
        except FileNotFoundError:
            pass
        os.symlink(dat_file, local_dat)
        
    def start_single(self, multi=False):
        """Start a single instance"""
        params = self.data["multiparams"] if multi else self.data["params"]
        subprocess.Popen([self.data["exePath"]] + params)
        
    def start_multi(self, dat_file):
        """Start a multibox instance"""
        self.start_single(True)
        time.sleep(5)
        self.shut_mutex()
        
    def shut_mutex(self):
        """Close the mutex handle"""
        command = [self.data["handle"], "-a", "AN-Mutex-Window-Guild Wars"]
        handle_response = str(subprocess.check_output(" ".join(command)))
        
        pid = re.compile("pid: \d+").search(handle_response).span()
        pid = handle_response[pid[0] + 5:pid[1] + 1]
        
        val = re.compile("\w+: \\\\").search(handle_response).span()
        val = handle_response[val[0]:val[1] - 3]
        
        command = [self.data["handle"], "-c", val, "-p", pid, "-y"]
        subprocess.call(" ".join(command))
        
    def add_account(self):
        """Add a new account"""
        dat_file = filedialog.askopenfilename(
            title="Select Account DAT file",
            filetypes=[("DAT files", "*.dat")],
            initialdir=self.data["localPath"]
        )
        if dat_file:
            # Copy the DAT file to the Guild Wars directory
            filename = os.path.basename(dat_file)
            destination = os.path.join(self.data["localPath"], filename)
            
            try:
                shutil.copy2(dat_file, destination)
                self.refresh_accounts()
                messagebox.showinfo("Success", f"Account {filename[:-4]} added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add account: {str(e)}")

    def remove_account(self):
        """Remove selected account(s)"""
        selection = self.account_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select account(s) to remove")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to remove the selected account(s)?"):
            for idx in reversed(selection):
                account = self.account_listbox.get(idx)
                dat_file = os.path.join(self.data["localPath"], f"{account}.dat")
                try:
                    os.remove(dat_file)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to remove {account}: {str(e)}")
            
            self.refresh_accounts()

def main():
    root = tk.Tk()
    app = GuildWarsLauncher(root)
    root.mainloop()

if __name__ == "__main__":
    main()