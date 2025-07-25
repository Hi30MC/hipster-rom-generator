import functools
import hashlib


def get_indent(depth):
    return "\u23D0 " * depth


def get_method_color(method_name, bold=False):
    """Get a consistent 24-bit RGB color for a method name based on its hash"""
    # Generate RGB values from hash
    hash_bytes = hashlib.md5(method_name.encode()).digest()
    r = hash_bytes[0]
    g = hash_bytes[1]
    b = hash_bytes[2]

    # Ensure colors are bright enough to be readable
    r = max(r, 128)
    g = max(g, 128)
    b = max(b, 128)

    # 24-bit RGB color format: \033[38;2;R;G;Bm
    color = f'\033[38;2;{r};{g};{b}m'
    if bold:
        color = f'\033[1m{color}'  # Add bold

    reset = '\033[0m'
    return color, reset


def log_method_calls(cls):
    """Decorator that logs info when any method in the class is called"""

    original_init = cls.__init__

    @functools.wraps(original_init)
    def new_init(self, *args, **kwargs):
        self._call_depth = 0
        original_init(self, *args, **kwargs)
    cls.__init__ = new_init

    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith('_'):
            @functools.wraps(attr)
            def make_wrapper(method_name, original_method):
                def wrapper(self, *args, **kwargs):
                    args_str = ', '.join(str(arg) for arg in args)
                    kwargs_str = ', '.join(f'{k}={v}' for k, v in kwargs.items())
                    all_args = ', '.join(filter(None, [args_str, kwargs_str]))
                    indent = get_indent(self._call_depth)
                    color, reset = get_method_color(method_name, bold=True)
                    print(f"{indent}{color}{method_name}({all_args}){reset}")
                    self._call_depth += 1
                    try:
                        result = original_method(self, *args, **kwargs)
                    finally:
                        self._call_depth -= 1
                    return result
                return wrapper

            setattr(cls, attr_name, make_wrapper(attr_name, attr))
    return cls
