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

.. argparse::
   :module: py_trees.demos.selector
   :func: command_line_argument_parser
   :prog: py-trees-demo-selector

.. graphviz:: dot/demo-selector.dot

.. image:: images/selector.gif

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
    content = (
        "在选择器的子节点中进行更高优先级的切换和中断。\n"
    )
    content += "\n"
    content += "在此示例中，更高优先级的子节点最初设置为失败，\n"
    content += "回退到持续运行的第二个子节点。在第三个\n"
    content += (
        "tick时，第一个子节点成功并取消了迄今为止正在运行的子节点。\n"
    )
    if py_trees.console.has_colours:
        banner_line = console.green + "*" * 79 + "\n" + console.reset
        s = banner_line
        s += console.bold_white + "选择器".center(79) + "\n" + console.reset
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
    parser = argparse.ArgumentParser(
        description=description(),
        epilog=epilog(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-r", "--render", action="store_true", help="将dot树渲染到文件"
    )
    return parser


def create_root() -> py_trees.behaviour.Behaviour:
    """
    创建根行为及其子树。

    返回:
        根行为
    """
    root = py_trees.composites.Selector(name="Selector", memory=False)
    ffs = py_trees.behaviours.StatusQueue(
        name="FFS",
        queue=[
            py_trees.common.Status.FAILURE,
            py_trees.common.Status.FAILURE,
            py_trees.common.Status.SUCCESS,
        ],
        eventually=py_trees.common.Status.SUCCESS,
    )
    always_running = py_trees.behaviours.Running(name="Running")
    root.add_children([ffs, always_running])
    return root


##############################################################################
# 主函数
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
    for i in range(1, 4):
        try:
            print("\n--------- Tick {0} ---------\n".format(i))
            root.tick_once()
            print("\n")
            print(py_trees.display.unicode_tree(root=root, show_status=True))
            time.sleep(1.0)
        except KeyboardInterrupt:
            break
    print("\n")
