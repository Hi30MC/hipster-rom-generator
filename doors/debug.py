import functools
import hashlib
import re


def get_indent(depth):
    return "\u23d0 " * depth


def colored_str(name, bold=False) -> str:
    """Get a consistent 24-bit RGB color for a method name based on its hash"""
    # Generate RGB values from hash
    hash_bytes = hashlib.md5(name.encode()).digest()
    r = hash_bytes[0]
    g = hash_bytes[1]
    b = hash_bytes[2]

    # Ensure colors are bright enough to be readable
    r = max(r, 128)
    g = max(g, 128)
    b = max(b, 128)

    # 24-bit RGB color format: \033[38;2;R;G;Bm
    color = f"\033[38;2;{r};{g};{b}m"
    if bold:
        color = f"\033[1m{color}"  # Add bold

    reset = "\033[0m"
    return f"{color}{name}{reset}"


def wrap_function(fn, method_name: str):
    @functools.wraps(fn)
    def wrapper(self: SeqDebug, *args, **kwargs):
        no_indent = self._next_call_no_indent
        if no_indent:
            self._next_call_no_indent = False

        args_str = [str(arg) for arg in args] + [f"{k}={v}" for k, v in kwargs.items()]
        all_args_str = ", ".join(args_str)
        method_str = colored_str(method_name, bold=True)
        self._print_line(f"{method_str}({all_args_str})")

        if no_indent:
            return fn(self, *args, **kwargs)

        self._call_depth += 1
        try:
            result = fn(self, *args, **kwargs)
        finally:
            self._call_depth -= 1
        return result

    return wrapper


class DebugMeta(type):
    """Metaclass that automatically wraps methods for debugging"""

    def __new__(mcs, name, bases, namespace, **kwargs):
        # Create the class first
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        if not any(isinstance(base, DebugMeta) for base in bases):
            return cls
        # Only apply debugging to classes that inherit from SeqDebug

        # Wrap all public methods for debugging
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if (
                callable(attr)
                and not attr_name.startswith("_")
                and attr_name != "dedent"
            ):
                setattr(cls, attr_name, wrap_function(attr, attr_name))

        return cls


class SeqDebug(metaclass=DebugMeta):
    """Base class for sequence debugging. Classes inheriting from this will automatically log method calls."""

    def __init__(self):
        self._call_depth = 0
        self._line_num = 0
        self._next_call_no_indent = False
        self._msg_log = []

    def _dedent(self):
        self._next_call_no_indent = True
        return self

    def _print_line(self, msg: str):
        indent = get_indent(self._call_depth)
        msg = f"{self._line_num:5} {indent}{msg}"
        self._msg_log += strip_color(msg)
        print(msg)
        self._line_num += 1

    def _log(self, *msgs: str):
        self._print_line(" ".join(colored_str(msg) for msg in msgs))

    def _write_log(self, path: str):
        with open(path, "w") as f:
            f.write("\n".join(self._msg_log))


ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def strip_color(text: str) -> str:
    """Remove ANSI color codes from a string."""
    return ansi_escape.sub("", text)
