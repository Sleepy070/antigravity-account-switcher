import os

def patch():
    with open('switcher.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    target = """SWITCHER_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SWITCHER_DIR, "config.json")
PROFILES_DIR = os.path.join(USER_HOME, ".gemini", "account_profiles")"""

    replacement = """if getattr(sys, 'frozen', False):
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
        pass"""
        
    new_content = content.replace(target, replacement)
    
    with open('switcher.py', 'w', encoding='utf-8') as f:
        f.write(new_content)

if __name__ == '__main__':
    patch()
