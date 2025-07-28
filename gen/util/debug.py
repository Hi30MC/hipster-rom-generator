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
        self.line_num = 0
        self._next_call_no_indent = False
        self.call_log = []
        original_init(self, *args, **kwargs)
    cls.__init__ = new_init

    def dedent(self):
        """Mark the next method call to not increase indent"""
        self._next_call_no_indent = True
        return self

    cls.dedent = dedent

    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if callable(attr) and not attr_name.startswith('_'):
            @functools.wraps(attr)
            def make_wrapper(method_name, original_method):
                def wrapper(self, *args, **kwargs):
                    args_str = ', '.join(str(arg) for arg in args)
                    kwargs_str = ', '.join(f'{k}={v}' for k, v in kwargs.items())
                    all_args = ', '.join(filter(None, [args_str, kwargs_str]))

                    # Check if this call should not increase indent
                    no_indent = getattr(self, '_next_call_no_indent', False)
                    if no_indent:
                        self._next_call_no_indent = False

                    indent = get_indent(self._call_depth)
                    color, reset = get_method_color(method_name, bold=True)
                    msg_no_format = f"{self.line_num:5}{indent}{method_name}({all_args})"
                    self.call_log.append(msg_no_format)
                    msg = f"{self.line_num:5}{indent}{color}{method_name}({all_args}){reset}"
                    print(msg)

                    # Only increase depth if not marked for no indent
                    if not no_indent:
                        self._call_depth += 1
                    self.line_num += 1
                    try:
                        result = original_method(self, *args, **kwargs)
                    finally:
                        if not no_indent:
                            self._call_depth -= 1
                    return result
                return wrapper

            setattr(cls, attr_name, make_wrapper(attr_name, attr))
    return cls
