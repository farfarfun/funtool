from __future__ import annotations

from typing import Any

import ipywidgets as widgets
from farlog import getLogger
from IPython.display import display

DEFAULT_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} - [{level}] {message}"


class OutputWidgetSink:
    """把 farlog 日志写入 Jupyter 输出组件。"""

    def __init__(self) -> None:
        layout = {"width": "100%", "height": "160px", "border": "1px solid black"}
        self.out = widgets.Output(layout=layout)

    def write(self, message: Any) -> None:
        """接收 Loguru 消息并追加到组件。"""
        output = {"name": "stdout", "output_type": "stream", "text": str(message)}
        self.out.outputs = (output,) + self.out.outputs

    def show_logs(self) -> None:
        """显示日志组件。"""
        display(self.out)

    def clear_logs(self) -> None:
        """清空日志组件。"""
        self.out.clear_output()


OutputWidgetHandler = OutputWidgetSink


def load_log_widget(
    name: str | None = None,
    formatter: str | None = None,
    *args: Any,
    **kwargs: Any,
) -> tuple[Any, OutputWidgetSink]:
    """创建 farlog 日志器及其 Jupyter 输出组件 sink。"""
    logger = getLogger(name or __name__)
    del args, kwargs
    sink = OutputWidgetSink()
    logger.add(sink.write, format=formatter or DEFAULT_FORMAT)
    return logger, sink
