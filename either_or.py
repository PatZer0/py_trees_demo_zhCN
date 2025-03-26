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
   :module: py_trees.demos.either_or
   :func: command_line_argument_parser
   :prog: py-trees-demo-either-or

.. graphviz:: dot/demo-either-or.dot

.. image:: images/either_or.gif
"""

##############################################################################
# 导入
##############################################################################

import argparse
import functools
import operator
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
    content = "'either_or'习语的演示。\n\n"
    content += "这种行为树模式使得可以触发相同优先级的子树\n"
    content += "（先到先得）。\n"
    content += "\n"
    content += "事件\n"
    content += "\n"
    content += " -  3 : 摇杆一启用，任务一开始\n"
    content += " -  5 : 任务一完成\n"
    content += " -  6 : 摇杆二启用，任务二开始\n"
    content += " -  7 : 摇杆一启用，任务一被忽略，任务二继续\n"
    content += " -  8 : 任务二完成\n"
    content += "\n"
    if py_trees.console.has_colours:
        banner_line = console.green + "*" * 79 + "\n" + console.reset
        s = banner_line
        s += console.bold_white + "二选一".center(79) + "\n" + console.reset
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
    """在树的每个tick之前立即打印一个带有当前tick计数的横幅。

    参数:
       behaviour_tree: 要tick的树（用于获取计数号）
    """
    print("\n--------- 运行 %s ---------\n" % behaviour_tree.count)


def post_tick_handler(
    snapshot_visitor: py_trees.visitors.SnapshotVisitor,
    behaviour_tree: py_trees.trees.BehaviourTree,
) -> None:
    """
    打印有关树访问部分的数据。

    参数:
        snapshot_handler: 收集有关树访问部分的数据
        behaviour_tree: 要收集数据的树
    """
    print(
        "\n"
        + py_trees.display.unicode_tree(
            root=behaviour_tree.root,
            visited=snapshot_visitor.visited,
            previously_visited=snapshot_visitor.previously_visited,
        )
    )
    print(py_trees.display.unicode_blackboard())


def create_root() -> py_trees.behaviour.Behaviour:
    """
    创建根行为及其子树。

    返回:
        根行为
    """
    trigger_one = py_trees.decorators.FailureIsRunning(
        name="FisR", child=py_trees.behaviours.SuccessEveryN(name="摇杆 1", n=4)
    )
    trigger_two = py_trees.decorators.FailureIsRunning(
        name="FisR", child=py_trees.behaviours.SuccessEveryN(name="摇杆 2", n=7)
    )
    enable_joystick_one = py_trees.behaviours.SetBlackboardVariable(
        name="摇杆1 - 已启用",
        variable_name="joystick_one",
        variable_value="enabled",
        overwrite=True,
    )
    enable_joystick_two = py_trees.behaviours.SetBlackboardVariable(
        name="摇杆2 - 已启用",
        variable_name="joystick_two",
        variable_value="enabled",
        overwrite=True,
    )
    reset_joystick_one = py_trees.behaviours.SetBlackboardVariable(
        name="摇杆1 - 已禁用",
        variable_name="joystick_one",
        variable_value="disabled",
        overwrite=True,
    )
    reset_joystick_two = py_trees.behaviours.SetBlackboardVariable(
        name="摇杆2 - 已禁用",
        variable_name="joystick_two",
        variable_value="disabled",
        overwrite=True,
    )
    task_one = py_trees.behaviours.TickCounter(
        name="任务 1", duration=2, completion_status=py_trees.common.Status.SUCCESS
    )
    task_two = py_trees.behaviours.TickCounter(
        name="任务 2", duration=2, completion_status=py_trees.common.Status.SUCCESS
    )
    idle = py_trees.behaviours.Running(name="空闲")
    either_or = py_trees.idioms.either_or(
        name="二选一",
        conditions=[
            py_trees.common.ComparisonExpression(
                "joystick_one", "enabled", operator.eq
            ),
            py_trees.common.ComparisonExpression(
                "joystick_two", "enabled", operator.eq
            ),
        ],
        subtrees=[task_one, task_two],
        namespace="either_or",
    )
    root = py_trees.composites.Parallel(
        name="根节点",
        policy=py_trees.common.ParallelPolicy.SuccessOnAll(synchronise=False),
    )
    reset = py_trees.composites.Sequence(name="重置", memory=True)
    reset.add_children([reset_joystick_one, reset_joystick_two])
    joystick_one_events = py_trees.composites.Sequence(name="摇杆1事件", memory=True)
    joystick_one_events.add_children([trigger_one, enable_joystick_one])
    joystick_two_events = py_trees.composites.Sequence(name="摇杆2事件", memory=True)
    joystick_two_events.add_children([trigger_two, enable_joystick_two])
    tasks = py_trees.composites.Selector(name="任务", memory=False)
    tasks.add_children([either_or, idle])
    root.add_children([reset, joystick_one_events, joystick_two_events, tasks])
    return root


##############################################################################
# 主函数
##############################################################################


def main() -> None:
    """演示脚本的入口点。"""
    args = command_line_argument_parser().parse_args()
    # py_trees.logging.level = py_trees.logging.Level.DEBUG
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
