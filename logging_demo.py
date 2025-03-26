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
   :module: py_trees.demos.logging
   :func: command_line_argument_parser
   :prog: py-trees-demo-logging

.. graphviz:: dot/demo-logging.dot

.. image:: images/logging.gif
"""

##############################################################################
# 导入
##############################################################################

import argparse
import functools
import json
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
    content = "树日志记录的演示。\n\n"
    content += "此演示使用SnapshotVisitor触发\n"
    content += "一个post-tick处理器，将树的序列化\n"
    content += "输出到json日志文件。\n"
    content += "\n"
    content += "访问者和post-tick处理器的这种耦合可以\n"
    content += "用于任何类型的事件处理 - 访问者是\n"
    content += "触发器，post-tick处理器是动作。除了\n"
    content += "日志记录外，最常见的用例是将树序列化\n"
    content += "用于消息传递到图形化的运行时监视器。\n"
    content += "\n"
    if py_trees.console.has_colours:
        banner_line = console.green + "*" * 79 + "\n" + console.reset
        s = banner_line
        s += console.bold_white + "日志记录".center(79) + "\n" + console.reset
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
        description=description(create_tree()),
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


def logger(
    snapshot_visitor: py_trees.visitors.DisplaySnapshotVisitor,
    behaviour_tree: py_trees.trees.BehaviourTree,
) -> None:
    """将树（相关部分）记录到yaml文件中。

    用作树的post-tick处理器。
    """
    if snapshot_visitor.changed:
        print(console.cyan + "记录中.......................是\n" + console.reset)
        tree_serialisation = {"tick": behaviour_tree.count, "nodes": []}
        for node in behaviour_tree.root.iterate():
            node_type_str = "Behaviour"
            for behaviour_type in [
                py_trees.composites.Sequence,
                py_trees.composites.Selector,
                py_trees.composites.Parallel,
                py_trees.decorators.Decorator,
            ]:
                if isinstance(node, behaviour_type):
                    node_type_str = behaviour_type.__name__
            if node.tip() is not None:
                node_tip = node.tip()
                assert node_tip is not None  # 帮助mypy
                node_tip_id = str(node_tip.id)
            else:
                node_tip_id = "none"
            node_snapshot = {
                "name": node.name,
                "id": str(node.id),
                "parent_id": str(node.parent.id) if node.parent else "none",
                "child_ids": [str(child.id) for child in node.children],
                "tip_id": node_tip_id,
                "class_name": str(node.__module__) + "." + str(type(node).__name__),
                "type": node_type_str,
                "status": node.status.value,
                "message": node.feedback_message,
                "is_active": True if node.id in snapshot_visitor.visited else False,
            }
            typing.cast(list, tree_serialisation["nodes"]).append(node_snapshot)
        if behaviour_tree.count == 0:
            with open("dump.json", "w+") as outfile:
                json.dump(tree_serialisation, outfile, indent=4)
        else:
            with open("dump.json", "a") as outfile:
                json.dump(tree_serialisation, outfile, indent=4)
    else:
        print(console.yellow + "记录中.......................否\n" + console.reset)


def create_tree() -> py_trees.behaviour.Behaviour:
    """
    创建根行为及其子树。

    返回:
        根行为
    """
    every_n_success = py_trees.behaviours.SuccessEveryN("EveryN", 5)
    sequence = py_trees.composites.Sequence(name="Sequence", memory=True)
    guard = py_trees.behaviours.Success("Guard")
    periodic_success = py_trees.behaviours.Periodic("Periodic", 3)
    finisher = py_trees.behaviours.Success("Finisher")
    sequence.add_child(guard)
    sequence.add_child(periodic_success)
    sequence.add_child(finisher)
    sequence.blackbox_level = py_trees.common.BlackBoxLevel.COMPONENT
    idle = py_trees.behaviours.Success("Idle")
    root = py_trees.composites.Selector(name="Logging", memory=False)
    root.add_child(every_n_success)
    root.add_child(sequence)
    root.add_child(idle)
    return root


##############################################################################
# 主函数
##############################################################################


def main() -> None:
    """演示脚本的入口点。"""
    args = command_line_argument_parser().parse_args()
    py_trees.logging.level = py_trees.logging.Level.DEBUG
    py_trees.blackboard.Blackboard.enable_activity_stream(maximum_size=100)
    blackboard = py_trees.blackboard.Client(name="Configuration")
    blackboard.register_key(key="dude", access=py_trees.common.Access.WRITE)
    blackboard.register_key(
        key="/parameters/default_speed", access=py_trees.common.Access.EXCLUSIVE_WRITE
    )
    blackboard.dude = "Bob"
    blackboard.parameters.default_speed = 30.0

    tree = create_tree()
    print(description(tree))

    ####################
    # 渲染
    ####################
    if args.render:
        py_trees.display.render_dot_tree(tree, with_blackboard_variables=False)
        sys.exit()

    ####################
    # 树管理
    ####################
    behaviour_tree = py_trees.trees.BehaviourTree(tree)

    debug_visitor = py_trees.visitors.DebugVisitor()
    snapshot_visitor = py_trees.visitors.DisplaySnapshotVisitor()

    behaviour_tree.visitors.append(debug_visitor)
    behaviour_tree.visitors.append(snapshot_visitor)

    behaviour_tree.add_post_tick_handler(functools.partial(logger, snapshot_visitor))

    behaviour_tree.setup(timeout=15)

    ####################
    # 定时运行
    ####################
    if args.interactive:
        py_trees.console.read_single_keypress()
    while True:
        try:
            behaviour_tree.tick()
            if args.interactive:
                py_trees.console.read_single_keypress()
            else:
                time.sleep(0.5)
        except KeyboardInterrupt:
            break
    print("\n")
