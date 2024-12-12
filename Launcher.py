import tkinter as tk
from tkinter import filedialog, messagebox
import os
import ctypes
from ctypes import wintypes
import time
import subprocess

class GWLauncher:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Guild Wars Launcher")
        self.window.geometry("400x150")
        self.window.resizable(False, False)
        
        self.gw_path = ""
        self.dll_path = ""
        
        # Create GUI elements
        self.select_gw_button = tk.Button(
            self.window, 
            text="Select GW.exe", 
            command=self.select_gw_file,
            width=15,
            height=1
        )
        self.select_gw_button.pack(pady=5)
        
        self.gw_path_label = tk.Label(
            self.window, 
            text="No GW.exe selected",
            wraplength=350
        )
        self.gw_path_label.pack(pady=2)

        self.select_dll_button = tk.Button(
            self.window, 
            text="Select Py4GW.dll", 
            command=self.select_dll_file,
            width=15,
            height=1
        )
        self.select_dll_button.pack(pady=5)
        
        self.dll_path_label = tk.Label(
            self.window, 
            text="No DLL selected",
            wraplength=350
        )
        self.dll_path_label.pack(pady=2)
        
        self.launch_button = tk.Button(
            self.window, 
            text="Launch Game", 
            command=self.launch_game,
            width=15,
            height=1,
            state="disabled"
        )
        self.launch_button.pack(pady=10)

    def select_gw_file(self):
        filename = filedialog.askopenfilename(
            title="Select Guild Wars Executable",
            filetypes=[("Guild Wars", "Gw.exe"), ("All files", "*.*")]
        )
        if filename:
            self.gw_path = filename
            self.gw_path_label.config(text=os.path.basename(filename))
            self.check_enable_launch()

    def select_dll_file(self):
        filename = filedialog.askopenfilename(
            title="Select Py4GW.dll",
            filetypes=[("DLL files", "*.dll"), ("All files", "*.*")]
        )
        if filename:
            self.dll_path = filename
            self.dll_path_label.config(text=os.path.basename(filename))
            self.check_enable_launch()

    def check_enable_launch(self):
        if self.gw_path and self.dll_path:
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

    def launch_game(self):
        try:
            # Check if selected files exist
            if not os.path.exists(self.gw_path):
                messagebox.showerror("Error", "GW.exe not found!")
                return
                
            if not os.path.exists(self.dll_path):
                messagebox.showerror("Error", "Py4GW.dll not found!")
                return
            
            # Launch Guild Wars
            gw_dir = os.path.dirname(self.gw_path)
            process = subprocess.Popen([self.gw_path], cwd=gw_dir)
            
            # Wait for process to start
            time.sleep(2)
            
            # Inject DLL
            self.inject_dll(process.pid, self.dll_path)
            
            messagebox.showinfo("Success", "Game launched and DLL injected successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error launching game: {str(e)}")

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    launcher = GWLauncher()
    launcher.run()