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
import psutil
import winreg
import time
import ctypes

MUTEX_ALL_ACCESS = 0x1F001

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
        
        # Add this line:
        self.dll_path = None  # Initialize dll_path attribute
        
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
        self.debug_window.log(f"=== Starting launch for account: {account.name} ===")
        
        # Generate unique identifiers for this instance
        instance_id = account.guid
        window_name = f"Guild Wars_{instance_id}"
        instance_mutex = f"Global\\GW_Instance_{instance_id}"
        
        # Define instance-specific mutex names
        mutex_names = [
            f"AN-Mutex-Window-{instance_id}",
            f"AN-Mutex-Input-{instance_id}", 
            f"AN-Mutex-Render-{instance_id}",
            instance_mutex
        ]
        
        # Force close any existing mutexes
        self.debug_window.log("Attempting to clear mutexes...")
        for mutex_name in mutex_names:
            try:
                mutex = win32event.OpenMutex(
                    win32con.SYNCHRONIZE | MUTEX_ALL_ACCESS,
                    0,
                    mutex_name
                )
                if mutex:
                    win32api.CloseHandle(mutex)
                    self.debug_window.log(f"Successfully cleared mutex: {mutex_name}")
                else:
                    self.debug_window.log(f"Mutex not found: {mutex_name}")
            except Exception as e:
                self.debug_window.log(f"Error clearing mutex {mutex_name}: {str(e)}", logging.WARNING)

        try:
            # Setup environment with instance-specific variables
            env = os.environ.copy()
            env['GUILD_WARS_INSTANCE'] = instance_id
            env['GW_MUTEX_WINDOW'] = mutex_names[0]
            env['GW_MUTEX_INPUT'] = mutex_names[1]
            env['GW_MUTEX_RENDER'] = mutex_names[2]
            env['PATH'] = os.path.dirname(account.gwpath) + os.pathsep + env.get('PATH', '')
            
            # Build command with instance-specific window name
            cmd = [account.gwpath]
            if account.email:
                cmd.extend(["-email", account.email])
            if account.password:
                cmd.extend(["-password", account.password])
            if account.character:
                cmd.extend(["-character", account.character])
            cmd.extend([
                "-windowname", window_name,
                "-mutex", instance_mutex  # Add instance-specific mutex
            ])
            
            if account.extraargs:
                cmd.extend(account.extraargs.split())

            # Create process with specific security attributes
            sa = win32security.SECURITY_ATTRIBUTES()
            sa.bInheritHandle = True
            
            startupinfo = win32process.STARTUPINFO()
            
            # Create process suspended with additional flags
            flags = (
                win32con.CREATE_SUSPENDED | 
                win32con.CREATE_NEW_CONSOLE | 
                win32con.NORMAL_PRIORITY_CLASS |
                win32con.CREATE_DEFAULT_ERROR_MODE
            )
            if account.elevated:
                flags |= win32con.CREATE_NEW_PROCESS_GROUP
            
            self.debug_window.log(f"Launching: {' '.join(cmd)}")
            
            # Launch process
            proc_handle, thread_handle, pid, tid = win32process.CreateProcess(
                None,
                ' '.join(f'"{x}"' if ' ' in x else x for x in cmd),
                sa,
                sa,
                True,
                flags,
                env,
                os.path.dirname(account.gwpath),
                startupinfo
            )
            
            self.debug_window.log(f"Process created successfully with PID: {pid}")
            
            # After creating the process and before checking status
            win32api.Sleep(5000)  # Increase initial wait to 5 seconds
            
            # Add multiple status checks with delays
            for i in range(3):
                exit_code = ctypes.c_ulong(0)
                if ctypes.windll.kernel32.GetExitCodeProcess(
                    proc_handle.handle,
                    ctypes.byref(exit_code)
                ):
                    if exit_code.value == win32con.STILL_ACTIVE:
                        self.debug_window.log(f"Process check {i+1}: Still active")
                        win32api.Sleep(1000)
                        continue
                    else:
                        self.debug_window.log(f"Process terminated with exit code: {exit_code.value}")
                        break
                else:
                    raise Exception("Failed to get process status")

            # Only proceed with thread resume if process is still active
            if exit_code.value == win32con.STILL_ACTIVE:
                self.debug_window.log("Process verified active, resuming thread...")
                win32process.ResumeThread(thread_handle)
            else:
                raise Exception(f"Process failed to start (exit code: {exit_code.value})")

            # Add additional verification after resume
            win32api.Sleep(2000)
            if not ctypes.windll.kernel32.GetExitCodeProcess(
                proc_handle.handle,
                ctypes.byref(exit_code)
            ) or exit_code.value != win32con.STILL_ACTIVE:
                raise Exception("Process terminated after resume")

            # Now try to inject DLL if path is set
            if self.dll_path:
                if self.inject_dll(pid):
                    self.debug_window.log("DLL injection successful")
                else:
                    self.debug_window.log("DLL injection failed", logging.WARNING)
            
            # Final verification with multiple checks
            for i in range(3):  # Check status multiple times
                exit_code = ctypes.c_ulong(0)
                if not ctypes.windll.kernel32.GetExitCodeProcess(
                    proc_handle.handle,
                    ctypes.byref(exit_code)
                ):
                    raise Exception("Failed to get final process status")
                
                if exit_code.value != win32con.STILL_ACTIVE:
                    raise Exception(f"Process terminated after DLL injection with exit code: {exit_code.value}")
                
                win32api.Sleep(1000)
            
            account.active = True
            account.state = "Active"
            self.refresh_list()
            self.debug_window.log(f"=== Launch completed successfully for {account.name} ===")
            return True
            
        except Exception as e:
            self.debug_window.log(f"!!! Launch failed with error: {str(e)} !!!", logging.ERROR)
            self.debug_window.log(f"Error type: {type(e).__name__}", logging.ERROR)
            import traceback
            self.debug_window.log(f"Stack trace:\n{traceback.format_exc()}", logging.ERROR)
            
            # Try to kill the process if it's still running
            try:
                if 'proc_handle' in locals():
                    win32api.TerminateProcess(proc_handle, 1)
            except:
                pass
            
            account.state = f"Error: {str(e)}"
            self.refresh_list()
            return False
        
        finally:
            # Clean up handles
            try:
                if 'proc_handle' in locals():
                    win32api.CloseHandle(proc_handle)
                if 'thread_handle' in locals():
                    win32api.CloseHandle(thread_handle)
            except:
                pass

        # Verify working directory exists
        working_dir = os.path.dirname(account.gwpath)
        if not os.path.exists(working_dir):
            raise Exception(f"Working directory does not exist: {working_dir}")
        
        # Verify GW.exe exists and is accessible
        if not os.path.exists(account.gwpath):
            raise Exception(f"GW.exe not found at: {account.gwpath}")

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

def clear_mutex():
    """
    Clear the Guild Wars mutex to allow multiple instances
    """
    try:
        import win32api
        import win32con
        
        # Try to open the GW mutex
        mutex_name = "AN-Mutex-Window-Guild Wars"
        mutex = win32api.OpenMutex(win32con.SYNCHRONIZE, False, mutex_name)
        
        if mutex:
            # Close handle if mutex exists
            win32api.CloseHandle(mutex)
            return True
            
    except Exception as e:
        print(f"Mutex clear error: {e}")
    return False

def manage_registry(gw_path):
    """
    Manage GW registry entries for multiple instances
    Based on GWMultiLaunch's RegistryManager implementation
    """
    try:
        # Backup original path
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                            r"SOFTWARE\ArenaNet\Guild Wars",
                            0, winreg.KEY_ALL_ACCESS)
        
        # Temporarily modify path for new instance
        winreg.SetValueEx(key, "Path", 0, winreg.REG_SZ, gw_path)
        
        return True
    except Exception as e:
        print(f"Registry error: {e}")
        return False

def launch_gw(self, account: Account) -> bool:
    """
    Launch GW instance with proper handle management
    Based directly on GWMultiLaunch's proven implementation
    """
    try:
        # Step 1: Kill all existing GW mutexes
        mutex_names = [
            "AN-Mutex-Window-Guild Wars",
            "AN-Mutex-Input-Guild Wars", 
            "AN-Mutex-Render-Guild Wars"
        ]
        
        for mutex_name in mutex_names:
            try:
                # Try to open with full access
                mutex = win32event.OpenMutex(
                    win32con.SYNCHRONIZE | win32con.MUTEX_ALL_ACCESS,
                    0,
                    mutex_name
                )
                if mutex:
                    # Close and release the handle
                    win32api.CloseHandle(mutex)
            except:
                continue

        # Step 2: Set up process creation with specific security settings
        sa = win32security.SECURITY_ATTRIBUTES()
        sa.bInheritHandle = 1
        
        # Step 3: Create process with modified token if elevated requested
        if account.elevated:
            # Get current process token
            ph = win32api.GetCurrentProcess()
            th = win32security.OpenProcessToken(ph, win32con.TOKEN_ALL_ACCESS)
            
            # Create elevated token
            elevation = win32security.TOKEN_ELEVATION()
            elevation.TokenIsElevated = True
            
            # Create process with elevated token
            token = win32security.DuplicateTokenEx(
                th,
                win32security.SecurityIdentification,
                win32security.TokenPrimary,
                elevation
            )
        else:
            token = None

        # Step 4: Build command line
        args = []
        if account.email:
            args.extend(["-email", account.email])
        if account.password:
            args.extend(["-password", account.password])
        if account.character:
            args.extend(["-character", account.character])
        if account.extraargs:
            args.extend(account.extraargs.split())

        # Add unique window name
        unique_id = str(time.time()).replace(".", "")
        window_name = f"Guild Wars_{unique_id}"
        args.extend(["-windowname", window_name])

        # Step 5: Create startup info
        si = win32process.STARTUPINFO()
        si.dwFlags = win32con.STARTF_USESHOWWINDOW
        si.wShowWindow = win32con.SW_SHOWNORMAL
        
        # Step 6: Launch process
        creation_flags = win32con.CREATE_DEFAULT_ERROR_MODE
        if account.elevated:
            creation_flags |= win32con.CREATE_NEW_CONSOLE

        cmd_line = f'"{account.gwpath}" {" ".join(args)}'
        
        process_info = win32process.CreateProcess(
            account.gwpath,
            cmd_line,
            sa,  # Process attributes
            sa,  # Thread attributes
            1,   # Inherit handles
            creation_flags,
            None,  # Environment
            None,  # Current directory
            si    # Startup info
        )

        # Step 7: Store process info and update state
        account.process = process_info[0]  # Process handle
        account.active = True
        account.state = "Running"

        # Step 8: Critical delay to allow proper mutex handling
        time.sleep(2)  # Increased delay for reliability

        return True

    except Exception as e:
        print(f"Launch error: {e}")
        account.state = f"Error: {str(e)}"
        return False

def kill_gw_processes():
    """
    Kill all existing GW processes
    """
    for proc in psutil.process_iter(['name']):
        try:
            if proc.name().lower() == "gw.exe":
                proc.kill()
        except:
            continue

def clear_mutexes(self):
    mutex_names = [
        "AN-Mutex-Window-Guild Wars",
        "AN-Mutex-Input-Guild Wars",
        "AN-Mutex-Render-Guild Wars",
        self.GW_MUTEX_NAME
    ]
    
    for mutex_name in mutex_names:
        try:
            mutex = None
            try:
                mutex = win32event.OpenMutex(
                    win32con.SYNCHRONIZE | MUTEX_ALL_ACCESS,
                    False,
                    mutex_name
                )
            except:
                continue
                
            if mutex:
                self.debug_window.log(f"Clearing mutex: {mutex_name}")
                win32api.CloseHandle(mutex)
                win32api.Sleep(100)  # Small delay between mutex operations
        except Exception as e:
            self.debug_window.log(f"Error clearing mutex {mutex_name}: {str(e)}", logging.WARNING)

if __name__ == "__main__":
    launcher = GWLauncher()
    launcher.run() 