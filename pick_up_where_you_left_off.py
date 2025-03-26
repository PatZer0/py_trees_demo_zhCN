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
   :module: py_trees.demos.pick_up_where_you_left_off
   :func: command_line_argument_parser
   :prog: py-trees-demo-pick-up-where-you-left-off

.. graphviz:: dot/pick_up_where_you_left_off.dot

.. image:: images/pick_up_where_you_left_off.gif
"""

##############################################################################
# 导入
##############################################################################

import argparse
import functools
import sys
import time
import typing

import py_trees
import py_trees.console as console

##############################################################################
# 类
##############################################################################


def description(root: py_trees.behaviour.Behaviour) -> str:
    """
    打印程序的描述和使用信息。

    返回:
       程序描述字符串
    """
    content = "'从你离开的地方继续'习语的演示。\n\n"
    content += "一种常见的行为树模式，允许在被高优先级中断后\n"
    content += "恢复工作。\n"
    content += "\n"
    content += "事件\n"
    content += "\n"
    content += " -  2 : 任务一完成，任务二运行中\n"
    content += " -  3 : 高优先级中断\n"
    content += " -  7 : 任务二重启\n"
    content += " -  9 : 任务二完成\n"
    content += "\n"
    if py_trees.console.has_colours:
        banner_line = console.green + "*" * 79 + "\n" + console.reset
        s = banner_line
        s += (
            console.bold_white
            + "从你离开的地方继续".center(79)
            + "\n"
            + console.reset
        )
        s += banner_line
        s += "\n"
        s += content
        s += "\n"
        s += py_trees.display.unicode_tree(root)
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
        description=description(create_root()),
        epilog=epilog(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-r", "--render", action="store_true", help="将dot树渲染到文件"
    )
    group.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="在每个tick暂停并等待按键",
    )
    return parser


def pre_tick_handler(behaviour_tree: py_trees.trees.BehaviourTree) -> None:
    """在树的每个tick之前立即打印一个横幅。

    参数:
        behaviour_tree (:class:`~py_trees.trees.BehaviourTree`): 树的管理者

    """
    print("\n--------- 运行 %s ---------\n" % behaviour_tree.count)


def post_tick_handler(
    snapshot_visitor: py_trees.visitors.SnapshotVisitor,
    behaviour_tree: py_trees.trees.BehaviourTree,
) -> None:
    """打印一个ASCII树，显示当前快照状态。"""
    print(
        "\n"
        + py_trees.display.unicode_tree(
            root=behaviour_tree.root,
            visited=snapshot_visitor.visited,
            previously_visited=snapshot_visitor.previously_visited,
        )
    )


def create_root() -> py_trees.behaviour.Behaviour:
    """
    创建根行为及其子树。

    返回:
        根行为
    """
    task_one = py_trees.behaviours.StatusQueue(
        name="任务 1",
        queue=[
            py_trees.common.Status.RUNNING,
            py_trees.common.Status.RUNNING,
        ],
        eventually=py_trees.common.Status.SUCCESS,
    )
    task_two = py_trees.behaviours.StatusQueue(
        name="任务 2",
        queue=[
            py_trees.common.Status.RUNNING,
            py_trees.common.Status.RUNNING,
        ],
        eventually=py_trees.common.Status.SUCCESS,
    )
    high_priority_interrupt = py_trees.decorators.RunningIsFailure(
        name="Running is Failure",
        child=py_trees.behaviours.Periodic(name="高优先级", n=3),
    )
    piwylo = py_trees.idioms.pick_up_where_you_left_off(
        name="从你离开\n的地方\n继续", tasks=[task_one, task_two]
    )
    root = py_trees.composites.Selector(name="Root", memory=False)
    root.add_children([high_priority_interrupt, piwylo])

    return root


##############################################################################
# 主函数
##############################################################################


def main() -> None:
    """演示脚本的入口点。"""
    args = command_line_argument_parser().parse_args()
    py_trees.logging.level = py_trees.logging.Level.DEBUG
    root = create_root()
    print(description(root))

    ####################
    # 渲染
    ####################
    if args.render:
        py_trees.display.render_dot_tree(root)
        sys.exit()

    ####################
    # 树管理
    ####################
    behaviour_tree = py_trees.trees.BehaviourTree(root)
    behaviour_tree.add_pre_tick_handler(pre_tick_handler)
    behaviour_tree.visitors.append(py_trees.visitors.DebugVisitor())
    snapshot_visitor = py_trees.visitors.SnapshotVisitor()
    behaviour_tree.add_post_tick_handler(
        functools.partial(post_tick_handler, snapshot_visitor)
    )
    behaviour_tree.visitors.append(snapshot_visitor)
    behaviour_tree.setup(timeout=15)

    ####################
    # 定时运行
    ####################
    if args.interactive:
        py_trees.console.read_single_keypress()
    for _unused_i in range(1, 11):
        try:
            behaviour_tree.tick()
            if args.interactive:
                py_trees.console.read_single_keypress()
            else:
                time.sleep(0.5)
        except KeyboardInterrupt:
            break
    print("\n")
