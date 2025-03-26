#!/usr/bin/env python
#
# License: BSD
#   https://raw.githubusercontent.com/splintered-reality/py_trees/devel/LICENSE
#
##############################################################################
# 文档
##############################################################################

"""
一个py_trees演示。

. argparse::
   :module: py_trees.demos.lifecycle
   :func: command_line_argument_parser
   :prog: py-trees-demo-behaviour-lifecycle

.. image:: images/lifecycle.gif
"""

##############################################################################
# 导入
##############################################################################

import argparse
import time
import typing

import py_trees
import py_trees.console as console

##############################################################################
# 类
##############################################################################


def description() -> str:
    """
    打印程序的描述和使用信息。

    返回:
       程序描述字符串
    """
    content = "演示行为的典型生命周期。\n\n"
    content += (
        "这个行为将从1数到3，然后重置并重复。在此过程中，\n"
    )
    content += "它会记录并显示被调用的方法 - 构造，设置，\n"
    content += "初始化，运行和终止。\n"
    if py_trees.console.has_colours:
        banner_line = console.green + "*" * 79 + "\n" + console.reset
        s = banner_line
        s += (
            console.bold_white + "行为生命周期".center(79) + "\n" + console.reset
        )
        s += banner_line
        s += "\n"
        s += content
        s += "\n"
        s += banner_line
    else:
        s = content
    return s


def epilog() -> typing.Optional[str]:
    """
    为--help打印一个有趣的结语。

    返回:
       有趣的结语信息
    """
    if py_trees.console.has_colours:
        return (
            console.cyan
            + "他的面条般的附属物延伸出去抚摸被祝福的人...\n"
            + console.reset
        )
    else:
        return None


def command_line_argument_parser() -> argparse.ArgumentParser:
    """
    处理命令行参数。

    返回:
        参数解析器
    """
    return argparse.ArgumentParser(
        description=description(),
        epilog=epilog(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )


class Counter(py_trees.behaviour.Behaviour):
    """简单的计数行为。

    * 每次tick将计数器从零开始递增
    * 当计数器达到三时成功完成
    * 在initialise()方法中重置计数器。
    """

    def __init__(self, name: str = "Counter"):
        """配置行为的名称。"""
        super(Counter, self).__init__(name)
        self.logger.debug("%s.__init__()" % (self.__class__.__name__))

    def setup(self, **kwargs: int) -> None:
        """此示例不需要延迟初始化。"""
        self.logger.debug("%s.setup()" % (self.__class__.__name__))

    def initialise(self) -> None:
        """重置计数器变量。"""
        self.logger.debug("%s.initialise()" % (self.__class__.__name__))
        self.counter = 0

    def update(self) -> py_trees.common.Status:
        """增加计数器并决定新状态。"""
        self.counter += 1
        new_status = (
            py_trees.common.Status.SUCCESS
            if self.counter == 3
            else py_trees.common.Status.RUNNING
        )
        if new_status == py_trees.common.Status.SUCCESS:
            self.feedback_message = (
                "计数中...{0} - 唷，今天就数到这里吧".format(self.counter)
            )
        else:
            self.feedback_message = "还在计数"
        self.logger.debug(
            "%s.update()[%s->%s][%s]"
            % (self.__class__.__name__, self.status, new_status, self.feedback_message)
        )
        return new_status

    def terminate(self, new_status: py_trees.common.Status) -> None:
        """这个例子中没有需要清理的内容。"""
        self.logger.debug(
            "%s.terminate()[%s->%s]"
            % (self.__class__.__name__, self.status, new_status)
        )


##############################################################################
# 主函数
##############################################################################


def main() -> None:
    """演示脚本的入口点。"""
    command_line_argument_parser().parse_args()

    print(description())

    py_trees.logging.level = py_trees.logging.Level.DEBUG

    counter = Counter()
    counter.setup()
    try:
        for _unused_i in range(0, 7):
            counter.tick_once()
            time.sleep(0.5)
        print("\n")
    except KeyboardInterrupt:
        print("")
        pass
