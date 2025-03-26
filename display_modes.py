#!/usr/bin/env python3
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
   :module: py_trees.demos.display_modes
   :func: command_line_argument_parser
   :prog: py-trees-demo-display-modes

.. figure:: images/display_modes.png
   :align: center

   控制台截图
"""

##############################################################################
# 导入
##############################################################################

import argparse
import itertools
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
    content = "演示ASCII/Unicode显示模式的使用。\n"
    content += "\n"
    content += "...\n"
    content += "...\n"

    if py_trees.console.has_colours:
        banner_line = console.green + "*" * 79 + "\n" + console.reset
        s = banner_line
        s += console.bold_white + "显示模式".center(79) + "\n" + console.reset
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
    return parser


def create_root() -> py_trees.behaviour.Behaviour:
    """
    创建要被tick/显示的树。

    返回:
        树的根节点
    """
    root = py_trees.composites.Sequence(name="根节点", memory=True)
    child = py_trees.composites.Sequence(name="子节点1", memory=True)
    child2 = py_trees.composites.Sequence(name="子节点2", memory=True)
    child3 = py_trees.composites.Sequence(name="子节点3", memory=True)
    root.add_child(child)
    root.add_child(child2)
    root.add_child(child3)
    queue = [py_trees.common.Status.RUNNING]
    eventually = py_trees.common.Status.SUCCESS
    child.add_child(
        py_trees.behaviours.StatusQueue(name="RS", queue=queue, eventually=eventually)
    )
    child2.add_child(
        py_trees.behaviours.StatusQueue(name="RS", queue=queue, eventually=eventually)
    )
    child2_child1 = py_trees.composites.Sequence(name="子节点2_子节点1", memory=True)
    child2_child1.add_child(
        py_trees.behaviours.StatusQueue(name="RS", queue=queue, eventually=eventually)
    )
    child2.add_child(child2_child1)
    child3.add_child(
        py_trees.behaviours.StatusQueue(name="RS", queue=queue, eventually=eventually)
    )
    return root


##############################################################################
# 主程序
##############################################################################


def main() -> None:
    """演示脚本的入口点。"""
    _ = (
        command_line_argument_parser().parse_args()
    )  # 仅配置，没有需要处理的参数
    print(description())
    print(
        "-------------------------------------------------------------------------------"
    )
    print("$ py_trees.blackboard.Client(name='黑板')")
    print("$ foo.register_key(key='dude', access=py_trees.common.Access.WRITE)")
    print("$ foo.register_key(key='/dudette', access=py_trees.common.Access.WRITE)")
    print("$ foo.register_key(key='/foo/bar/wow', access=py_trees.common.Access.WRITE)")
    print(
        "-------------------------------------------------------------------------------"
    )

    snapshot_visitor = py_trees.visitors.SnapshotVisitor()
    tree = py_trees.trees.BehaviourTree(create_root())
    tree.add_visitor(snapshot_visitor)

    for tick in range(2):
        tree.tick()
        for show_visited, show_status in itertools.product(
            [False, True], [False, True]
        ):
            console.banner(
                "Tick {} / show_only_visited=={} / show_status=={}".format(
                    tick, show_visited, show_status
                )
            )
            print(
                py_trees.display.unicode_tree(
                    tree.root,
                    show_status=show_status,
                    show_only_visited=show_visited,
                    visited=snapshot_visitor.visited,
                    previously_visited=snapshot_visitor.previously_visited,
                )
            )
            print()
