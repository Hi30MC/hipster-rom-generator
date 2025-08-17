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


def log_calls(fn, method_name: str):
    @functools.wraps(fn)
    def wrapper(self: SeqDebug, *args, **kwargs):
        no_indent = self._next_call_no_indent
        if no_indent:
            self._next_call_no_indent = False

        args_str = [str(arg) for arg in args] + [f"{k}={v}" for k, v in kwargs.items()]
        all_args_str = ", ".join(args_str)
        method_str = colored_str(method_name, bold=True)
        method_call_msg = f"{method_str}({all_args_str})"

        # Track if this method should be printed (lazy printing)
        if no_indent:
            # If no indent, print immediately and execute
            self._print_line(method_call_msg)
            return fn(self, *args, **kwargs)

        # Set up lazy printing state - store the method call for potential printing
        self._pending_methods.append((self._call_depth, method_call_msg))

        self._call_depth += 1
        try:
            result = fn(self, *args, **kwargs)
        finally:
            self._call_depth -= 1
            # Remove the pending method after execution
            if self._pending_methods:
                self._pending_methods.pop()

        return result

    return wrapper


class AutoLogMethods(type):
    """Metaclass that automatically wraps methods in log_calls"""

    def __new__(mcs, name, bases, namespace, **kwargs):
        # Create the class first
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)

        if not any(issubclass(base, SeqDebug) for base in bases):
            raise TypeError("Class must inherit from SeqDebug")

        # Wrap all public methods for debugging
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if (
                callable(attr)
                and not attr_name.startswith("_")
                and attr_name != "dedent"
            ):
                setattr(cls, attr_name, log_calls(attr, attr_name))

        return cls


class SeqDebug:
    """Base class for sequence debugging. Must inherit this class to use @log_calls"""

    def __init__(self):
        self._call_depth = 0
        self._line_num = 0
        self._next_call_no_indent = False
        self._msg_log = []
        self._pending_methods = []

    def _dedent(self):
        # self._next_call_no_indent = True
        return self

    def _print_pending_methods_if_needed(self):
        """Print all pending method calls if any exist"""
        if self._pending_methods:
            # Print all pending methods in order (deepest first)
            methods_to_print = self._pending_methods.copy()
            self._pending_methods.clear()

            for call_depth, method_msg in methods_to_print:
                # Print the method call with proper indentation
                indent = get_indent(call_depth)
                msg_r = f"{indent}{method_msg}"
                print(f"{self._line_num:5d} {msg_r}")
                self._msg_log.append(strip_color(msg_r))
                self._line_num += 1

    def _print_line(self, msg: str):
        # If there are pending method calls, print them first
        self._print_pending_methods_if_needed()

        indent = get_indent(self._call_depth)
        msg_r = f"{indent}{msg}"
        print(f"{self._line_num:5d} {msg_r}")
        self._msg_log.append(strip_color(msg_r))
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
