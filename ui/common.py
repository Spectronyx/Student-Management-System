import getpass
from typing import List, Tuple, Any
from utils.helpers import (
    Color, print_header, print_error, print_success, print_info, print_warning
)

def prompt_input(label: str, default: str = None) -> str:
    prompt_str = f"{Color.BOLD}{label}{Color.END}"
    if default:
        prompt_str += f" [{default}]"
    prompt_str += ": "
    val = input(prompt_str).strip()
    if not val and default:
        return default
    return val

def prompt_password(label: str = "Enter Password") -> str:
    prompt_str = f"{Color.BOLD}{label}{Color.END}: "
    try:
        return getpass.getpass(prompt_str).strip()
    except Exception:
        return input(prompt_str).strip()

def prompt_int(label: str, default: int = None) -> int:
    while True:
        val = prompt_input(label, str(default) if default is not None else None)
        try:
            return int(val)
        except ValueError:
            print_error("Please enter a valid integer number.")

def prompt_float(label: str, default: float = None) -> float:
    while True:
        val = prompt_input(label, str(default) if default is not None else None)
        try:
            return float(val)
        except ValueError:
            print_error("Please enter a valid numeric value.")

def prompt_menu_choice(title: str, options: List[Tuple[str, str]]) -> str:
    """Renders a clean formatted menu list and prompts choice."""
    print_header(title)
    for key, desc in options:
        print(f"  {Color.BOLD}{Color.CYAN}[{key}]{Color.END} {desc}")
    print("-" * 70)
    choice = input(f"{Color.BOLD}Select an option: {Color.END}").strip()
    return choice
