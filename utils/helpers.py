import os
import sys
from typing import List, Any, Dict

class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(title: str, width: int = 70):
    print("\n" + Color.BOLD + Color.PURPLE + "=" * width)
    print(f" {title.center(width - 2)}")
    print("=" * width + Color.END)

def print_success(msg: str):
    print(f"{Color.GREEN}✔ {msg}{Color.END}")

def print_error(msg: str):
    print(f"{Color.RED}✖ Error: {msg}{Color.END}")

def print_info(msg: str):
    print(f"{Color.CYAN}ℹ {msg}{Color.END}")

def print_warning(msg: str):
    print(f"{Color.YELLOW}⚠️ Warning: {msg}{Color.END}")

def format_table(headers: List[str], rows: List[List[Any]]) -> str:
    """Formats list of headers and rows into a clean ASCII table."""
    if not rows:
        return f"{Color.YELLOW}No records found.{Color.END}"

    str_rows = [[str(cell) if cell is not None else "" for cell in row] for row in rows]
    col_widths = [len(str(h)) for h in headers]
    for row in str_rows:
        for idx, cell in enumerate(row):
            if idx < len(col_widths):
                col_widths[idx] = max(col_widths[idx], len(cell))

    separator = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    header_row = "|" + "|".join(f" {headers[i].ljust(col_widths[i])} " for i in range(len(headers))) + "|"

    output = [separator, header_row, separator]
    for row in str_rows:
        row_str = "|" + "|".join(f" {row[i].ljust(col_widths[i])} " if i < len(row) else f" {''.ljust(col_widths[i])} " for i in range(len(headers))) + "|"
        output.append(row_str)
    output.append(separator)

    return "\n".join(output)

def calculate_grade(marks_obtained: float, total_marks: float = 100.0) -> tuple:
    """Calculates percentage and grade based on marks obtained."""
    percentage = (marks_obtained / total_marks) * 100.0 if total_marks > 0 else 0.0
    if percentage >= 90.0:
        return percentage, "A+"
    elif percentage >= 80.0:
        return percentage, "A"
    elif percentage >= 70.0:
        return percentage, "B+"
    elif percentage >= 60.0:
        return percentage, "B"
    elif percentage >= 50.0:
        return percentage, "C"
    elif percentage >= 40.0:
        return percentage, "D"
    else:
        return percentage, "F"
