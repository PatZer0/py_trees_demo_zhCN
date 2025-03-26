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
   :module: py_trees.demos.dot_graphs
   :func: command_line_argument_parser
   :prog: py-trees-demo-dot-graphs

.. graphviz:: dot/demo-dot-graphs.dot

"""

##############################################################################
# 导入
##############################################################################

import argparse
import subprocess
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
    name = "py-trees-demo-dot-graphs"
    content = "渲染一个简单树的dot图，包含黑盒。\n"
    if py_trees.console.has_colours:
        banner_line = console.green + "*" * 79 + "\n" + console.reset
        s = banner_line
        s += console.bold_white + "Dot图".center(79) + "\n" + console.reset
        s += banner_line
        s += "\n"
        s += content
        s += "\n"
        s += console.white
        s += console.bold + "    生成完整Dot图" + console.reset + "\n"
        s += "\n"
        s += console.cyan + "        {0}".format(name) + console.reset + "\n"
        s += "\n"
        s += console.bold + "    使用不同可见性级别" + console.reset + "\n"
        s += "\n"
        s += (
            console.cyan
            + "        {0}".format(name)
            + console.yellow
            + " --level=all"
            + console.reset
            + "\n"
        )
        s += (
            console.cyan
            + "        {0}".format(name)
            + console.yellow
            + " --level=detail"
            + console.reset
            + "\n"
        )
        s += (
            console.cyan
            + "        {0}".format(name)
            + console.yellow
            + " --level=component"
            + console.reset
            + "\n"
        )
        s += (
            console.cyan
            + "        {0}".format(name)
            + console.yellow
            + " --level=big_picture"
            + console.reset
            + "\n"
        )
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
        "-l",
        "--level",
        action="store",
        default="fine_detail",
        choices=["all", "fine_detail", "detail", "component", "big_picture"],
        help="可见性级别",
    )
    return parser


def create_tree(level: str) -> py_trees.behaviour.Behaviour:
    """
    创建根行为及其子树。

    返回:
        根行为
    """
    root = py_trees.composites.Selector(name="演示Dot图 %s" % level, memory=False)
    first_blackbox = py_trees.composites.Sequence(name="黑盒 1", memory=True)
    first_blackbox.add_child(py_trees.behaviours.Running("工作者"))
    first_blackbox.add_child(py_trees.behaviours.Running("工作者"))
    first_blackbox.add_child(py_trees.behaviours.Running("工作者"))
    first_blackbox.blackbox_level = py_trees.common.BlackBoxLevel.BIG_PICTURE
    second_blackbox = py_trees.composites.Sequence(name="黑盒 2", memory=True)
    second_blackbox.add_child(py_trees.behaviours.Running("工作者"))
    second_blackbox.add_child(py_trees.behaviours.Running("工作者"))
    second_blackbox.add_child(py_trees.behaviours.Running("工作者"))
    second_blackbox.blackbox_level = py_trees.common.BlackBoxLevel.COMPONENT
    third_blackbox = py_trees.composites.Sequence(name="黑盒 3", memory=True)
    third_blackbox.add_child(py_trees.behaviours.Running("工作者"))
    third_blackbox.add_child(py_trees.behaviours.Running("工作者"))
    third_blackbox.add_child(py_trees.behaviours.Running("工作者"))
    third_blackbox.blackbox_level = py_trees.common.BlackBoxLevel.DETAIL
    root.add_child(first_blackbox)
    root.add_child(second_blackbox)
    first_blackbox.add_child(third_blackbox)
    return root


##############################################################################
# 主程序
##############################################################################


def main() -> None:
    """演示脚本的入口点。"""
    args = command_line_argument_parser().parse_args()
    args.enum_level = py_trees.common.string_to_visibility_level(args.level)
    print(description())
    py_trees.logging.level = py_trees.logging.Level.DEBUG

    root = create_tree(args.level)
    py_trees.display.render_dot_tree(root, args.enum_level)

    if py_trees.utilities.which("xdot"):
        try:
            subprocess.call(["xdot", "demo_dot_graphs_%s.dot" % args.level])
        except KeyboardInterrupt:
            pass
    else:
        print("")
        console.logerror(
            "未找到xdot查看器，跳过显示 [提示: sudo apt install xdot]"
        )
        print("")
