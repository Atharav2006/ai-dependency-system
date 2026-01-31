import importlib
import sys
import os

modules_to_test = [
    'app.main',
    'app.routes.sessions',
    'app.routes.analytics',
    'app.routes.gamification'
]

sys.path.append(os.getcwd())

for module_name in modules_to_test:
    try:
        print(f"Testing {module_name}...")
        importlib.import_module(module_name)
        print(f"Successfully imported {module_name}")
    except IndentationError as e:
        print(f"IndentationError in {module_name}: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"Error in {module_name}: {e}")
        import traceback
        traceback.print_exc()
