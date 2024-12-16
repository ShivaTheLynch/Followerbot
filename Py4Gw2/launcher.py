import tkinter as tk
from tkinter import filedialog, messagebox
import time
import os
import ctypes
from ctypes import wintypes

# Constants for patching
SIG_PATCH = b"\x56\x57\x68\x00\x01\x00\x00\x89\x85\xF4\xFE\xFF\xFF\xC7\x00\x00\x00\x00\x00"
PAYLOAD = b"\x31\xC0\x90\xC3"

def patch_mutex(process_handle):
    """Apply the mutex patch to the process."""
    PROCESS_ALL_ACCESS = 0x1F0FFF
    buffer_size = 0x48D000
    buffer = ctypes.create_string_buffer(buffer_size)
    bytes_read = wintypes.SIZE_T()

    # Read process memory
    if not ctypes.windll.kernel32.ReadProcessMemory(
        process_handle, 0x400000, buffer, buffer_size, ctypes.byref(bytes_read)
    ):
        messagebox.showerror("Error", "Failed to read process memory.")
        return False

    idx = buffer.raw.find(SIG_PATCH)
    if idx == -1:
        messagebox.showerror("Error", "Signature not found.")
        return False

    patch_address = 0x400000 + idx - 0x1A

    # Write the patch
    if not ctypes.windll.kernel32.WriteProcessMemory(
        process_handle, patch_address, PAYLOAD, len(PAYLOAD), ctypes.byref(bytes_read)
    ):
        messagebox.showerror("Error", "Failed to write process memory.")
        return False

    return True


def launch_game(gwpath, email, password, character, extraargs, dllpath):
    """Launch the game and handle mutex patching and DLL injection."""
    try:
        STARTUPINFO = ctypes.create_string_buffer(68)
        PROCESS_INFORMATION = ctypes.create_string_buffer(16)

        args = f"-email \"{email}\" -password \"{password}\" -character \"{character}\" {extraargs}"
        command_line = f'"{gwpath}" {args}'

        success = ctypes.windll.kernel32.CreateProcessW(
            gwpath, command_line, None, None, False, 0x4, None, None, STARTUPINFO, PROCESS_INFORMATION
        )
        
        if not success:
            messagebox.showerror("Error", "Failed to launch the game executable.")
            return

        process_handle = ctypes.cast(PROCESS_INFORMATION[0:4], ctypes.POINTER(ctypes.c_void_p))[0]
        thread_handle = ctypes.cast(PROCESS_INFORMATION[4:8], ctypes.POINTER(ctypes.c_void_p))[0]

        if not patch_mutex(process_handle):
            messagebox.showerror("Error", "Mutex patch failed.")
            return

        ctypes.windll.kernel32.ResumeThread(thread_handle)
        
        time.sleep(3)  # Delay before DLL injection

        # Inject DLL
        kernel32 = ctypes.windll.kernel32
        load_library = kernel32.LoadLibraryW
        dll_path_buffer = ctypes.create_unicode_buffer(dllpath)
        remote_memory = kernel32.VirtualAllocEx(
            process_handle, None, len(dllpath) * 2, 0x3000, 0x40
        )
        if not remote_memory:
            messagebox.showerror("Error", "Failed to allocate memory for DLL.")
            return

        kernel32.WriteProcessMemory(
            process_handle, remote_memory, dll_path_buffer, len(dllpath) * 2, None
        )
        remote_thread = kernel32.CreateRemoteThread(
            process_handle, None, 0, load_library, remote_memory, 0, None
        )
        if not remote_thread:
            messagebox.showerror("Error", "Failed to inject DLL.")
            return

        messagebox.showinfo("Success", "Game launched and DLL injected successfully.")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


def create_gui():
    """Create the GUI for the launcher."""
    def browse_gw():
        gw_path.set(filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")]))

    def browse_dll():
        dll_path.set(filedialog.askopenfilename(filetypes=[("DLL Files", "*.dll")]))

    def launch():
        gw = gw_path.get()
        dll = dll_path.get()
        email = email_entry.get()
        password = password_entry.get()
        character = character_entry.get()
        extraargs = extraargs_entry.get()

        if not os.path.isfile(gw):
            messagebox.showerror("Error", "Invalid Gw.exe path.")
            return
        if not os.path.isfile(dll):
            messagebox.showerror("Error", "Invalid DLL path.")
            return

        launch_game(gw, email, password, character, extraargs, dll)

    root = tk.Tk()
    root.title("GW Launcher")

    # Input fields
    gw_path = tk.StringVar()
    dll_path = tk.StringVar()

    tk.Label(root, text="Gw.exe Path:").grid(row=0, column=0, sticky="e")
    tk.Entry(root, textvariable=gw_path, width=50).grid(row=0, column=1)
    tk.Button(root, text="Browse", command=browse_gw).grid(row=0, column=2)

    tk.Label(root, text="DLL Path:").grid(row=1, column=0, sticky="e")
    tk.Entry(root, textvariable=dll_path, width=50).grid(row=1, column=1)
    tk.Button(root, text="Browse", command=browse_dll).grid(row=1, column=2)

    tk.Label(root, text="Email:").grid(row=2, column=0, sticky="e")
    email_entry = tk.Entry(root, width=50)
    email_entry.grid(row=2, column=1)

    tk.Label(root, text="Password:").grid(row=3, column=0, sticky="e")
    password_entry = tk.Entry(root, width=50, show="*")
    password_entry.grid(row=3, column=1)

    tk.Label(root, text="Character:").grid(row=4, column=0, sticky="e")
    character_entry = tk.Entry(root, width=50)
    character_entry.grid(row=4, column=1)

    tk.Label(root, text="Extra Args:").grid(row=5, column=0, sticky="e")
    extraargs_entry = tk.Entry(root, width=50)
    extraargs_entry.grid(row=5, column=1)

    tk.Button(root, text="Launch", command=launch).grid(row=6, column=1)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
