#!/usr/bin/env python
#
# License: BSD
#   https://raw.githubusercontent.com/splintered-reality/py_trees/devel/LICENSE
#
##############################################################################
# 文档
##############################################################################

"""
一个py_trees演示程序。

.. argparse::
   :module: py_trees.demos.action
   :func: command_line_argument_parser
   :prog: py-trees-demo-action-behaviour

.. image:: images/action.gif
"""

##############################################################################
# 导入
##############################################################################

import argparse
import atexit
import multiprocessing
import multiprocessing.connection
import time
import typing

import py_trees.common
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
    content = "演示典型'动作'行为的特征。\n"
    content += "\n"
    content += "* 在setup()方法中模拟外部进程并连接到它\n"
    content += (
        "* 在initialise()方法中向外部进程启动新目标\n"
    )
    content += "* 在update()方法中监控持续目标状态\n"
    content += (
        "* 根据外部进程的反馈确定RUNNING/SUCCESS状态\n"
    )

    if py_trees.console.has_colours:
        banner_line = console.green + "*" * 79 + "\n" + console.reset
        s = banner_line
        s += console.bold_white + "动作行为".center(79) + "\n" + console.reset
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
    为--help打印一个有趣的结束语。

    返回:
       有趣的消息
    """
    if py_trees.console.has_colours:
        return (
            console.cyan
            + "而他那面条般的附肢伸出去挠了挠那些有福的人...\n"
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


def planning(pipe_connection: multiprocessing.connection.Connection) -> None:
    """模拟一个（潜在的）长时间运行的外部进程。

    参数:
        pipe_connection: 与计划进程的连接
    """
    idle = True
    percentage_complete = 0
    try:
        while True:
            if pipe_connection.poll():
                pipe_connection.recv()
                percentage_complete = 0
                idle = False
            if not idle:
                percentage_complete += 10
                pipe_connection.send([percentage_complete])
                if percentage_complete == 100:
                    idle = True
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass


class Action(py_trees.behaviour.Behaviour):
    """演示远距离风格动作行为。

    这个行为连接到一个单独运行的进程
    （在setup()中启动）并与该子进程进行合作
    以在每个tick执行一项任务并监控该任务的进度
    直到完成。当任务运行时，此行为返回
    :data:`~py_trees.common.Status.RUNNING`。

    完成时，行为返回成功或失败
    （取决于任务本身的成功或失败）。

    关键点 - 这个行为本身不应该做任何工作！
    """

    def __init__(self, name: str):
        """配置行为的名称。"""
        super(Action, self).__init__(name)
        self.logger.debug("%s.__init__()" % (self.__class__.__name__))

    def setup(self, **kwargs: int) -> None:
        """启动此行为将与之配合工作的独立进程。

        通常这个进程已经在运行。在这种情况下，
        setup通常只负责验证它存在。
        """
        self.logger.debug(
            "%s.setup()->连接到外部进程" % (self.__class__.__name__)
        )
        self.parent_connection, self.child_connection = multiprocessing.Pipe()
        self.planning = multiprocessing.Process(
            target=planning, args=(self.child_connection,)
        )
        atexit.register(self.planning.terminate)
        self.planning.start()

    def initialise(self) -> None:
        """重置计数器变量。"""
        self.logger.debug(
            "%s.initialise()->发送新目标" % (self.__class__.__name__)
        )
        self.parent_connection.send(["新目标"])
        self.percentage_completion = 0

    def update(self) -> py_trees.common.Status:
        """增加计数器，监控并决定新状态。"""
        new_status = py_trees.common.Status.RUNNING
        if self.parent_connection.poll():
            self.percentage_completion = self.parent_connection.recv().pop()
            if self.percentage_completion == 100:
                new_status = py_trees.common.Status.SUCCESS
        if new_status == py_trees.common.Status.SUCCESS:
            self.feedback_message = "处理完成"
            self.logger.debug(
                "%s.update()[%s->%s][%s]"
                % (
                    self.__class__.__name__,
                    self.status,
                    new_status,
                    self.feedback_message,
                )
            )
        else:
            self.feedback_message = "{0}%".format(self.percentage_completion)
            self.logger.debug(
                "%s.update()[%s][%s]"
                % (self.__class__.__name__, self.status, self.feedback_message)
            )
        return new_status

    def terminate(self, new_status: py_trees.common.Status) -> None:
        """在这个例子中没有需要清理的内容。"""
        self.logger.debug(
            "%s.terminate()[%s->%s]"
            % (self.__class__.__name__, self.status, new_status)
        )


##############################################################################
# 主程序
##############################################################################


def main() -> None:
    """演示脚本的入口点。"""
    command_line_argument_parser().parse_args()

    print(description())

    py_trees.logging.level = py_trees.logging.Level.DEBUG

    action = Action(name="动作")
    action.setup()
    try:
        for _unused_i in range(0, 12):
            action.tick_once()
            time.sleep(0.5)
        print("\n")
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()