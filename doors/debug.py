import functools
import hashlib
from abc import ABC
from abc import abstractmethod
from typing import Union, NamedTuple
from typing import Callable


CallNode = Union["MessageNode", "MethodNode"]


class MessageNode:
    parent: "MethodNode | None" = None

    def __init__(self, content: str):
        self.message = content


class CallName(NamedTuple):
    method_name: str
    args: list[str]

    def default_to_string(self) -> str:
        args_str = ", ".join(self.args)
        return f"{self.method_name}({args_str})"

    def __str__(self) -> str:
        return self.default_to_string()


class MethodNode:
    parent: "MethodNode | None" = None

    def __init__(self, call_name: CallName | None):
        self.call_name = call_name
        self.children: list[CallNode] = []

    def add_child(self, child: CallNode):
        child.parent = self
        self.children.append(child)


class CallTree:
    def __init__(self):
        self.root = MethodNode(None)
        self.current_node: MethodNode = self.root

    def start_method(self, call_name: CallName):
        node = MethodNode(call_name)
        self.current_node.add_child(node)
        self.current_node = node
        return node

    def add_message(self, message: str):
        self.current_node.add_child(MessageNode(message))

    def exit_method(self):
        if self.current_node.parent:
            self.current_node = self.current_node.parent

    def to_string(self, options: "FormatOptions | None" = None) -> str:
        if options is None:
            options = FormatOptions.text()
        formatter = TextFormatter(options)
        formatter.visit_node(self.root)
        return formatter.to_string()


def log_calls(call_tree_attr: str = "call_tree"):
    """Decorator to log method calls"""

    def decorator(fn: Callable):
        @functools.wraps(fn)
        def wrapper(self, *args, **kwargs):
            args_list = [str(arg) for arg in args] + [
                f"{k}={v}" for k, v in kwargs.items()
            ]
            call_tree = getattr(self, call_tree_attr)
            method_name = fn.__name__
            call_tree.start_method(CallName(method_name, args_list))

            try:
                result = fn(self, *args, **kwargs)
            finally:
                call_tree.exit_method()

            return result

        return wrapper

    return decorator


class AutoLog(type):
    def __new__(
        cls, name: str, bases: tuple[type, ...], attrs: dict[str, object]
    ) -> type:
        for name, value in attrs.items():
            if not name.startswith("_") and callable(value):
                attrs[name] = log_calls()(value)
        return super().__new__(cls, name, bases, attrs)


class PrintTreeVisitor(ABC):
    @abstractmethod
    def on_method(self, method: MethodNode, depth: int):
        pass

    @abstractmethod
    def on_message(self, message: MessageNode, depth: int):
        pass

    def visit_node(self, node: MethodNode, depth: int = 0):
        self.on_method(node, depth)
        for child in node.children:
            if isinstance(child, MethodNode):
                self.visit_node(child, depth + 1)
            elif isinstance(child, MessageNode):
                self.on_message(child, depth + 1)


class FormatOptions(NamedTuple):
    indent_str: str = "  "
    method_formatter: Callable[[CallName], str | None] = str
    message_formatter: Callable[[str], str] = str
    line_formatter: Callable[[str, int], str] = lambda msg, _line_number: msg

    def get_indent(self, depth: int) -> str:
        return self.indent_str * depth

    @classmethod
    def text(cls) -> "FormatOptions":
        return cls(
            indent_str="\u23d0 ",
        )

    @classmethod
    def yaml(cls) -> "FormatOptions":
        return cls(
            indent_str="  ",
            method_formatter=lambda name: f"- {name}:",
            message_formatter=lambda msg: f"- {msg}",
            # cut first 2 chars to de-indent
            line_formatter=lambda msg, line_number: msg[2:],
        )


class TextFormatter(PrintTreeVisitor):

    def __init__(self, options: FormatOptions):
        self.options = options
        self.lines: list[str] = []

    def on_method(self, method: MethodNode, depth: int):
        call_name = method.call_name
        if call_name is None:
            return
        self.add_line(self.options.method_formatter(call_name), depth)

    def on_message(self, message: MessageNode, depth: int):
        self.add_line(self.options.message_formatter(message.message), depth)

    def add_line(self, content: str | None, depth: int):
        if content is None:
            return
        indent = self.options.get_indent(depth - 1)
        line = indent + content
        line_num = len(self.lines)
        self.lines.append(self.options.line_formatter(line, line_num))

    def to_string(self) -> str:
        return "\n".join(self.lines)
