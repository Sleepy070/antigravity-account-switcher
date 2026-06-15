import os
import sys
import json
import shutil
import subprocess
import time
import urllib.request
import ctypes
from ctypes import wintypes

# Configure paths
USER_HOME = os.path.expanduser('~')
APPDATA = os.environ.get('APPDATA', '')
LOCALAPPDATA = os.environ.get('LOCALAPPDATA', '')



# Application data directories to backup/restore
SOURCES = {
    "standalone": {
        "name": "Antigravity 客户端",
        "root": os.path.join(APPDATA, "Antigravity"),
        "files": [
            ("Network/Cookies", "Network/Cookies"),
            ("Network/Cookies-journal", "Network/Cookies-journal"),
            ("SharedStorage", "SharedStorage"),
            ("SharedStorage-wal", "SharedStorage-wal")
        ],
        "dirs": [
            ("Local Storage", "Local Storage"),
            ("Session Storage", "Session Storage")
        ]
    },
    "ide": {
        "name": "Antigravity IDE 插件",
        "root": os.path.join(APPDATA, "Antigravity IDE"),
        "files": [
            ("Network/Cookies", "Network/Cookies"),
            ("Network/Cookies-journal", "Network/Cookies-journal"),
            ("SharedStorage", "SharedStorage"),
            ("SharedStorage-wal", "SharedStorage-wal")
        ],
        "dirs": [
            ("Local Storage", "Local Storage"),
            ("Session Storage", "Session Storage")
        ]
    },
    "browser": {
        "name": "内置浏览器工具型 Profile",
        "root": os.path.join(USER_HOME, ".gemini", "antigravity-browser-profile", "Default"),
        "files": [
            ("Network/Cookies", "Network/Cookies"),
            ("Network/Cookies-journal", "Network/Cookies-journal")
        ],
        "dirs": [
            ("Local Storage", "Local Storage")
        ]
    }
}

# Paths for switcher tool data
if getattr(sys, 'frozen', False):
    SWITCHER_DIR = os.path.dirname(sys.executable)
else:
    SWITCHER_DIR = os.path.dirname(os.path.abspath(__file__))

PROFILES_DIR = os.path.join(USER_HOME, ".gemini", "account_profiles")
os.makedirs(PROFILES_DIR, exist_ok=True)
CONFIG_PATH = os.path.join(PROFILES_DIR, "config.json")

# Migration logic: move old config from executable dir to persistent dir
old_config = os.path.join(SWITCHER_DIR, "config.json")
if not os.path.exists(CONFIG_PATH) and os.path.exists(old_config):
    try:
        import shutil
        shutil.copy2(old_config, CONFIG_PATH)
    except Exception:
        pass

# Executable paths to launch
ANTIGRAVITY_EXE = os.path.join(LOCALAPPDATA, "Programs", "antigravity", "Antigravity.exe")

# Windows Credentials Manager structure definitions
class CREDENTIALW(ctypes.Structure):
    _fields_ = [
        ("Flags", wintypes.DWORD),
        ("Type", wintypes.DWORD),
        ("TargetName", wintypes.LPWSTR),
        ("Comment", wintypes.LPWSTR),
        ("LastWritten", wintypes.FILETIME),
        ("CredentialBlobSize", wintypes.DWORD),
        ("CredentialBlob", ctypes.c_void_p),
        ("Persist", wintypes.DWORD),
        ("AttributeCount", wintypes.DWORD),
        ("Attributes", ctypes.c_void_p),
        ("TargetAlias", wintypes.LPWSTR),
        ("UserName", wintypes.LPWSTR),
    ]

try:
    advapi32 = ctypes.windll.advapi32
    advapi32.CredReadW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, ctypes.POINTER(ctypes.POINTER(CREDENTIALW))]
    advapi32.CredReadW.restype = wintypes.BOOL

    advapi32.CredWriteW.argtypes = [ctypes.POINTER(CREDENTIALW), wintypes.DWORD]
    advapi32.CredWriteW.restype = wintypes.BOOL

    advapi32.CredDeleteW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD]
    advapi32.CredDeleteW.restype = wintypes.BOOL

    advapi32.CredFree.argtypes = [ctypes.c_void_p]
except Exception as e:
    advapi32 = None
    print(f"Failed to load advapi32: {e}")

def read_windows_credential(target):
    if not advapi32:
        return None
    pcred = ctypes.POINTER(CREDENTIALW)()
    if advapi32.CredReadW(target, 1, 0, ctypes.byref(pcred)):
        try:
            cred = pcred.contents
            blob_data = ctypes.string_at(cred.CredentialBlob, cred.CredentialBlobSize)
            return cred.UserName, blob_data
        finally:
            advapi32.CredFree(pcred)
    return None

def write_windows_credential(target, username, blob_data):
    if not advapi32:
        return False
    cred = CREDENTIALW()
    cred.Flags = 0
    cred.Type = 1  # CRED_TYPE_GENERIC
    cred.TargetName = target
    cred.Comment = None
    cred.Persist = 2  # CRED_PERSIST_LOCAL_MACHINE
    cred.UserName = username
    cred.CredentialBlobSize = len(blob_data)
    cred.CredentialBlob = ctypes.cast(ctypes.c_char_p(blob_data), ctypes.c_void_p)
    cred.AttributeCount = 0
    cred.Attributes = None
    cred.TargetAlias = None
    return advapi32.CredWriteW(ctypes.byref(cred), 0)

def delete_windows_credential(target):
    if not advapi32:
        return False
    return advapi32.CredDeleteW(target, 1, 0)

def fetch_google_user_info(access_token):
    """Fetches user email and name from Google UserInfo API using access_token."""
    try:
        req = urllib.request.Request(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Failed to fetch userinfo: {e}")
        return None

def get_active_google_token_info():
    """Reads windows credentials and extracts active Google access token."""
    res = read_windows_credential("gemini:antigravity")
    if not res:
        return None
    username, blob = res
    try:
        cred_json = json.loads(blob.decode('utf-8'))
        access_token = cred_json.get("token", {}).get("access_token")
        return access_token
    except Exception as e:
        print(f"Error parsing active credential: {e}")
        return None

def get_valid_active_access_token():
    """Reads windows credentials, checks if access token is expired, refreshes it if needed, and returns it."""
    import datetime
    res = read_windows_credential("gemini:antigravity")
    if not res:
        return None
    username, blob = res
    try:
        cred_json = json.loads(blob.decode('utf-8'))
        token_info = cred_json.get("token", {})
        access_token = token_info.get("access_token")
        refresh_token = token_info.get("refresh_token")
        expiry_str = token_info.get("expiry")
        
        is_expired = False
        if expiry_str:
            try:
                expiry_time = datetime.datetime.fromisoformat(expiry_str)
                now = datetime.datetime.now(datetime.timezone.utc).astimezone()
                if expiry_time <= now + datetime.timedelta(minutes=5):
                    is_expired = True
            except Exception:
                is_expired = True
        else:
            is_expired = True
            
        if is_expired and refresh_token:
            log("主账号凭据已过期或即将过期，正在尝试静默刷新...", "system")
            refresh_res = refresh_oauth_token(refresh_token)
            new_access = refresh_res.get("access_token")
            expires_in = refresh_res.get("expires_in", 3599)
            if new_access:
                now = datetime.datetime.now(datetime.timezone.utc).astimezone()
                expiry_time = now + datetime.timedelta(seconds=expires_in)
                new_expiry = expiry_time.isoformat()
                
                config = load_config()
                active_profile = config.get("active_profile", "")
                if active_profile:
                    update_profile_credentials(active_profile, new_access, new_expiry)
                else:
                    token_info["access_token"] = new_access
                    token_info["expiry"] = new_expiry
                    new_blob_data = json.dumps(cred_json).encode('utf-8')
                    write_windows_credential("gemini:antigravity", username, new_blob_data)
                
                access_token = new_access
                log("已成功刷新 Google 授权凭据并同步。", "info")
            else:
                log("自动刷新 Google 凭据失败。", "error")
                
        return access_token
    except Exception as e:
        log(f"读取或刷新活动凭据时发生错误: {e}", "error")
        return None

# --- Global Log Callback ---
log_callback = None

def set_log_callback(callback):
    global log_callback
    log_callback = callback

def log(message, level="info"):
    if log_callback:
        log_callback(message, level)
    else:
        print(f"[{level.upper()}] {message}")

# --- Config Management ---
config = {"active_profile": "", "profiles": {}}

def load_config():
    global config
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except Exception as e:
            log(f"Error loading config: {e}", "error")
    else:
        config = {
            "active_profile": "",
            "profiles": {}
        }
        save_config()
    return config

def save_config(new_config=None):
    global config
    if new_config is not None:
        config = new_config
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    except Exception as e:
        log(f"Error saving config: {e}", "error")

# --- Process Helpers ---
TH32CS_SNAPPROCESS = 0x00000002
class PROCESSENTRY32(ctypes.Structure):
    _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD), ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.POINTER(wintypes.ULONG)), ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD), ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", wintypes.LONG), ("dwFlags", wintypes.DWORD), ("szExeFile", ctypes.c_char * 260)]

def is_antigravity_running():
    try:
        kernel32 = ctypes.windll.kernel32
        hProcessSnap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
        if hProcessSnap == -1:
            return False
            
        pe32 = PROCESSENTRY32()
        pe32.dwSize = ctypes.sizeof(PROCESSENTRY32)
        
        if not kernel32.Process32First(hProcessSnap, ctypes.byref(pe32)):
            kernel32.CloseHandle(hProcessSnap)
            return False
            
        running = False
        while True:
            if pe32.szExeFile.decode('utf-8', errors='ignore').lower() == "antigravity.exe":
                running = True
                break
            if not kernel32.Process32Next(hProcessSnap, ctypes.byref(pe32)):
                break
                
        kernel32.CloseHandle(hProcessSnap)
        return running
    except Exception:
        return False

def kill_processes():
    log("正在关闭 Antigravity 客户端及后台语言服务...", "system")
    subprocess.run("taskkill /f /im Antigravity.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run("taskkill /f /im language_server.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run("taskkill /f /im cef_server.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Poll and wait for processes to exit (up to 5 seconds)
    for _ in range(10):
        if not is_antigravity_running():
            break
        time.sleep(0.5)
        
    time.sleep(0.5)  # Safe margin for OS file lock release
    log("相关客户端进程已强制结束，会话数据库 file locks已释放。", "info")

def launch_app():
    if os.path.exists(ANTIGRAVITY_EXE):
        log("正在尝试启动 Antigravity 客户端...", "system")
        try:
            subprocess.Popen([ANTIGRAVITY_EXE], shell=True)
            log("客户端启动指令发送成功。", "info")
            return True
        except Exception as e:
            log(f"启动失败: {e}", "error")
            return False
    else:
        log("警告: 未在默认安装路径找到 Antigravity 客户端，请手动启动。", "warn")
        return False

# --- File Ops (Retry logic for locks) ---
def retry_action(func, *args, retries=5, delay=0.5):
    for i in range(retries):
        try:
            return func(*args)
        except Exception as e:
            if i == retries - 1:
                raise e
            time.sleep(delay)

def backup_to_profile(profile_name):
    profile_dir = os.path.join(PROFILES_DIR, profile_name)
    os.makedirs(profile_dir, exist_ok=True)
    
    log(f"开始备份当前会话凭据到配置 [{profile_name}]...", "system")
    backed_up_components = []

    for key, cfg in SOURCES.items():
        src_root = cfg["root"]
        if not os.path.exists(src_root):
            continue
        
        profile_app_dir = os.path.join(profile_dir, key)
        os.makedirs(profile_app_dir, exist_ok=True)
        
        # Copy files
        for rel_src, rel_dst in cfg["files"]:
            src_file = os.path.join(src_root, rel_src)
            if os.path.exists(src_file):
                dst_file = os.path.join(profile_app_dir, rel_dst)
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                
                def copy_f(sf=src_file, df=dst_file):
                    if os.path.exists(df):
                        os.remove(df)
                    shutil.copy2(sf, df)
                
                retry_action(copy_f)
        
        # Copy directories
        for rel_src, rel_dst in cfg["dirs"]:
            src_dir = os.path.join(src_root, rel_src)
            if os.path.exists(src_dir):
                dst_dir = os.path.join(profile_app_dir, rel_dst)
                
                def copy_d(sd=src_dir, dd=dst_dir):
                    if os.path.exists(dd):
                        shutil.rmtree(dd)
                    shutil.copytree(sd, dd)
                
                retry_action(copy_d)
        
        backed_up_components.append(cfg["name"])
        
    # Backup the Windows Credential Manager generic credential if exists
    try:
        res = read_windows_credential("gemini:antigravity")
        if res:
            username, blob = res
            cred_file = os.path.join(profile_dir, "win_cred.json")
            with open(cred_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "username": username,
                    "blob_hex": blob.hex()
                }, f, indent=2)
            log("成功备份 Windows 凭据管理器中的 Google 授权凭据。", "info")
            backed_up_components.append("Windows 授权凭据")
        else:
            log("未在 Windows 凭据管理器中发现 'gemini:antigravity'，跳过凭据备份。", "warn")
    except Exception as e:
        log(f"备份 Windows 凭据失败: {e}", "warn")
        
    if backed_up_components:
        log(f"成功完成备份。已同步项: {', '.join(backed_up_components)}", "info")
        return True
    else:
        log("未检测到本地有任何登录会话凭据（可能是干净的未登录状态）。", "warn")
        return False

def restore_from_profile(profile_name):
    profile_dir = os.path.join(PROFILES_DIR, profile_name)
    if not os.path.exists(profile_dir):
        log(f"还原失败: 找不到配置文件夹 {profile_dir}", "error")
        return False
    
    log(f"开始加载配置 [{profile_name}] 的会话凭据...", "system")
    restored_components = []

    for key, cfg in SOURCES.items():
        dst_root = cfg["root"]
        profile_app_dir = os.path.join(profile_dir, key)
        if not os.path.exists(profile_app_dir):
            continue
        
        os.makedirs(dst_root, exist_ok=True)
        
        # Copy files back
        for rel_src, rel_dst in cfg["files"]:
            src_file = os.path.join(profile_app_dir, rel_src)
            if os.path.exists(src_file):
                dst_file = os.path.join(dst_root, rel_dst)
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                
                def copy_f(sf=src_file, df=dst_file):
                    if os.path.exists(df):
                        os.remove(df)
                    shutil.copy2(sf, df)
                
                retry_action(copy_f)
        
        # Copy directories back
        for rel_src, rel_dst in cfg["dirs"]:
            src_dir = os.path.join(profile_app_dir, rel_src)
            if os.path.exists(src_dir):
                dst_dir = os.path.join(dst_root, rel_dst)
                
                def copy_d(sd=src_dir, dd=dst_dir):
                    if os.path.exists(dd):
                        shutil.rmtree(dd)
                    shutil.copytree(sd, dd)
                
                retry_action(copy_d)
        
        restored_components.append(cfg["name"])
        
    # Restore the Windows Credential Manager generic credential
    cred_file = os.path.join(profile_dir, "win_cred.json")
    if os.path.exists(cred_file):
        try:
            with open(cred_file, 'r', encoding='utf-8') as f:
                cred_data = json.load(f)
            username = cred_data["username"]
            blob_data = bytes.fromhex(cred_data["blob_hex"])
            if write_windows_credential("gemini:antigravity", username, blob_data):
                log("成功还原 Windows 凭据管理器中的 Google 授权凭据。", "info")
                restored_components.append("Windows 授权凭据")
            else:
                log("还原 Windows 凭据失败：写入 Credential Manager 返回 False。", "error")
        except Exception as e:
            log(f"还原 Windows 凭据失败: {e}", "error")
    else:
        # If no backup, delete the active credential so it doesn't leak/pollute
        try:
            delete_windows_credential("gemini:antigravity")
            log("未发现凭据备份，已清理当前活动的 Windows 授权凭据以防污染。", "info")
        except Exception as e:
            log(f"清理 Windows 凭据失败: {e}", "warn")
            
    log(f"还原成功。已载入并覆盖凭据: {', '.join(restored_components)}", "info")
    return True

def clear_active_session():
    log("正在彻底清理当前的本地会话缓存与 Cookie...", "system")
    failed_deletions = []
    
    for key, cfg in SOURCES.items():
        root_dir = cfg["root"]
        if not os.path.exists(root_dir):
            continue
        
        # Delete cookies & other session files
        for rel_src, _ in cfg["files"]:
            f_path = os.path.join(root_dir, rel_src)
            if os.path.exists(f_path):
                def rm_f(p=f_path):
                    os.remove(p)
                try:
                    retry_action(rm_f)
                except Exception as e:
                    log(f"删除文件失败 {f_path}: {e}", "warn")
                    failed_deletions.append(f_path)
                    
        # Delete Local Storage & Session Storage dirs
        for rel_src, _ in cfg["dirs"]:
            d_path = os.path.join(root_dir, rel_src)
            if os.path.exists(d_path):
                def rm_d(p=d_path):
                    shutil.rmtree(p)
                try:
                    retry_action(rm_d)
                except Exception as e:
                    log(f"删除目录失败 {d_path}: {e}", "warn")
                    failed_deletions.append(d_path)
                    
    # Delete Windows Credential Manager credential
    try:
        if delete_windows_credential("gemini:antigravity"):
            log("成功清除 Windows 凭据管理器中的 Google 授权凭据 ('gemini:antigravity')。", "info")
        else:
            log("未在 Windows 凭据管理器中发现 'gemini:antigravity' 凭据，无需清除。", "info")
    except Exception as e:
        log(f"清除 Windows 凭据失败: {e}", "warn")
        failed_deletions.append("Windows Credential Manager ('gemini:antigravity')")
        
    if failed_deletions:
        log(f"部分会话文件清理失败 (共 {len(failed_deletions)} 个项目被锁定)。", "error")
    else:
        log("所有活动会话缓存清除完成。", "info")
        
    return failed_deletions

# --- Real-time Quota and OAuth Token Refreshing ---

CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "YOUR_CLIENT_ID_HERE")
CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "YOUR_CLIENT_SECRET_HERE")

def refresh_oauth_token(refresh_token):
    import urllib.parse
    import urllib.request
    url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }
    data_bytes = urllib.parse.urlencode(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data_bytes,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    with urllib.request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))

def call_cloudcode_api(url, access_token, post_data=None):
    import urllib.request
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "User-Agent": "antigravity/2.1.4"
        },
        method="POST" if post_data is not None else "GET"
    )
    data_bytes = json.dumps(post_data).encode('utf-8') if post_data is not None else None
    with urllib.request.urlopen(req, data=data_bytes, timeout=5) as response:
        return json.loads(response.read().decode('utf-8'))




def parse_reset_time(reset_time_str):
    if not reset_time_str:
        return ""
    try:
        import datetime
        t_str = reset_time_str.replace('Z', '+00:00')
        if '.' in t_str:
            parts = t_str.split('.')
            sub_parts = parts[1].split('+')
            frac = sub_parts[0][:6]
            t_str = parts[0] + '.' + frac + '+' + sub_parts[1]
        reset_dt = datetime.datetime.fromisoformat(t_str)
        now_dt = datetime.datetime.now(datetime.timezone.utc).astimezone(reset_dt.tzinfo)
        
        if reset_dt <= now_dt:
            return ""
            
        delta = reset_dt - now_dt
        hours = delta.total_seconds() / 3600.0
        
        if hours >= 24:
            days = round(hours / 24)
            days = max(1, days)
            return f"{days}day"
        else:
            h = round(hours)
            h = max(1, h)
            return f"{h}h"
    except Exception:
        return ""



def fetch_real_quota_data(refresh_token, access_token):
    import urllib.error
    import datetime
    from concurrent.futures import ThreadPoolExecutor
    
    new_access = None
    new_expiry = None
    
    def fetch_apis(token):
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_tier = executor.submit(call_cloudcode_api, "https://daily-cloudcode-pa.googleapis.com/v1internal:loadCodeAssist", token, {})
            future_models = executor.submit(call_cloudcode_api, "https://daily-cloudcode-pa.googleapis.com/v1internal:fetchAvailableModels", token, {})
            return future_tier.result(), future_models.result()
    
    try:
        tier_res, models_res = fetch_apis(access_token)
    except urllib.error.HTTPError as e:
        if e.code == 401 and refresh_token:
            # Refresh token and retry
            refresh_res = refresh_oauth_token(refresh_token)
            new_access = refresh_res.get("access_token")
            expires_in = refresh_res.get("expires_in", 3599)
            if new_access:
                # Calculate new expiry string in local timezone format
                now = datetime.datetime.now(datetime.timezone.utc).astimezone()
                expiry_time = now + datetime.timedelta(seconds=expires_in)
                new_expiry = expiry_time.isoformat()
                
                # Retry with new access token
                tier_res, models_res = fetch_apis(new_access)
            else:
                raise e
        else:
            raise e

    # Parse Tier Name directly from API response
    paid_tier_info = tier_res.get("paidTier", {})
    tier_name = paid_tier_info.get("name")
    if not tier_name:
        current_tier_info = tier_res.get("currentTier", {})
        tier_name = current_tier_info.get("name")
        if not tier_name or tier_name == "Antigravity":
            tier_name = current_tier_info.get("id", "Free")
            
    if tier_name == "free-tier":
        tier_name = "Free"
    
    # Parse Quota Remaining Percent & Reset Time
    gemini_min_rem = None
    gemini_reset = None
    
    claude_min_rem = None
    claude_reset = None
    
    models = models_res.get("models", {})
    
    for m_id, m_data in models.items():
        quota = m_data.get("quotaInfo", {})
        rem = quota.get("remainingFraction")
        if rem is None and "resetTime" in quota:
            rem = 0.0
            
        if rem is not None:
            m_id_lower = m_id.lower()
            if m_id_lower.startswith(('claude-', 'gpt-')):
                if claude_min_rem is None or rem < claude_min_rem:
                    claude_min_rem = rem
                    claude_reset = quota.get("resetTime")
            elif m_id_lower.startswith(('gemini-', 'google-')) or m_data.get('modelProvider') == 'MODEL_PROVIDER_GOOGLE':
                if rem < 1.0 or gemini_min_rem is None:
                    if gemini_min_rem is None or rem < gemini_min_rem:
                        gemini_min_rem = rem
                        gemini_reset = quota.get("resetTime")
            else:
                if gemini_min_rem is None or rem < gemini_min_rem:
                    gemini_min_rem = rem
                    gemini_reset = quota.get("resetTime")
                    
    gemini_reset_str = parse_reset_time(gemini_reset)
    claude_reset_str = parse_reset_time(claude_reset)
        
    return tier_name, gemini_min_rem, gemini_reset_str, claude_min_rem, claude_reset_str, new_access, new_expiry


def update_profile_credentials(profile_name, new_access_token, new_expiry):
    profile_dir = os.path.join(PROFILES_DIR, profile_name)
    cred_file = os.path.join(profile_dir, "win_cred.json")
    if os.path.exists(cred_file):
        try:
            with open(cred_file, 'r', encoding='utf-8') as f:
                cred_data = json.load(f)
            
            username = cred_data["username"]
            blob_data = bytes.fromhex(cred_data["blob_hex"])
            inner_json = json.loads(blob_data.decode('utf-8'))
            
            inner_json["token"]["access_token"] = new_access_token
            if new_expiry:
                inner_json["token"]["expiry"] = new_expiry
                
            new_blob_data = json.dumps(inner_json).encode('utf-8')
            cred_data["blob_hex"] = new_blob_data.hex()
            
            with open(cred_file, 'w', encoding='utf-8') as f:
                json.dump(cred_data, f, indent=2)
                
            log(f"已更新本地配置文件中的授权凭据 [{profile_name}]。", "info")
            
            # If this is the active profile, synchronize it to Windows Credentials Manager
            active_config = load_config()
            if active_config.get("active_profile", "") == profile_name:
                if write_windows_credential("gemini:antigravity", username, new_blob_data):
                    log("已同步更新 Windows 凭据管理器中的 Google 授权凭据。", "info")
                else:
                    log("同步更新 Windows 凭据管理器失败。", "error")
        except Exception as e:
            log(f"更新凭据文件时出错 [{profile_name}]: {e}", "warn")
