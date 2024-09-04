import sys
import re
from pathlib import Path
from pylatexenc.latexwalker import LatexWalker, LatexWalkerParseError


# Comprehensive list of known LaTeX math macros
KNOWN_MATH_MACROS = {
    # Greek letters
    'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'varepsilon', 'zeta', 'eta', 'theta', 'vartheta', 'iota', 'kappa', 
    'lambda', 'mu', 'nu', 'xi', 'pi', 'varpi', 'rho', 'varrho', 'sigma', 'varsigma', 'tau', 'upsilon', 'phi', 
    'varphi', 'chi', 'psi', 'omega',
    'Gamma', 'Delta', 'Theta', 'Lambda', 'Xi', 'Pi', 'Sigma', 'Upsilon', 'Phi', 'Psi', 'Omega',

    # Binary operators
    'times', 'div', 'pm', 'mp', 'ast', 'star', 'circ', 'bullet', 'cdot', 'cap', 'cup', 'sqcap', 'sqcup',
    'vee', 'wedge', 'oplus', 'ominus', 'otimes', 'oslash', 'odot', 'uplus', 'bigcirc', 'dagger', 'ddagger',
    'amalg', 'diamond', 'bigtriangledown', 'bigtriangleup', 'triangleleft', 'triangleright', 'boxplus', 
    'boxminus', 'boxtimes', 'boxdot',

    # Binary relations
    'leq', 'le', 'geq', 'ge', 'neq', 'equiv', 'sim', 'simeq', 'approx', 'cong', 'propto', 'models', 
    'perp', 'parallel', 'asymp', 'bowtie', 'vdash', 'dashv', 'in', 'ni', 'subset', 'supset', 'subseteq', 
    'supseteq', 'sqsubset', 'sqsupset', 'sqsubseteq', 'sqsupseteq', 'smile', 'frown', 'subsetneq', 'supsetneq',
    'preceq', 'succeq', 'prec', 'succ', 'll', 'gg', 'doteq', 'equiv', 'circeq', 'approxeq',

    # Set notation
    'emptyset', 'infty', 'nabla', 'partial', 'forall', 'exists', 'neg', 'top', 'bot', 'setminus', 'mid', 
    'backslash', 'cupdot', 'capdot', 'sqcupdot', 'complement',

    # Functions
    'sin', 'cos', 'tan', 'csc', 'sec', 'cot', 'sinh', 'cosh', 'tanh', 'arcsin', 'arccos', 'arctan', 
    'ln', 'log', 'exp', 'gcd', 'lim', 'sup', 'inf', 'det', 'dim', 'arg', 'deg', 'Pr', 'min', 'max', 'limsup', 
    'liminf', 'mod', 'bmod', 'pmod',

    # Arrows
    'leftarrow', 'rightarrow', 'leftrightarrow', 'Leftarrow', 'Rightarrow', 'Leftrightarrow', 
    'uparrow', 'downarrow', 'updownarrow', 'Uparrow', 'Downarrow', 'Updownarrow', 
    'longrightarrow', 'longleftarrow', 'Longleftrightarrow', 'hookrightarrow', 'hookleftarrow', 'mapsto', 
    'leadsto', 'nearrow', 'searrow', 'nwarrow', 'swarrow', 'rightsquigarrow', 'twoheadrightarrow', 
    'leftleftarrows', 'rightrightarrows', 'leftrightharpoons', 'rightleftharpoons', 'to',

    # Delimiters
    'langle', 'rangle', 'lceil', 'rceil', 'lfloor', 'rfloor', 'lbrace', 'rbrace', 'lbrack', 'rbrack', 'vert', 'Vert',
    'left', 'right', 'big', 'Big', 'bigg', 'Bigg', 'biggl', 'Biggl', 'biggr', 'Biggr', 'Bigl', 'Bigr', 'bigl', 'bigr',

    # Miscellaneous symbols
    'infty', 'nabla', 'partial', 'imath', 'jmath', 'ell', 'Re', 'Im', 'wp', 'aleph', 'hbar', 'mho', 
    'Box', 'Diamond', 'angle', 'measuredangle', 'sphericalangle', 'star', 'bigstar', 'blacktriangle', 
    'blacksquare', 'triangledown', 'triangle', 'spadesuit', 'heartsuit', 'diamondsuit', 'clubsuit',
    'flat', 'natural', 'sharp', 'checkmark', 'lightning', 'topbot', 'circledast', 'circledcirc', 'circleddash',

    # Accents
    'hat', 'tilde', 'bar', 'vec', 'dot', 'ddot', 'overline', 'underline', 'widehat', 'widetilde', 'acute', 'grave',
    'breve', 'check', 'overbrace', 'underbrace',

    # Fractions and roots
    'frac', 'sqrt', 'over', 'dfrac', 'tfrac', 'binom', 'cfrac', 'tbinom', 'dbinom',

    # Scripts
    'mathcal', 'mathbb', 'mathbf', 'mathfrak', 'mathsf', 'mathtt', 'mathit', 'mathscr', 'boldsymbol',
    'mathrm', 'mathnormal', 'mathbold', 'mathboldsymbol', 'mathbolditalic', 'mathboldscr', 'mathboldfrak',

    # Sum, Product, Limits
    'sum', 'prod', 'bigcup', 'bigcap', 'int', 'oint', 'bigoplus', 'bigotimes', 'bigwedge', 'bigvee', 
    'bigsqcup', 'coprod', 'bigodot', 'biguplus',

    # Brackets and spacing
    'left', 'right', 'big', 'Big', 'bigg', 'Bigg', 'quad', 'qquad', 'hspace', 'vspace', 'negmedspace', 'negthickspace', 
    'hfill', 'vfill', 'phantom', 'mathstrut', 'noalign', 'vphantom', 'hphantom', 'smash',

    # Text styles
    'textstyle', 'displaystyle', 'scriptstyle', 'scriptscriptstyle',

    # Dots
    'dots', 'cdots', 'vdots', 'ddots', 'iddots', 'dotsc', 'dotsb', 'dotso', 'ldots', 'adots',
    'cdotp', 'ldotp', 'cdots', 'adots', 'iddots',

    # Operators with limits
    'lim', 'int', 'sum', 'prod', 'bigcup', 'bigcap', 'limsup', 'liminf', 'oint', 'coprod', 'varlimsup', 
    'varliminf', 'varinjlim', 'varprojlim', 'sup', 'inf',

    # Logicals and relations
    'land', 'lor', 'not', 'implies', 'iff', 'therefore', 'because', 'vdash', 'dashv', 'models', 'ni', 
    'vdots', 'ddots', 'perp', 'asymp', 'smile', 'frown', 'prec', 'succ', 'subset', 'supset', 'vdash',

    # Common mathematical sets (using mathbb)
    'R', 'C', 'Q', 'Z', 'N', 'P', 'H',

    # Miscellaneous
    'overline', 'underline', 'boxed', 'text', 'mod', 'bmod', 'pmod', 'mathstrut', 'quad', 'qquad',

}


class UnknownLatexMacroError(Exception):
    pass

class InvalidLatexExpressionError(Exception):
    pass

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
    from pylatexenc.latexwalker import LatexMacroNode
    import pdb
    

    def recurse(node):
        if isinstance(node, LatexMacroNode):
            if node.macroname in ['[', ']', '{', '}', '(', ')', '|', '||']:
                return
            if node.macroname not in KNOWN_MATH_MACROS:
                # pdb.set_trace()
                raise UnknownLatexMacroError(f"Unknown LaTeX macro: {node.macroname}")
            
            if node.nodeargd is not None:
                for child in node.nodeargd.argnlist:
                    recurse(child)

    lw = LatexWalker(latex_expr, tolerant_parsing=False)
    nodelist, _, _ = lw.get_latex_nodes()
    # pdb.set_trace()
    
    for node in nodelist:
        recurse(node)


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
                try:
                    validate_latex(expr)
                except UnknownLatexMacroError as e:
                    raise InvalidLatexExpressionError(
                        f"Invalid LaTeX expression in {file_path}: \n\n{expr}"
                    ) from e
                