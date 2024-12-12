import tkinter as tk
from tkinter import filedialog, messagebox
import os
import ctypes
from ctypes import wintypes
import time
import subprocess
import json  # Add at the top with other imports
import sys
import mmap
import shutil
from pathlib import Path

class GWLauncher:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Guild Wars Launcher")
        self.window.geometry("400x400")
        self.window.resizable(False, False)
        
        self.gw_paths = []
        self.dll_path = ""
        self.config_file = "launcher_config.json"

        # Create DLL selection area
        dll_frame = tk.Frame(self.window)
        dll_frame.pack(pady=10, padx=5, fill=tk.X)
        
        self.dll_path_label = tk.Label(dll_frame, text="No DLL selected", width=30)
        self.dll_path_label.pack(side=tk.LEFT, padx=2)
        
        dll_button = tk.Button(dll_frame, text="Select DLL", command=self.select_dll_file)
        dll_button.pack(side=tk.LEFT)

        # Create GW instances area
        label_frame = tk.Frame(self.window)
        label_frame.pack(pady=5, padx=5, fill=tk.X)
        
        tk.Label(label_frame, text="Guild Wars Instances:").pack(side=tk.LEFT)
        
        self.gw_frame = tk.Frame(self.window)
        self.gw_frame.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
        
        # Create buttons frame
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10, padx=5, fill=tk.X)
        
        add_button = tk.Button(button_frame, text="Add Instance", command=self.add_gw_instance)
        add_button.pack(side=tk.LEFT, padx=2)
        
        remove_button = tk.Button(button_frame, text="Remove Instance", command=self.remove_gw_instance)
        remove_button.pack(side=tk.LEFT, padx=2)
        
        self.launch_button = tk.Button(button_frame, text="Launch All", command=self.launch_all_instances, state="disabled")
        self.launch_button.pack(side=tk.RIGHT, padx=2)
        
        # Move these two lines to after launch_button is created
        self.add_gw_instance()  # Add initial GW instance
        self.load_config()      # Load config after all GUI elements are created

    def load_config(self):
        """Load saved configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.dll_path = config.get('dll_path', '')
                saved_gw_paths = config.get('gw_paths', [])
                
                # Update DLL path display if it exists
                if self.dll_path:
                    self.dll_path_label.config(text=os.path.basename(self.dll_path))
                    
                # Create instances for saved GW paths
                for path in saved_gw_paths:
                    if os.path.exists(path):
                        frame = self.add_gw_instance()
                        frame.gw_path = path
                        label = frame.winfo_children()[0]  # Get the label widget
                        label.config(text=os.path.basename(path))
                
                self.check_enable_launch()
        except FileNotFoundError:
            pass  # No config file exists yet

    def save_config(self):
        """Save current configuration to JSON file"""
        config = {
            'dll_path': self.dll_path,
            'gw_paths': self.gw_paths
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f)

    def add_gw_instance(self):
        frame = tk.Frame(self.gw_frame)
        frame.pack(pady=2, padx=5, fill=tk.X)
        
        label = tk.Label(frame, text="No GW.exe selected", width=30)
        label.pack(side=tk.LEFT, padx=2)
        
        select_button = tk.Button(
            frame,
            text="Select GW.exe",
            command=lambda f=frame, l=label: self.select_gw_file(f, l)
        )
        select_button.pack(side=tk.LEFT)
        
        launch_button = tk.Button(
            frame,
            text="Launch",
            command=lambda f=frame: self.launch_single_instance(f),
            state="disabled"
        )
        launch_button.pack(side=tk.LEFT, padx=2)
        frame.launch_button = launch_button  # Store reference to launch button
        
        self.check_enable_launch()
        
        return frame  # Add this line to return the frame

    def remove_gw_instance(self):
        if len(self.gw_frame.winfo_children()) > 1:  # Keep at least one instance
            self.gw_frame.winfo_children()[-1].destroy()
            self.gw_paths.pop() if self.gw_paths else None
            self.check_enable_launch()

    def select_gw_file(self, frame, label):
        filename = filedialog.askopenfilename(
            title="Select Guild Wars Executable",
            filetypes=[("Guild Wars", "Gw.exe"), ("All files", "*.*")]
        )
        if filename:
            frame.gw_path = filename
            label.config(text=os.path.basename(filename))
            frame.launch_button.config(state="normal" if self.dll_path else "disabled")
            self.check_enable_launch()
            self.save_config()  # Save after selecting file

    def check_enable_launch(self):
        # Get all selected GW paths
        self.gw_paths = []
        for frame in self.gw_frame.winfo_children()[1:]:  # Skip the label
            if hasattr(frame, 'gw_path'):
                self.gw_paths.append(frame.gw_path)
                # Update individual launch buttons based on DLL path
                frame.launch_button.config(state="normal" if self.dll_path else "disabled")
        
        # Enable main launch if we have at least one GW path and the DLL
        if self.gw_paths and self.dll_path:
            self.launch_button.config(state="normal")
        else:
            self.launch_button.config(state="disabled")

    def inject_dll(self, pid, dll_path):
        # Windows API constants
        PROCESS_ALL_ACCESS = 0x1F0FFF
        MEM_COMMIT = 0x1000
        MEM_RESERVE = 0x2000
        PAGE_READWRITE = 0x04
        
        # Get handle to kernel32.dll
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
        
        # Get process handle
        process_handle = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
        if not process_handle:
            raise Exception(f"Failed to open process: {ctypes.get_last_error()}")
        
        # Get address of LoadLibraryA
        loadlib_addr = ctypes.c_void_p(
            ctypes.cast(
                kernel32.GetProcAddress(
                    kernel32.GetModuleHandleA(b"kernel32.dll"),
                    b"LoadLibraryA"
                ),
                ctypes.c_void_p
            ).value
        )
        
        # Allocate memory in target process
        path_bytes = (dll_path.encode('ascii') + b'\0')
        path_size = len(path_bytes)
        remote_mem = kernel32.VirtualAllocEx(
            process_handle, 
            None, 
            path_size,
            MEM_COMMIT | MEM_RESERVE,
            PAGE_READWRITE
        )
        
        # Write DLL path to allocated memory
        written = ctypes.c_size_t()
        kernel32.WriteProcessMemory(
            process_handle,
            remote_mem,
            path_bytes,
            path_size,
            ctypes.byref(written)
        )
        
        # Create remote thread to load DLL
        thread_h = kernel32.CreateRemoteThread(
            process_handle,
            None,
            0,
            loadlib_addr,
            remote_mem,
            0,
            None
        )
        
        # Wait for thread to finish
        kernel32.WaitForSingleObject(thread_h, 0xFFFFFFFF)
        
        # Clean up
        kernel32.CloseHandle(thread_h)
        kernel32.CloseHandle(process_handle)

    def select_dll_file(self):
        filename = filedialog.askopenfilename(
            title="Select Py4GW.dll",
            filetypes=[("DLL files", "*.dll"), ("All files", "*.*")]
        )
        if filename:
            self.dll_path = filename
            self.dll_path_label.config(text=os.path.basename(filename))
            self.check_enable_launch()
            self.save_config()  # Save after selecting DLL

    def launch_all_instances(self):
        """Launch all configured Guild Wars instances"""
        for frame in self.gw_frame.winfo_children()[1:]:  # Skip the label
            if hasattr(frame, 'gw_path'):
                self.launch_single_instance(frame)
                time.sleep(2)  # Wait between launches to prevent conflicts

    def launch_single_instance(self, frame):
        """Launch a single Guild Wars instance and inject the DLL"""
        if not hasattr(frame, 'gw_path'):
            return
        
        try:
            # Get the directory containing GW.exe
            gw_dir = os.path.dirname(frame.gw_path)
            
            # Start the process from its directory
            startup_info = subprocess.STARTUPINFO()
            startup_info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            process = subprocess.Popen(
                [frame.gw_path],
                cwd=gw_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                startupinfo=startup_info
            )
            
            # Wait a bit for the process to start
            time.sleep(2)
            
            # Inject the DLL
            if self.dll_path:
                try:
                    self.inject_dll(process.pid, self.dll_path)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to inject DLL: {str(e)}")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch Guild Wars: {str(e)}")

    def run(self):
        self.window.mainloop()

def patch_client(exe_path):
    """Patches GW.exe to allow multiple instances by modifying the mutex check"""
    try:
        # Make a backup if it doesn't exist
        backup_path = exe_path + '.backup'
        if not os.path.exists(backup_path):
            shutil.copy2(exe_path, backup_path)
            print(f"Created backup at {backup_path}")

        # Pattern to search for (mutex check)
        pattern = bytes([0x8B, 0xC8, 0x33, 0xDB, 0x39, 0x8D, 0xC0, 0xFD, 0xFF, 0xFF, 0x0F, 0x95, 0xC3])
        
        # Open file for reading and writing
        with open(exe_path, 'rb+') as f:
            # Memory map the file
            with mmap.mmap(f.fileno(), 0) as mm:
                # Find pattern
                pos = mm.find(pattern)
                if pos == -1:
                    print("Could not find mutex check pattern - file may already be patched")
                    return True
                
                # Move to position and write patch (NOP instructions)
                mm.seek(pos)
                mm.write(bytes([0x90] * len(pattern)))  # NOP out the mutex check
                
        print(f"Successfully patched {exe_path}")
        return True

    except Exception as e:
        print(f"Failed to patch client: {str(e)}")
        return False

def launch_client(gw_path, email=None, password=None, character=None):
    """Launch a GW client with optional login credentials"""
    
    # Ensure the executable exists
    if not os.path.exists(gw_path):
        print(f"Could not find GW executable at: {gw_path}")
        return False

    # Patch the client if needed
    if not patch_client(gw_path):
        return False

    # Build command line arguments
    args = [gw_path]
    if email and password:
        args.extend(['-email', email, '-password', password])
    if character:
        args.extend(['-character', character])

    try:
        # Launch the process
        subprocess.Popen(args)
        return True
    except Exception as e:
        print(f"Failed to launch client: {str(e)}")
        return False

if __name__ == "__main__":
    launcher = GWLauncher()
    launcher.run()
