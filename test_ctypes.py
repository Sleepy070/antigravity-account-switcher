import ctypes
from ctypes import wintypes

TH32CS_SNAPPROCESS = 0x00000002

class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [("dwSize", wintypes.DWORD),
                ("cntUsage", wintypes.DWORD),
                ("th32ProcessID", wintypes.DWORD),
                ("th32DefaultHeapID", ctypes.POINTER(wintypes.ULONG)),
                ("th32ModuleID", wintypes.DWORD),
                ("cntThreads", wintypes.DWORD),
                ("th32ParentProcessID", wintypes.DWORD),
                ("pcPriClassBase", wintypes.LONG),
                ("dwFlags", wintypes.DWORD),
                ("szExeFile", ctypes.c_char * 260)]

def test():
    kernel32 = ctypes.windll.kernel32
    hProcessSnap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if hProcessSnap == -1:
        print("Failed to create snapshot")
        return
        
    pe32 = PROCESSENTRY32()
    pe32.dwSize = ctypes.sizeof(PROCESSENTRY32)
    
    if not kernel32.Process32First(hProcessSnap, ctypes.byref(pe32)):
        kernel32.CloseHandle(hProcessSnap)
        print("Failed to get first process")
        return
        
    found = False
    count = 0
    while True:
        count += 1
        exe = pe32.szExeFile.decode('utf-8', errors='ignore')
        if exe.lower() == "explorer.exe":
            found = True
            
        if not kernel32.Process32Next(hProcessSnap, ctypes.byref(pe32)):
            break
            
    kernel32.CloseHandle(hProcessSnap)
    print(f"Explorer found: {found}, Total procs: {count}")

if __name__ == "__main__":
    test()
