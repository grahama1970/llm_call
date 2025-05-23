import os
import sys
from pathlib import Path
import importlib.util
from dotenv import load_dotenv

# --- Configuration for the Check Script ---
PROJECT_ROOT = Path(__file__).parent.resolve()
SRC_DIR_NAME = "src"
MAIN_PACKAGE_NAME = "llm_call" # Your main package name
EXPECTED_PYTHONPATH_TARGET = PROJECT_ROOT / SRC_DIR_NAME

# --- Logger (Simple for this utility) ---
def log_info(message):
    print(f"[INFO] {message}")

def log_warning(message):
    print(f"\033[93m[WARNING] {message}\033[0m") # Yellow

def log_error(message):
    print(f"\033[91m[ERROR] {message}\033[0m") # Red

def log_success(message):
    print(f"\033[92m[SUCCESS] {message}\033[0m") # Green

# --- Check Functions ---

def check_pythonpath_and_dotenv():
    log_info("Checking PYTHONPATH and .env setup...")
    dotenv_path = PROJECT_ROOT / '.env'
    pythonpath_from_env_file = None
    pythonpath_from_os_environ = os.environ.get('PYTHONPATH')

    if dotenv_path.is_file():
        log_info(f".env file found at: {dotenv_path}")
        # Temporarily load .env to see what it would set PYTHONPATH to
        # Create a dummy environment to load .env into to avoid polluting current os.environ
        original_environ = os.environ.copy()
        try:
            # Use python-dotenv to parse the .env file content for PYTHONPATH
            # This doesn't actually set os.environ if we just read it.
            # A bit more manual parsing is needed here for safety or use dotenv.dotenv_values
            env_values = load_dotenv(dotenv_path=dotenv_path, override=False, verbose=False) # Don't override, just load for check
            if env_values: # load_dotenv returns True if a .env was loaded, False otherwise
                 # Re-check os.environ AFTER load_dotenv has had a chance (it modifies os.environ in place)
                pythonpath_from_env_file = os.environ.get('PYTHONPATH_DOTENV_CHECK', os.environ.get('PYTHONPATH'))
                # To properly check what dotenv *would* set, without actually setting it globally for this script:
                from dotenv import dotenv_values
                env_vars_from_file = dotenv_values(dotenv_path)
                pythonpath_from_env_file = env_vars_from_file.get('PYTHONPATH')

            if pythonpath_from_env_file:
                log_info(f"PYTHONPATH defined in .env: '{pythonpath_from_env_file}'")
                resolved_path_from_env = Path(pythonpath_from_env_file.split(os.pathsep)[0]).resolve() # Take first path if multiple
                if resolved_path_from_env == EXPECTED_PYTHONPATH_TARGET.resolve():
                    log_success(f"PYTHONPATH in .env correctly points to your project's '{SRC_DIR_NAME}' directory.")
                else:
                    log_error(f"PYTHONPATH in .env ('{resolved_path_from_env}') does NOT correctly point to expected '{EXPECTED_PYTHONPATH_TARGET.resolve()}'.")
            else:
                log_warning("PYTHONPATH is not defined in your .env file.")
        finally:
            os.environ.clear()
            os.environ.update(original_environ) # Restore original environment
    else:
        log_warning(".env file not found at project root. PYTHONPATH check via .env skipped.")

    if pythonpath_from_os_environ:
        log_info(f"Current process os.environ['PYTHONPATH']: '{pythonpath_from_os_environ}'")
        # This one is tricky as it could be set by many things (shell, wrapper scripts)
    else:
        log_info("os.environ['PYTHONPATH'] is not set in the current process (before script-specific modifications).")

    log_info(f"Current sys.path (first few entries relevant to project):")
    found_src_in_sys_path = False
    for i, p_item in enumerate(sys.path):
        try:
            resolved_p_item = Path(p_item).resolve()
            if i < 5 or EXPECTED_PYTHONPATH_TARGET.resolve() in resolved_p_item.parents or EXPECTED_PYTHONPATH_TARGET.resolve() == resolved_p_item :
                print(f"  sys.path[{i}]: {resolved_p_item}")
            if resolved_p_item == EXPECTED_PYTHONPATH_TARGET.resolve():
                found_src_in_sys_path = True
        except: # Handle non-path strings if any
            if i < 5: print(f"  sys.path[{i}]: {p_item} (could not resolve as path)")


    if found_src_in_sys_path:
        log_success(f"Expected src path '{EXPECTED_PYTHONPATH_TARGET.resolve()}' IS in sys.path.")
    else:
        log_error(f"Expected src path '{EXPECTED_PYTHONPATH_TARGET.resolve()}' IS NOT in sys.path. This will likely cause import errors for '{MAIN_PACKAGE_NAME}'.")
        log_info("Consider running 'uv pip install -e .' or setting PYTHONPATH correctly for your execution environment.")


def check_init_files(start_path: Path, package_prefix=""):
    """Recursively checks for __init__.py files in directories that look like packages."""
    items = list(start_path.iterdir())
    has_py_files = any(item.is_file() and item.suffix == '.py' for item in items)
    sub_packages_correct = True

    for item in items:
        if item.is_dir():
            # Heuristic: if a directory contains .py files or other subdirectories with .py files,
            # it's likely intended to be a package or namespace package.
            # For simplicity, we'll assume any subdir under a package root that isn't special (like __pycache__)
            # and contains python files or further subdirs should be a package.
            if item.name.startswith('.') or item.name == '__pycache__':
                continue

            # Check if this subdirectory itself likely contains Python code
            # This is a heuristic to decide if an __init__.py is "expected"
            subdir_has_py_files_or_subpackages = any(f.suffix == '.py' for f in item.glob('**/*'))

            init_py_path = item / "__init__.py"
            current_package_name = f"{package_prefix}{item.name}"

            if subdir_has_py_files_or_subpackages: # Only expect __init__.py if it looks like it holds Python code
                if not init_py_path.is_file():
                    log_error(f"Missing __init__.py: Directory '{item}' appears to be a package/subpackage ('{current_package_name}') but lacks an __init__.py file.")
                    sub_packages_correct = False
                else:
                    log_info(f"Found __init__.py in package/subpackage: '{item}' (as '{current_package_name}')")
                
                # Recursively check subdirectories
                if not check_init_files(item, package_prefix=f"{current_package_name}."):
                    sub_packages_correct = False
            elif init_py_path.is_file(): # Has __init__.py but no other .py files/subpackages
                 log_info(f"Found __init__.py in namespace-like package: '{item}' (as '{current_package_name}')")


    if package_prefix == "" and has_py_files and not (start_path / "__init__.py").is_file():
        # Special check for the main package directory itself under src
        log_error(f"Missing __init__.py: Main package directory '{start_path}' lacks an __init__.py file.")
        return False
        
    return sub_packages_correct

def check_name_collisions(package_path: Path, base_package_name: str):
    """Checks for .py files that have the same name as subdirectories (potential packages) within the same scope."""
    log_info(f"Checking for name collisions in '{package_path}' and its subdirectories...")
    collisions_found = False
    for root, dirs, files in os.walk(package_path):
        current_path = Path(root)
        # Create a set of subdirectory names (potential subpackage names)
        dir_names_set = {d for d in dirs if not d.startswith('.') and d != '__pycache__'}
        
        for file_name in files:
            if file_name.endswith(".py"):
                module_name_without_ext = file_name[:-3]
                if module_name_without_ext in dir_names_set:
                    log_error(f"Name Collision: Module '{current_path / file_name}' has the same name as subdirectory '{current_path / module_name_without_ext}'. This can cause import issues.")
                    collisions_found = True
    
    if not collisions_found:
        log_success("No obvious name collisions found between .py files and package directories.")
    return not collisions_found

# --- Main Execution ---
if __name__ == "__main__":
    log_info(f"--- Project Setup Check for '{MAIN_PACKAGE_NAME}' in '{PROJECT_ROOT}' ---")

    # 1. Check PYTHONPATH and sys.path (relative to where this script is run)
    # For this check to be most effective, run this script from the project root.
    # Temporarily add src to sys.path for the duration of this script if not already there,
    # to simulate how an editable install or correct PYTHONPATH would work for subsequent checks.
    src_dir_abs = EXPECTED_PYTHONPATH_TARGET.resolve()
    original_sys_path = list(sys.path)
    if str(src_dir_abs) not in [str(Path(p).resolve()) for p in sys.path]:
        sys.path.insert(0, str(src_dir_abs))
        log_warning(f"Temporarily added '{src_dir_abs}' to sys.path for checks.")
    
    check_pythonpath_and_dotenv()
    print("-" * 50)

    # 2. Check for __init__.py files
    main_package_path = EXPECTED_PYTHONPATH_TARGET / MAIN_PACKAGE_NAME
    if main_package_path.is_dir():
        log_info(f"Checking for __init__.py files starting from '{main_package_path}'...")
        all_inits_ok = check_init_files(main_package_path, package_prefix=f"{MAIN_PACKAGE_NAME}.")
        if all_inits_ok:
            log_success(f"Basic __init__.py structure for package '{MAIN_PACKAGE_NAME}' seems reasonable.")
        else:
            log_error(f"Potential issues found with __init__.py files for package '{MAIN_PACKAGE_NAME}'.")
    else:
        log_error(f"Main package directory '{main_package_path}' not found!")
    print("-" * 50)

    # 3. Check for name collisions (e.g. module_name.py and module_name/ directory)
    if main_package_path.is_dir():
        check_name_collisions(main_package_path, MAIN_PACKAGE_NAME)
    print("-" * 50)

    # 4. Attempt to import the main package
    log_info(f"Attempting to import main package: '{MAIN_PACKAGE_NAME}'...")
    try:
        # This relies on sys.path being correctly set up by now (either by env or editable install)
        # or by the temporary add at the start of this __main__ block.
        imported_package = importlib.import_module(MAIN_PACKAGE_NAME)
        log_success(f"Successfully imported main package '{MAIN_PACKAGE_NAME}'.")
        log_info(f"Found at: {getattr(imported_package, '__file__', 'N/A')}")
        log_info(f"Package path(s): {getattr(imported_package, '__path__', 'N/A')}")
    except ModuleNotFoundError:
        log_error(f"Failed to import main package '{MAIN_PACKAGE_NAME}'. ModuleNotFoundError.")
        log_info("Ensure your project is installed (e.g., `uv pip install -e .`) or PYTHONPATH is set correctly.")
    except ImportError as e:
        log_error(f"Failed to import main package '{MAIN_PACKAGE_NAME}'. ImportError: {e}")
        log_info("This might indicate an issue within an __init__.py file of the package itself.")
    except Exception as e:
        log_error(f"An unexpected error occurred while trying to import '{MAIN_PACKAGE_NAME}': {e}")

    # Restore original sys.path if it was modified
    sys.path = original_sys_path
    if str(src_dir_abs) == sys.path[0] and str(src_dir_abs) not in [str(Path(p).resolve()) for p in original_sys_path]: # check if we actually added it
        log_info(f"Restored original sys.path.")

    log_info("--- Check Complete ---")