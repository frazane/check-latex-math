import sys
import re
from pathlib import Path
from pylatexenc.latexwalker import LatexWalker, LatexWalkerParseError

def find_files(directories: list[Path], file_patterns: list[str]) -> list[Path]:
    matches = []
    for directory in directories:
        for pattern in file_patterns:
            matches.extend(Path(directory).rglob(pattern))
    return matches

def extract_latex_math(content: str) -> list[str]:
    patterns = [
        r'\$\$(.*?)\$\$',     # $$...$$ (block-level LaTeX)
        r'\$(.*?)\$',         # $...$ (inline LaTeX)
        r'\\\[(.*?)\\\]',     # \[...\] (display math)
        r'\\\((.*?)\\\)'      # \(...\) (inline math)
    ]
    latex_math = []
    for pattern in patterns:
        latex_math.extend(re.findall(pattern, content, re.DOTALL))
    return latex_math

def validate_latex(latex_expr: str) -> bool:
    """
    Validate LaTeX expressions using pylatexenc.
    """
    try:
        lw = LatexWalker(latex_expr, tolerant_parsing=False)
        lw.get_latex_nodes()
        return True
    except LatexWalkerParseError as e:
        return False
    except Exception as e:
        return False


def separate_dir_patterns(args: list[str]) -> tuple[list[str], list[str]]:
    """
    Separate directories and file patterns from command line arguments.
    """
    directories = []
    file_patterns = []
    
    for arg in args:
        if Path(arg).is_dir():
            directories.append(arg)
        else:
            file_patterns.append(arg)
    
    return directories, file_patterns


def main():
    """
    Main function to check directories for specified file types and validate LaTeX math.
    """
    args = sys.argv[1:]
    directories, file_patterns = separate_dir_patterns(args)
    all_files = find_files(directories, file_patterns)
    
    for file_path in all_files:
        with file_path.open('r') as file:
            content = file.read()
            latex_expressions = extract_latex_math(content)
            for expr in latex_expressions:
                if not validate_latex(expr):
                    raise Exception(
                        "Invalid LaTeX math expression detected in file: "
                        f"{file_path}: \n \n {expr} \n"
                    )