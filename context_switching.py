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
   :module: py_trees.demos.context_switching
   :func: command_line_argument_parser
   :prog: py-trees-demo-context-switching

.. graphviz:: dot/demo-context_switching.dot

.. image:: images/context_switching.gif
"""

##############################################################################
# 导入
##############################################################################

import argparse
import sys
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
    content = "演示使用并行和序列进行上下文切换。\n"
    content += "\n"
    content += (
        "上下文切换行为与工作序列并行运行。\n"
    )
    content += (
        "上下文切换发生在上下文切换行为的initialise()和terminate()方法中。\n"
    )
    content += (
        "注意，无论序列结果是失败还是成功，上下文切换行为都会始终调用\n"
    )
    content += (
        "terminate()方法来恢复上下文。在更高优先级的父行为取消\n"
    )
    content += (
        "这个并行子树的情况下，它也会调用terminate()来恢复上下文。\n"
    )
    if py_trees.console.has_colours:
        banner_line = console.green + "*" * 79 + "\n" + console.reset
        s = banner_line
        s += console.bold_white + "上下文切换".center(79) + "\n" + console.reset
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
    parser = argparse.ArgumentParser(
        description=description(),
        epilog=epilog(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-r", "--render", action="store_true", help="将dot树渲染到文件"
    )
    return parser


class ContextSwitch(py_trees.behaviour.Behaviour):
    """
    上下文切换类的示例。

    该类在`initialise()`中设置上下文，
    并在`terminate()`中恢复上下文。与进行工作的
    序列/子树并行使用，这些工作在此上下文中进行。

    .. attention:: 简单地在序列两端设置一对行为（设置和重置上下文）对于
        上下文切换是不够的。如果序列中的某个工作行为失败，最后的重置上下文
        开关将永远不会触发。
    """

    def __init__(self, name: str = "ContextSwitch"):
        """使用行为名称初始化。"""
        super(ContextSwitch, self).__init__(name)
        self.feedback_message = "无上下文"

    def initialise(self) -> None:
        """备份并设置新上下文。"""
        self.logger.debug("%s.initialise()[切换上下文]" % (self.__class__.__name__))
        # 一些操作：
        #   1. 从某处获取当前上下文
        #   2. 内部缓存上下文
        #   3. 应用新上下文
        self.feedback_message = "新上下文"

    def update(self) -> py_trees.common.Status:
        """在等待其他活动完成时只返回RUNNING。"""
        self.logger.debug(
            "%s.update()[RUNNING][%s]"
            % (self.__class__.__name__, self.feedback_message)
        )
        return py_trees.common.Status.RUNNING

    def terminate(self, new_status: py_trees.common.Status) -> None:
        """使用先前备份的上下文恢复上下文。"""
        self.logger.debug(
            "%s.terminate()[%s->%s][恢复上下文]"
            % (self.__class__.__name__, self.status, new_status)
        )
        # 一些操作：
        #   1. 恢复缓存的上下文
        self.feedback_message = "已恢复上下文"


def create_root() -> py_trees.behaviour.Behaviour:
    """
    创建根行为及其子树。

    返回:
        根行为
    """
    root = py_trees.composites.Parallel(
        name="并行", policy=py_trees.common.ParallelPolicy.SuccessOnOne()
    )
    context_switch = ContextSwitch(name="上下文")
    sequence = py_trees.composites.Sequence(name="序列", memory=True)
    for job in ["动作1", "动作2"]:
        success_after_two = py_trees.behaviours.StatusQueue(
            name=job,
            queue=[py_trees.common.Status.RUNNING, py_trees.common.Status.RUNNING],
            eventually=py_trees.common.Status.SUCCESS,
        )
        sequence.add_child(success_after_two)
    root.add_child(context_switch)
    root.add_child(sequence)
    return root


##############################################################################
# 主程序
##############################################################################


def main() -> None:
    """演示脚本的入口点。"""
    args = command_line_argument_parser().parse_args()
    print(description())
    py_trees.logging.level = py_trees.logging.Level.DEBUG

    root = create_root()

    ####################
    # 渲染
    ####################
    if args.render:
        py_trees.display.render_dot_tree(root)
        sys.exit()

    ####################
    # 执行
    ####################
    root.setup_with_descendants()
    for i in range(1, 6):
        try:
            print("\n--------- Tick {0} ---------\n".format(i))
            root.tick_once()
            print("\n")
            print("{}".format(py_trees.display.unicode_tree(root, show_status=True)))
            time.sleep(1.0)
        except KeyboardInterrupt:
            break
    print("\n")
