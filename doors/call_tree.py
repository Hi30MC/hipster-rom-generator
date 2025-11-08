import functools
from typing import Union, NamedTuple
from typing import Callable
from typing import cast
import dataclasses


CallNode = Union["MessageNode", "MethodNode"]


class MessageNode:
    parent: "MethodNode | None" = None

    def __init__(self, message: str):
        self.message = message


class MethodCall(NamedTuple):
    method_name: str
    args: list[str]

    def __str__(self) -> str:
        args_str = ", ".join(self.args)
        return f"{self.method_name}({args_str})"


class MethodNode:
    parent: "MethodNode | None" = None

    def __init__(self, call_name: MethodCall | None):
        self.call_name = call_name
        self.children: list[CallNode] = []

    def add_child(self, child: CallNode):
        child.parent = self
        self.children.append(child)


class CallTree:
    def __init__(self):
        self.root = MethodNode(None)
        self.current_node: MethodNode = self.root

    def enter_method(self, call: MethodCall):
        node = MethodNode(call)
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
        return "\n".join(formatter.lines)


def skip_logging[T: Callable](func: T) -> T:
    func._skip_logging = True  # type: ignore
    return func


def log_calls(call_tree_attr: str = "call_tree"):
    """Decorator to log method calls"""

    def decorator[T: Callable](fn: T) -> T:
        if getattr(fn, "_skip_logging", False):
            return fn

        @functools.wraps(fn)
        def wrapper(self, *args, **kwargs):
            args_list = [str(arg) for arg in args] + [
                f"{k}={v}" for k, v in kwargs.items()
            ]
            call_tree: CallTree = getattr(self, call_tree_attr)
            method_name = fn.__name__
            call_tree.enter_method(MethodCall(method_name, args_list))

            try:
                result = fn(self, *args, **kwargs)
            finally:
                call_tree.exit_method()

            return result

        return cast(T, wrapper)

    return decorator


class AutoLog(type):
    def __new__(
        cls, name: str, bases: tuple[type, ...], attrs: dict[str, object]
    ) -> type:
        for name, value in attrs.items():
            if not name.startswith("_") and callable(value):
                attrs[name] = log_calls()(value)
        return super().__new__(cls, name, bases, attrs)


@dataclasses.dataclass
class FormatOptions:
    indent_str: str = "  "
    method_formatter: Callable[[MethodCall], str | None] = str
    message_formatter: Callable[[str], str] = str
    line_formatter: Callable[[str], str] = str
    skip_empty_methods: bool = False
    collapse_simple_methods: bool = True

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
        )


class TextFormatter:

    def __init__(self, options: FormatOptions):
        self.options = options
        self.lines: list[str] = []

    def _add_method_message(self, method: MethodNode, depth: int):
        call_name = method.call_name
        if call_name is None:
            return
        self._add_line(self.options.method_formatter(call_name), depth)

    def _add_message(self, message: MessageNode, depth: int):
        self._add_line(self.options.message_formatter(message.message), depth)

    def _add_line(self, content: str | None, depth: int):
        if content is None:
            return
        line = self.options.get_indent(depth - 1) + content
        self.lines.append(self.options.line_formatter(line))

    def visit_node(self, node: MethodNode, depth: int = 0):
        if self.options.skip_empty_methods and not node.children:
            return
        self._add_method_message(node, depth)
        if (
            self.options.collapse_simple_methods
            and node.children
            and all(isinstance(child, MessageNode) for child in node.children)
            and sum(len(child.message) for child in node.children) < 50
        ):
            joined_messages = " ".join(child.message for child in node.children)
            self.lines[-1] += " " + joined_messages
            return
        for child in node.children:
            if isinstance(child, MethodNode):
                self.visit_node(child, depth + 1)
            elif isinstance(child, MessageNode):
                self._add_message(child, depth + 1)
