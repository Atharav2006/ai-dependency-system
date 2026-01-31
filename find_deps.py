import os
import re

def get_imports():
    imports = set()
    for root, dirs, files in os.walk("backend/app"):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Match 'import module'
                    for match in re.finditer(r"^import (\w+)", content, re.MULTILINE):
                        imports.add(match.group(1))
                    # Match 'from module import ...'
                    for match in re.finditer(r"^from (\w+)", content, re.MULTILINE):
                        imports.add(match.group(1))
    
    # Filter out local imports
    # Local imports are 'app', 'sessions', 'analytics', etc if they are in the same dir
    # But for simplicity, let's just look for known libraries
    known_libs = ["fastapi", "uvicorn", "supabase", "dotenv", "httpx", "jwt", "cryptography", "google", "openai", "anthropic", "groq", "pydantic"]
    
    external_imports = [i for i in imports if i not in ["app", "os", "json", "re", "time", "datetime", "typing", "abc", "collections", "traceback"]]
    
    print("\n".join(sorted(external_imports)))

if __name__ == "__main__":
    get_imports()
