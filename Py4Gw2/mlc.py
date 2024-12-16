import win32gui
import win32con
import win32api
import win32process
import json
from dataclasses import dataclass, asdict
from typing import List, Optional
import os
import subprocess
import win32event
import ctypes
import logging
from datetime import datetime
import time
import psutil
from ctypes import wintypes
import threading
from Patcher import Patcher
import sys
from enum import Enum
# Add these constants
PROCESS_ALL_ACCESS = 0x1F0FFF
VIRTUAL_MEM = 0x1000 | 0x2000  # MEM_COMMIT | MEM_RESERVE
PAGE_READWRITE = 0x04
MEM_RELEASE = 0x8000

class ModType(Enum):
    TEXMOD = "texmod"
    DLL = "dll"

@dataclass
class Mod:
    active: bool = False
    fileName: str = ""
    type: ModType = ModType.TEXMOD

@dataclass
class Account:
    character: str = ""
    email: str = ""
    gwpath: str = ""
    password: str = ""
    extraargs: str = ""
    elevated: bool = False
    title: str = ""
    active: bool = False
    state: str = "Inactive"
    usePluginFolderMods: bool = True
    mods: List[Mod] = None

    def __post_init__(self):
        if self.mods is None:
            self.mods = []

    def add_mod(self, file_path: str, mod_type: ModType):
        """Add a new mod to the account"""
        mod = Mod(
            active=True,
            fileName=file_path,
            type=mod_type
        )
        self.mods.append(mod)

    def remove_mod(self, file_path: str):
        """Remove a mod by its file path"""
        self.mods = [mod for mod in self.mods if mod.fileName != file_path]

    def toggle_mod(self, file_path: str, active: bool):
        """Toggle a mod's active state"""
        for mod in self.mods:
            if mod.fileName == file_path:
                mod.active = active
                break

class DebugWindow:
    def __init__(self, parent_hwnd):
        # Register window class for debug window
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.debug_wnd_proc
        wc.lpszClassName = "GWDebugWindow"
        wc.hbrBackground = win32gui.GetStockObject(win32con.WHITE_BRUSH)
        win32gui.RegisterClass(wc)
        
        # Create debug window
        self.hwnd = win32gui.CreateWindow(
            wc.lpszClassName,
            "Debug Log",
            win32con.WS_OVERLAPPEDWINDOW | win32con.WS_VISIBLE,
            100, 100, 600, 400,
            parent_hwnd, 0, 0, None
        )
        
        # Create edit control for log display
        self.edit_hwnd = win32gui.CreateWindow(
            "EDIT", "",
            win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.WS_VSCROLL |
            win32con.ES_MULTILINE | win32con.ES_AUTOVSCROLL | win32con.ES_READONLY,
            0, 0, 600, 400,
            self.hwnd, 0, 0, None
        )
        
        self.log_messages = []

    def debug_wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_SIZE:
            width = win32api.LOWORD(lparam)
            height = win32api.HIWORD(lparam)
            win32gui.MoveWindow(self.edit_hwnd, 0, 0, width, height, True)
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] {message}\n"
        self.log_messages.append(log_entry)
        
        # Join all messages and set text
        full_log = "".join(self.log_messages)
        win32gui.SetWindowText(self.edit_hwnd, full_log)
        
        # Scroll to bottom
        win32gui.SendMessage(self.edit_hwnd, win32con.EM_SCROLLCARET, 0, 0)

class GWLauncher:
    def __init__(self):
        # Set up file paths first
        if getattr(sys, 'frozen', False):
            # If the application is run as a bundle (compiled executable)
            self.app_directory = os.path.dirname(sys.executable)
        else:
            # If the application is run from a Python interpreter
            self.app_directory = os.path.dirname(os.path.abspath(__file__))
        
        self.accounts_file = os.path.join(self.app_directory, "accounts.json")
        
        # Add menu IDs
        self.ID_LAUNCH = 1001
        self.ID_ADD = 1002
        self.ID_EDIT = 1003
        self.ID_DELETE = 1004
        self.ID_SELECT_DLL = 1005
        self.ID_TOGGLE_DLL = 1006
        
        # Track which account was right-clicked
        self.selected_account: Optional[Account] = None
        
        # Initialize accounts list
        self.accounts: List[Account] = []
        
        # Add DLL settings
        self.dll_path = self.load_dll_path()
        self.dll_enabled = self.load_dll_enabled()
        
        # Register main window class
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.wnd_proc
        wc.lpszClassName = "GWLauncherClass"
        wc.hbrBackground = win32gui.GetStockObject(win32con.WHITE_BRUSH)
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        wc.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        
        try:
            win32gui.UnregisterClass("GWLauncherClass", None)
        except:
            pass
        
        win32gui.RegisterClass(wc)
        
        # Create main window
        style = win32con.WS_OVERLAPPEDWINDOW | win32con.WS_CLIPCHILDREN
        self.hwnd = win32gui.CreateWindow(
            wc.lpszClassName,
            "GW Launcher",
            style,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            300, 400,
            0, 0,
            0, None
        )
        
        # Create debug window BEFORE any logging attempts
        self.debug_window = DebugWindow(self.hwnd)
        
        # Now we can start logging
        self.debug_window.log("GWLauncher initialized")
        self.debug_window.log(f"Application directory: {self.app_directory}")
        self.debug_window.log(f"Accounts file location: {self.accounts_file}")
        
        # Load accounts after debug window is created
        self.load_accounts()
        
        # Show main window
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
        win32gui.UpdateWindow(self.hwnd)
        
        # Add mod management to launcher
        self.load_mods()

    def wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
            return 0
            
        elif msg == win32con.WM_ERASEBKGND:
            return 1  # Prevent background erasing
            
        elif msg == win32con.WM_PAINT:
            self.paint()
            return 0
            
        elif msg == win32con.WM_LBUTTONDOWN:
            x = win32api.LOWORD(lparam)
            y = win32api.HIWORD(lparam)
            self.handle_click(x, y)
            return 0
            
        elif msg == win32con.WM_RBUTTONUP:
            x = win32api.LOWORD(lparam)
            y = win32api.HIWORD(lparam)
            self.show_context_menu(x, y)
            return 0
            
        elif msg == win32con.WM_COMMAND:
            self.handle_command(wparam)
            return 0
            
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def paint(self):
        hdc, ps = win32gui.BeginPaint(self.hwnd)
        rect = win32gui.GetClientRect(self.hwnd)
        
        try:
            # Create memory DC for double buffering
            memdc = win32gui.CreateCompatibleDC(hdc)
            bitmap = win32gui.CreateCompatibleBitmap(hdc, rect[2], rect[3])
            old_bitmap = win32gui.SelectObject(memdc, bitmap)
            
            try:
                # Clear background
                brush = win32gui.GetStockObject(win32con.WHITE_BRUSH)
                win32gui.FillRect(memdc, rect, brush)
                
                # Draw accounts list with buttons
                y = 5
                for account in self.accounts:
                    # Account text
                    text = f"{account.title or account.character} - {account.state}"
                    win32gui.DrawText(
                        memdc, text, -1,
                        (5, y, rect[2]-205, y+20),  # Reduced width to make room for buttons
                        win32con.DT_LEFT | win32con.DT_VCENTER | win32con.DT_SINGLELINE | win32con.DT_END_ELLIPSIS
                    )
                    
                    # Draw buttons
                    button_width = 60
                    button_spacing = 5
                    button_x = rect[2] - (button_width * 3 + button_spacing * 2)
                    
                    # Launch button
                    win32gui.Rectangle(memdc, button_x, y, button_x + button_width, y + 20)
                    win32gui.DrawText(memdc, "Launch", -1,
                        (button_x, y, button_x + button_width, y + 20),
                        win32con.DT_CENTER | win32con.DT_VCENTER | win32con.DT_SINGLELINE
                    )
                    
                    # Edit button
                    button_x += button_width + button_spacing
                    win32gui.Rectangle(memdc, button_x, y, button_x + button_width, y + 20)
                    win32gui.DrawText(memdc, "Edit", -1,
                        (button_x, y, button_x + button_width, y + 20),
                        win32con.DT_CENTER | win32con.DT_VCENTER | win32con.DT_SINGLELINE
                    )
                    
                    # Delete button
                    button_x += button_width + button_spacing
                    win32gui.Rectangle(memdc, button_x, y, button_x + button_width, y + 20)
                    win32gui.DrawText(memdc, "Delete", -1,
                        (button_x, y, button_x + button_width, y + 20),
                        win32con.DT_CENTER | win32con.DT_VCENTER | win32con.DT_SINGLELINE
                    )
                    
                    y += 25
                
                # Draw bottom buttons
                bottom_y = rect[3] - 30
                
                # Add Account button
                win32gui.Rectangle(memdc, 5, bottom_y, 105, bottom_y + 25)
                win32gui.DrawText(memdc, "Add Account", -1,
                    (5, bottom_y, 105, bottom_y + 25),
                    win32con.DT_CENTER | win32con.DT_VCENTER | win32con.DT_SINGLELINE
                )
                
                # DLL Options button
                win32gui.Rectangle(memdc, 115, bottom_y, 215, bottom_y + 25)
                win32gui.DrawText(memdc, "DLL Options", -1,
                    (115, bottom_y, 215, bottom_y + 25),
                    win32con.DT_CENTER | win32con.DT_VCENTER | win32con.DT_SINGLELINE
                )
                
                # Copy from memory DC to window DC
                win32gui.BitBlt(
                    hdc, 0, 0, rect[2], rect[3],
                    memdc, 0, 0,
                    win32con.SRCCOPY
                )
            finally:
                win32gui.SelectObject(memdc, old_bitmap)
                win32gui.DeleteObject(bitmap)
                win32gui.DeleteDC(memdc)
        finally:
            win32gui.EndPaint(self.hwnd, ps)

    def load_accounts(self):
        self.debug_window.log("Starting account load process...")
        self.debug_window.log(f"Loading from: {self.accounts_file}")
        
        try:
            if os.path.exists(self.accounts_file):
                with open(self.accounts_file, "r", encoding='utf-8') as f:
                    file_content = f.read()
                    self.debug_window.log(f"File content length: {len(file_content)} bytes")
                    if not file_content.strip():
                        self.debug_window.log("accounts.json is empty")
                        self.accounts = []
                        return
                    
                    accounts_data = json.loads(file_content)
                    self.debug_window.log(f"Parsed JSON data: {accounts_data}")
                    
                    self.accounts = []
                    for acc_data in accounts_data:
                        acc = Account(
                            character=acc_data.get('character', ''),
                            email=acc_data.get('email', ''),
                            gwpath=acc_data.get('gwpath', ''),
                            password=acc_data.get('password', ''),
                            extraargs=acc_data.get('extraargs', ''),
                            elevated=acc_data.get('elevated', False),
                            title=acc_data.get('title', ''),
                            active=acc_data.get('active', False),
                            state=acc_data.get('state', 'Inactive')
                        )
                        self.accounts.append(acc)
                    
                    self.debug_window.log(f"Successfully loaded {len(self.accounts)} accounts")
            else:
                self.debug_window.log("accounts.json does not exist")
                self.accounts = []
        except FileNotFoundError:
            self.debug_window.log("FileNotFoundError while loading accounts.json")
            self.accounts = []
        except json.JSONDecodeError as e:
            self.debug_window.log(f"JSON decode error: {str(e)}")
            if os.path.exists(self.accounts_file):
                backup_path = f"{self.accounts_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.accounts_file, backup_path)
                self.debug_window.log(f"Corrupted file backed up to {backup_path}")
            self.accounts = []
        except Exception as e:
            self.debug_window.log(f"Unexpected error loading accounts: {str(e)}")
            self.accounts = []

    def save_accounts(self):
        self.debug_window.log("Starting account save process...")
        self.debug_window.log(f"Saving to: {self.accounts_file}")
        
        try:
            # Ensure the directory exists
            directory = os.path.dirname(self.accounts_file)
            if not os.path.exists(directory):
                os.makedirs(directory)
                self.debug_window.log(f"Created directory: {directory}")

            # Create backup of existing file if it exists
            if os.path.exists(self.accounts_file):
                backup_path = f"{self.accounts_file}.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.replace(self.accounts_file, backup_path)
                self.debug_window.log(f"Created backup at: {backup_path}")

            # Convert accounts to dictionary format
            accounts_data = []
            for account in self.accounts:
                acc_dict = {
                    'character': account.character,
                    'email': account.email,
                    'gwpath': account.gwpath,
                    'password': account.password,
                    'extraargs': account.extraargs,
                    'elevated': account.elevated,
                    'title': account.title,
                    'active': account.active,
                    'state': account.state
                }
                accounts_data.append(acc_dict)
            
            self.debug_window.log(f"Preparing to save {len(accounts_data)} accounts")
            
            # Save to file with pretty printing
            with open(self.accounts_file, "w", encoding='utf-8') as f:
                json.dump(accounts_data, f, indent=4, ensure_ascii=False)
            
            self.debug_window.log("Accounts saved successfully")
            
            # Verify the save
            if os.path.exists(self.accounts_file):
                file_size = os.path.getsize(self.accounts_file)
                self.debug_window.log(f"Verified: File exists and is {file_size} bytes")
                
                # Try to read it back to verify integrity
                with open(self.accounts_file, "r", encoding='utf-8') as f:
                    verify_data = json.load(f)
                    self.debug_window.log(f"Verified: File contains {len(verify_data)} accounts")
            else:
                self.debug_window.log("Warning: File does not exist after save!")

        except Exception as e:
            self.debug_window.log(f"Error saving accounts: {str(e)}")
            if 'backup_path' in locals():
                try:
                    os.replace(backup_path, self.accounts_file)
                    self.debug_window.log("Restored backup after save failure")
                except Exception as restore_error:
                    self.debug_window.log(f"Failed to restore backup: {str(restore_error)}")
            raise

    def inject_dll(self, pid):
        if not self.dll_path or not os.path.exists(self.dll_path):
            self.debug_window.log("Invalid DLL path")
            return False

        self.debug_window.log(f"Starting DLL injection for PID: {pid}")
        kernel32 = ctypes.windll.kernel32
        process_handle = None
        allocated_memory = None
        thread_handle = None

        try:
            # Get process handle
            process_handle = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
            if not process_handle:
                self.debug_window.log(f"Failed to open process. Error: {ctypes.get_last_error()}")
                return False

            # Get LoadLibraryA address
            loadlib_addr = kernel32.GetProcAddress(
                kernel32._handle,
                b"LoadLibraryA"
            )
            if not loadlib_addr:
                self.debug_window.log("Failed to get LoadLibraryA address")
                return False

            # Prepare DLL path
            dll_path_bytes = self.dll_path.encode('ascii') + b'\0'
            path_size = len(dll_path_bytes)

            # Allocate memory in target process
            allocated_memory = kernel32.VirtualAllocEx(
                process_handle,
                0,
                path_size,
                VIRTUAL_MEM,
                PAGE_READWRITE
            )
            if not allocated_memory:
                self.debug_window.log("Failed to allocate memory")
                return False

            # Write DLL path to allocated memory
            written = ctypes.c_size_t(0)
            write_success = kernel32.WriteProcessMemory(
                process_handle,
                allocated_memory,
                dll_path_bytes,
                path_size,
                ctypes.byref(written)
            )
            if not write_success or written.value != path_size:
                self.debug_window.log("Failed to write to process memory")
                return False

            # Create remote thread
            thread_handle = kernel32.CreateRemoteThread(
                process_handle,
                None,
                0,
                loadlib_addr,
                allocated_memory,
                0,
                None
            )
            if not thread_handle:
                self.debug_window.log("Failed to create remote thread")
                return False

            # Wait for thread completion
            kernel32.WaitForSingleObject(thread_handle, 5000)  # 5 second timeout

            # Get thread exit code
            exit_code = ctypes.c_ulong(0)
            if kernel32.GetExitCodeThread(thread_handle, ctypes.byref(exit_code)):
                self.debug_window.log(f"Injection completed with exit code: {exit_code.value}")
                return exit_code.value != 0
            return False

        except Exception as e:
            self.debug_window.log(f"DLL injection failed with error: {str(e)}")
            return False

        finally:
            # Cleanup
            if thread_handle:
                kernel32.CloseHandle(thread_handle)
            if allocated_memory and process_handle:
                kernel32.VirtualFreeEx(process_handle, allocated_memory, 0, MEM_RELEASE)
            if process_handle:
                kernel32.CloseHandle(process_handle)

    def wait_for_gw_window(self, pid, timeout=30):
        """Wait for GW window to be created and fully loaded"""
        self.debug_window.log(f"Waiting for GW window (PID: {pid})")
        start_time = time.time()
        found_windows = []
        
        def enum_windows_callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                try:
                    _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                    if window_pid == pid:
                        title = win32gui.GetWindowText(hwnd)
                        self.debug_window.log(f"Found window with title: '{title}' for PID: {pid}")
                        # Accept any window from the process initially
                        found_windows.append(hwnd)
                except Exception as e:
                    self.debug_window.log(f"Error in callback: {str(e)}")
            return True

        while time.time() - start_time < timeout:
            try:
                process = psutil.Process(pid)
                if process.status() != psutil.STATUS_RUNNING:
                    self.debug_window.log(f"Process {pid} is not running")
                    return False

                # Clear previous findings
                found_windows.clear()
                win32gui.EnumWindows(enum_windows_callback, None)
                
                if found_windows:
                    self.debug_window.log(f"Found {len(found_windows)} windows for process {pid}")
                    # Return True if we found any window from the process
                    return True
                
            except psutil.NoSuchProcess:
                self.debug_window.log(f"Process {pid} no longer exists")
                return False
            except Exception as e:
                self.debug_window.log(f"Error while waiting for GW window: {str(e)}")
                return False
                
            time.sleep(0.5)
            
            # Add progress indicator every 5 seconds
            elapsed = time.time() - start_time
            if elapsed % 5 < 0.5:
                self.debug_window.log(f"Still waiting... ({int(elapsed)}s)")
                # List all windows for the process
                try:
                    process = psutil.Process(pid)
                    self.debug_window.log(f"Process status: {process.status()}")
                    self.debug_window.log(f"Process command line: {process.cmdline()}")
                except Exception as e:
                    self.debug_window.log(f"Error getting process info: {str(e)}")
        
        self.debug_window.log(f"Timeout waiting for window of process {pid}")
        return False

    def launch_gw(self, account: Account):
        patcher = Patcher()
        try:
            pid = patcher.launch_and_patch(
                account.gwpath,
                account.email,
                account.password,
                account.character,
                account.extraargs,
                account.elevated
            )

            if pid is None:
                self.debug_window.log("Failed to launch or patch Guild Wars.")
                account.state = "Launch Failed"
                win32gui.InvalidateRect(self.hwnd, None, True)
                return
            else:
                self.debug_window.log(f"Launched and patched GW with PID: {pid}")


            if self.dll_enabled:
                def injection_thread():
                    try:
                        # Wait for window
                        if self.wait_for_gw_window(pid):
                            self.debug_window.log("GW window found, waiting for initialization...")
                            time.sleep(5)  # Reduced wait time
                            
                            # Verify process is still running
                            try:
                                process = psutil.Process(pid)
                                if process.status() != psutil.STATUS_RUNNING:
                                    self.debug_window.log("Process is no longer running")
                                    return
                            except psutil.NoSuchProcess:
                                self.debug_window.log("Process no longer exists")
                                return
                            
                            self.debug_window.log("Attempting DLL injection...")
                            if self.inject_dll(pid):
                                self.debug_window.log("DLL injection successful")
                            else:
                                self.debug_window.log("DLL injection failed")
                        else:
                            self.debug_window.log("Failed to detect GW window")
                    except Exception as e:
                        self.debug_window.log(f"Error in injection thread: {str(e)}")

                threading.Thread(target=injection_thread, daemon=True).start()

            account.state = "Active"
            win32gui.InvalidateRect(self.hwnd, None, True)

        except Exception as e:
            self.debug_window.log(f"Error launching GW: {str(e)}")
            account.state = "Launch Failed"
            win32gui.InvalidateRect(self.hwnd, None, True)

    def run(self):
        while True:
            try:
                msg = win32gui.PeekMessage(None, 0, 0, win32con.PM_REMOVE)
                if msg[1] == win32con.WM_QUIT:
                    break
                win32gui.TranslateMessage(msg[1])
                win32gui.DispatchMessage(msg[1])
            except:
                win32gui.PumpWaitingMessages()

    def handle_click(self, x, y):
        rect = win32gui.GetClientRect(self.hwnd)
        width = rect[2]
        
        # Check if click is on bottom buttons
        bottom_y = rect[3] - 30
        if bottom_y <= y <= bottom_y + 25:
            if 5 <= x <= 105:  # Add Account button
                self.debug_window.log("Add Account button clicked")
                self.show_account_dialog()
                return
            elif 115 <= x <= 215:  # DLL Options button
                self.debug_window.log("DLL Options button clicked")
                self.show_dll_options()
                return
        
        # Check if click is on account buttons
        account_idx = y // 25
        if 0 <= account_idx < len(self.accounts):
            button_width = 60
            button_spacing = 5
            button_x = width - (button_width * 3 + button_spacing * 2)
            
            if button_x <= x <= button_x + button_width:  # Launch button
                self.debug_window.log(f"Launch button clicked for account {account_idx}")
                self.launch_gw(self.accounts[account_idx])
            elif button_x + button_width + button_spacing <= x <= button_x + button_width * 2 + button_spacing:  # Edit button
                self.debug_window.log(f"Edit button clicked for account {account_idx}")
                self.show_account_dialog(self.accounts[account_idx])
            elif button_x + button_width * 2 + button_spacing * 2 <= x <= button_x + button_width * 3 + button_spacing * 2:  # Delete button
                self.debug_window.log(f"Delete button clicked for account {account_idx}")
                self.accounts.remove(self.accounts[account_idx])
                self.save_accounts()
                win32gui.InvalidateRect(self.hwnd, None, True)

    def show_context_menu(self, x, y):
        # Find clicked account
        account_idx = y // 25
        self.selected_account = self.accounts[account_idx] if 0 <= account_idx < len(self.accounts) else None
        
        # Create popup menu
        menu = win32gui.CreatePopupMenu()
        
        if self.selected_account:
            win32gui.AppendMenu(menu, win32con.MF_STRING, self.ID_LAUNCH, "Launch")
            win32gui.AppendMenu(menu, win32con.MF_STRING, self.ID_EDIT, "Edit")
            win32gui.AppendMenu(menu, win32con.MF_STRING, self.ID_DELETE, "Delete")
            win32gui.AppendMenu(menu, win32con.MF_SEPARATOR, 0, "")
        
        win32gui.AppendMenu(menu, win32con.MF_STRING, self.ID_ADD, "Add Account")
        win32gui.AppendMenu(menu, win32con.MF_SEPARATOR, 0, "")
        
        # DLL options submenu
        dll_menu = win32gui.CreatePopupMenu()
        win32gui.AppendMenu(dll_menu, win32con.MF_STRING, self.ID_SELECT_DLL, "Select DLL")
        # Add checkmark if DLL injection is enabled
        flags = win32con.MF_STRING | (win32con.MF_CHECKED if self.dll_enabled else win32con.MF_UNCHECKED)
        win32gui.AppendMenu(dll_menu, flags, self.ID_TOGGLE_DLL, "Enable DLL Injection")
        
        win32gui.AppendMenu(menu, win32con.MF_POPUP | win32con.MF_STRING, dll_menu, "DLL Options")
        
        # Convert client coordinates to screen coordinates
        pt = win32gui.ClientToScreen(self.hwnd, (x, y))
        win32gui.TrackPopupMenu(
            menu,
            win32con.TPM_LEFTALIGN | win32con.TPM_RIGHTBUTTON,
            pt[0], pt[1], 0, self.hwnd, None
        )
        win32gui.DestroyMenu(menu)

    def handle_command(self, wparam):
        command = win32api.LOWORD(wparam)
        
        if command == self.ID_LAUNCH and self.selected_account:
            # Only check for DLL if injection is enabled
            if self.dll_enabled and not self.dll_path:
                result = ctypes.windll.user32.MessageBoxW(
                    self.hwnd,
                    "DLL injection is enabled but no DLL is selected. Would you like to select one now?",
                    "DLL Selection",
                    win32con.MB_YESNO | win32con.MB_ICONQUESTION
                )
                if result == win32con.IDYES:
                    if self.select_dll():
                        self.launch_gw(self.selected_account)
                else:
                    self.debug_window.log("Launch cancelled - no DLL selected")
            else:
                self.launch_gw(self.selected_account)
            
        elif command == self.ID_ADD:
            self.show_account_dialog()
            
        elif command == self.ID_EDIT and self.selected_account:
            self.show_account_dialog(self.selected_account)
            
        elif command == self.ID_DELETE and self.selected_account:
            self.accounts.remove(self.selected_account)
            self.save_accounts()
            win32gui.InvalidateRect(self.hwnd, None, True)
            
        elif command == self.ID_SELECT_DLL:
            self.select_dll()
            
        elif command == self.ID_TOGGLE_DLL:
            self.dll_enabled = not self.dll_enabled
            self.save_settings()
            self.debug_window.log(f"DLL injection {'enabled' if self.dll_enabled else 'disabled'}")

    def show_account_dialog(self, account: Optional[Account] = None):
        self.debug_window.log("Opening account dialog...")
        
        # Dialog dimensions - adjusted for content
        DIALOG_WIDTH = 400
        DIALOG_HEIGHT = 400  # Increased height
        
        # Create dialog window
        dialog_class = "GWAccountDialog"
        
        # First try to unregister the class if it exists
        try:
            win32gui.UnregisterClass(dialog_class, None)
        except:
            pass
        
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.dialog_proc
        wc.lpszClassName = dialog_class
        wc.hbrBackground = win32gui.GetStockObject(win32con.WHITE_BRUSH)
        
        try:
            win32gui.RegisterClass(wc)
        except Exception as e:
            self.debug_window.log(f"Error registering dialog class: {str(e)}")
            return
        
        # Center dialog
        screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        x = (screen_width - DIALOG_WIDTH) // 2
        y = (screen_height - DIALOG_HEIGHT) // 2
        
        # Create dialog window
        style = win32con.WS_POPUP | win32con.WS_CAPTION | win32con.WS_SYSMENU
        self.dialog_hwnd = win32gui.CreateWindow(
            dialog_class,
            "Add Account" if not account else "Edit Account",
            style,
            x, y, DIALOG_WIDTH, DIALOG_HEIGHT,
            self.hwnd, 0, 0, None
        )
        
        # Store editing state
        self.editing_account = account
        
        # Create controls
        self.controls = {}
        y_pos = 20
        SPACING = 35  # Consistent spacing
        
        # Labels and text inputs
        fields = [
            ("character", "Character Name:"),
            ("email", "Email:"),
            ("password", "Password:"),
            ("title", "Display Title (optional):")
        ]
        
        for field_id, label in fields:
            # Label
            win32gui.CreateWindow(
                "STATIC", label,
                win32con.WS_CHILD | win32con.WS_VISIBLE,
                20, y_pos, 100, 20,
                self.dialog_hwnd, 0, 0, None
            )
            
            # Text input
            style = win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.WS_BORDER
            if field_id == "password":
                style |= win32con.ES_PASSWORD
            
            edit_hwnd = win32gui.CreateWindow(
                "EDIT", "",
                style,
                130, y_pos, 240, 20,
                self.dialog_hwnd, 0, 0, None
            )
            
            self.controls[field_id] = edit_hwnd
            if account:
                win32gui.SetWindowText(edit_hwnd, getattr(account, field_id))
            
            y_pos += SPACING
        
        # GW Path selection
        win32gui.CreateWindow(
            "STATIC", "Guild Wars Path:",
            win32con.WS_CHILD | win32con.WS_VISIBLE,
            20, y_pos, 100, 20,
            self.dialog_hwnd, 0, 0, None
        )
        
        self.controls["gwpath"] = win32gui.CreateWindow(
            "EDIT", account.gwpath if account else "",
            win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.WS_BORDER,
            130, y_pos, 200, 20,
            self.dialog_hwnd, 0, 0, None
        )
        
        # Browse button
        self.browse_btn = win32gui.CreateWindow(
            "BUTTON", "Browse",
            win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.BS_PUSHBUTTON,
            340, y_pos, 40, 20,
            self.dialog_hwnd, 1001, 0, None
        )
        
        y_pos += SPACING
        
        # Extra args
        win32gui.CreateWindow(
            "STATIC", "Extra Arguments:",
            win32con.WS_CHILD | win32con.WS_VISIBLE,
            20, y_pos, 100, 20,
            self.dialog_hwnd, 0, 0, None
        )
        
        self.controls["extraargs"] = win32gui.CreateWindow(
            "EDIT", account.extraargs if account else "",
            win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.WS_BORDER,
            130, y_pos, 240, 20,
            self.dialog_hwnd, 0, 0, None
        )
        
        y_pos += SPACING
        
        # Elevated checkbox
        self.controls["elevated"] = win32gui.CreateWindow(
            "BUTTON", "Run as Administrator",
            win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.BS_AUTOCHECKBOX,
            20, y_pos, 200, 20,
            self.dialog_hwnd, 0, 0, None
        )
        
        if account and account.elevated:
            win32gui.SendMessage(self.controls["elevated"], win32con.BM_SETCHECK, 1, 0)
        
        y_pos += SPACING
        
        # Button spacing from bottom
        BUTTON_MARGIN = 20
        button_y = DIALOG_HEIGHT - 45 - BUTTON_MARGIN  # 45 is button height + margin
        
        # OK/Cancel buttons
        self.ok_btn = win32gui.CreateWindow(
            "BUTTON", "OK",
            win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.BS_PUSHBUTTON,
            DIALOG_WIDTH - 180, button_y,
            70, 25,
            self.dialog_hwnd, 1002, 0, None
        )
        
        self.cancel_btn = win32gui.CreateWindow(
            "BUTTON", "Cancel",
            win32con.WS_CHILD | win32con.WS_VISIBLE | win32con.BS_PUSHBUTTON,
            DIALOG_WIDTH - 90, button_y,
            70, 25,
            self.dialog_hwnd, 1003, 0, None
        )
        
        self.debug_window.log("Account dialog created and shown")
        # Show dialog
        win32gui.ShowWindow(self.dialog_hwnd, win32con.SW_SHOW)

    def dialog_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_COMMAND:
            id = win32api.LOWORD(wparam)
            
            if id == 1001:  # Browse button
                flags = win32con.OFN_FILEMUSTEXIST | win32con.OFN_PATHMUSTEXIST
                filter = "Executable files (*.exe)\0*.exe\0All files (*.*)\0*.*\0"
                
                try:
                    filename = win32gui.GetOpenFileNameW(
                        Filter=filter,
                        Title="Select Guild Wars Client",
                        Flags=flags
                    )[0]
                    win32gui.SetWindowText(self.controls["gwpath"], filename)
                except:
                    pass
                    
            elif id == 1002:  # OK button
                self.save_dialog_data()
                win32gui.DestroyWindow(hwnd)
                
            elif id == 1003:  # Cancel button
                win32gui.DestroyWindow(hwnd)
                
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def save_dialog_data(self):
        self.debug_window.log("Starting to save dialog data...")
        
        # Get values from controls
        data = {}
        for field, hwnd in self.controls.items():
            if field == "elevated":
                data[field] = bool(win32gui.SendMessage(hwnd, win32con.BM_GETCHECK, 0, 0))
            else:
                data[field] = win32gui.GetWindowText(hwnd)
        
        self.debug_window.log(f"Collected dialog data: {data}")
        
        # Validate required fields
        required_fields = ["character", "email", "password", "gwpath"]
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            message = "Please fill in the following required fields:\n" + "\n".join(missing_fields)
            self.debug_window.log(f"Validation failed - missing fields: {missing_fields}")
            ctypes.windll.user32.MessageBoxW(
                self.dialog_hwnd,
                message,
                "Missing Information",
                win32con.MB_OK | win32con.MB_ICONWARNING
            )
            return
        
        # Validate GW path exists
        if not os.path.exists(data["gwpath"]):
            self.debug_window.log(f"Invalid GW path: {data['gwpath']}")
            ctypes.windll.user32.MessageBoxW(
                self.dialog_hwnd,
                "The specified Guild Wars path does not exist.",
                "Invalid Path",
                win32con.MB_OK | win32con.MB_ICONWARNING
            )
            return

        if self.editing_account:
            self.debug_window.log("Updating existing account")
            # Update existing account
            for key, value in data.items():
                setattr(self.editing_account, key, value)
        else:
            self.debug_window.log("Creating new account")
            # Create new account
            new_account = Account(**data)
            self.accounts.append(new_account)
        
        try:
            self.save_accounts()
            self.debug_window.log("Account saved successfully")
            win32gui.InvalidateRect(self.hwnd, None, True)
            win32gui.DestroyWindow(self.dialog_hwnd)
        except Exception as e:
            self.debug_window.log(f"Error while saving: {str(e)}")
            ctypes.windll.user32.MessageBoxW(
                self.dialog_hwnd,
                f"Error saving accounts: {str(e)}",
                "Save Error",
                win32con.MB_OK | win32con.MB_ICONERROR
            )

    def load_dll_path(self):
        """Load DLL path from settings file"""
        settings_file = os.path.join(self.app_directory, "settings.json")
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get('dll_path', '')
            return ''
        except Exception as e:
            return ''

    def save_dll_path(self, path):
        """Save DLL path to settings file"""
        settings_file = os.path.join(self.app_directory, "settings.json")
        try:
            # Load existing settings if file exists
            settings = {}
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
            
            # Update DLL path
            settings['dll_path'] = path
            
            # Save all settings back to file
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            
            self.debug_window.log(f"Saved DLL path: {path}")
            return True
        except Exception as e:
            self.debug_window.log(f"Error saving DLL path: {str(e)}")
            return False

    def select_dll(self):
        """Open file dialog to select DLL"""
        try:
            flags = win32con.OFN_FILEMUSTEXIST | win32con.OFN_PATHMUSTEXIST
            filter_str = "DLL files (*.dll)\0*.dll\0All files (*.*)\0*.*\0"
            
            filename = win32gui.GetOpenFileNameW(
                Filter=filter_str,
                Title="Select Injection DLL",
                Flags=flags
            )[0]
            
            if filename:
                self.dll_path = filename
                if self.save_dll_path(filename):
                    self.debug_window.log(f"Selected and saved new DLL: {filename}")
                    return True
                else:
                    self.debug_window.log("Failed to save DLL path")
            return False
        except Exception as e:
            self.debug_window.log(f"Error selecting DLL: {str(e)}")
            return False

    def load_dll_enabled(self):
        """Load DLL enabled setting from settings file"""
        settings_file = os.path.join(self.app_directory, "settings.json")
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get('dll_enabled', False)
            return False
        except Exception as e:
            return False

    def save_settings(self):
        """Save all settings to file"""
        settings_file = os.path.join(self.app_directory, "settings.json")
        try:
            settings = {
                'dll_path': self.dll_path,
                'dll_enabled': self.dll_enabled
            }
            
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            
            self.debug_window.log("Settings saved successfully")
        except Exception as e:
            self.debug_window.log(f"Error saving settings: {str(e)}")

    def show_dll_options(self):
        menu = win32gui.CreatePopupMenu()
        win32gui.AppendMenu(menu, win32con.MF_STRING, self.ID_SELECT_DLL, "Select DLL")
        flags = win32con.MF_STRING | (win32con.MF_CHECKED if self.dll_enabled else win32con.MF_UNCHECKED)
        win32gui.AppendMenu(menu, flags, self.ID_TOGGLE_DLL, "Enable DLL Injection")
        
        rect = win32gui.GetClientRect(self.hwnd)
        pt = win32gui.ClientToScreen(self.hwnd, (115, rect[3] - 30))
        
        win32gui.TrackPopupMenu(
            menu,
            win32con.TPM_LEFTALIGN | win32con.TPM_RIGHTBUTTON,
            pt[0], pt[1], 0, self.hwnd, None
        )
        win32gui.DestroyMenu(menu)

    def load_mods(self):
        """Load mods for all accounts from the accounts file"""
        try:
            with open(self.accounts_file, 'r') as f:
                accounts_data = json.load(f)
                for acc_data in accounts_data:
                    if 'mods' in acc_data:
                        mods = []
                        for mod_data in acc_data['mods']:
                            mod = Mod(
                                active=mod_data.get('active', False),
                                fileName=mod_data.get('fileName', ''),
                                type=ModType(mod_data.get('type', 'texmod'))
                            )
                            mods.append(mod)
                        acc_data['mods'] = mods
                    else:
                        acc_data['mods'] = []
                self.accounts = [Account(**acc) for acc in accounts_data]
        except FileNotFoundError:
            self.accounts = []

    def save_mods(self):
        """Save mods configuration to accounts file"""
        accounts_data = []
        for account in self.accounts:
            acc_dict = account.__dict__.copy()
            acc_dict['mods'] = [
                {
                    'active': mod.active,
                    'fileName': mod.fileName,
                    'type': mod.type.value
                }
                for mod in account.mods
            ]
            accounts_data.append(acc_dict)
            
        with open(self.accounts_file, 'w') as f:
            json.dump(accounts_data, f, indent=4)

    def launch_account_with_mods(self, account: Account):
        """Launch an account with its configured mods"""
        if account.usePluginFolderMods and account.mods:
            # Handle Texmod mods
            texmods = [mod for mod in account.mods 
                      if mod.active and mod.type == ModType.TEXMOD]
            for texmod in texmods:
                self.launch_texmod(texmod.fileName, account)

            # Handle DLL mods
            dlls = [mod for mod in account.mods 
                   if mod.active and mod.type == ModType.DLL]
            for dll in dlls:
                self.copy_dll_to_plugins(dll.fileName, account)

        # Continue with your existing launch logic
        self.launch_game(account)

    def launch_texmod(self, texmod_path: str, account: Account):
        """Launch Texmod with the specified mod"""
        # Implement your Texmod launching logic here
        pass

    def copy_dll_to_plugins(self, dll_path: str, account: Account):
        """Copy a DLL mod to the plugins folder"""
        plugins_dir = os.path.join(os.path.dirname(account.gwpath), 'plugins')
        if not os.path.exists(plugins_dir):
            os.makedirs(plugins_dir)
            
        dll_name = os.path.basename(dll_path)
        target_path = os.path.join(plugins_dir, dll_name)
        
        try:
            import shutil
            shutil.copy2(dll_path, target_path)
        except Exception as e:
            print(f"Failed to copy DLL {dll_path}: {e}")

    def launch_game(self, account: Account):
        """Launch the game with the account configuration"""
        # Your existing game launch logic
        pass

if __name__ == "__main__":
    launcher = GWLauncher()
    launcher.run()
