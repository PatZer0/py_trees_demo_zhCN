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
   :module: py_trees.demos.stewardship
   :func: command_line_argument_parser
   :prog: py-trees-demo-tree-stewardship

.. graphviz:: dot/demo-tree-stewardship.dot

.. image:: images/tree_stewardship.gif
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
    content = "行为树管理的演示。\n\n"
    content += (
        "一个稍微不那么简单的树，使用简单的stdout预tick处理器\n"
    )
    content += "和调试及快照访问器来记录和显示\n"
    content += "树的状态。\n"
    content += "\n"
    content += "事件\n"
    content += "\n"
    content += " -  3 : 序列从运行状态切换到成功状态\n"
    content += " -  4 : 选择器的第一个子节点仅成功一次\n"
    content += " -  8 : 当其他节点都失败时，后备空闲节点启动\n"
    content += " - 14 : 第一个子节点再次启动，中止其后面正在运行的序列\n"
    content += "\n"
    if py_trees.console.has_colours:
        banner_line = console.green + "*" * 79 + "\n" + console.reset
        s = banner_line
        s += console.bold_white + "行为树".center(79) + "\n" + console.reset
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
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-r", "--render", action="store_true", help="将dot树渲染到文件"
    )
    group.add_argument(
        "--render-with-blackboard-variables",
        action="store_true",
        help="将dot树渲染到文件，包含黑板变量",
    )
    group.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="在每个tick暂停并等待按键",
    )
    return parser


def pre_tick_handler(behaviour_tree: py_trees.trees.BehaviourTree) -> None:
    """生成一个简单的预tick横幅，打印到stdout。"""
    print("\n--------- 运行 %s ---------\n" % behaviour_tree.count)


class SuccessEveryN(py_trees.behaviours.SuccessEveryN):
    """为:class:`~py_trees.behaviours.SuccessEveryN`添加黑板计数器。"""

    def __init__(self) -> None:
        """设置黑板。"""
        super().__init__(name="EveryN", n=5)
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key("count", access=py_trees.common.Access.WRITE)

    def update(self) -> py_trees.common.Status:
        """
        运行:class:`~py_trees.behaviours.SuccessEveryN`更新并写入黑板。

        返回:
            返回:class:`~py_trees.behaviours.SuccessEveryN`的:class:`~py_trees.common.Status`
        """
        status = super().update()
        self.blackboard.count = self.count
        return status


class PeriodicSuccess(py_trees.behaviours.Periodic):
    """将:class:`~py_trees.behaviours.Periodic`的周期作为变量写入黑板。"""

    def __init__(self) -> None:
        """初始化:class:`~py_trees.behaviours.Periodic`并设置黑板。"""
        super().__init__(name="Periodic", n=3)
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key("period", access=py_trees.common.Access.WRITE)

    def update(self) -> py_trees.common.Status:
        """
        运行:class:`~py_trees.behaviours.Periodic`更新并写入黑板。

        返回:
            返回:class:`~py_trees.behaviours.Periodic`的:class:`~py_trees.common.Status`
        """
        status = super().update()
        self.blackboard.period = self.period
        return status


class Finisher(py_trees.behaviour.Behaviour):
    """
    从其他行为收集黑板数据并打印摘要。

    用于树运行结束时。
    """

    def __init__(self) -> None:
        """设置黑板。"""
        super().__init__(name="Finisher")
        self.blackboard = self.attach_blackboard_client(name=self.name)
        self.blackboard.register_key("count", access=py_trees.common.Access.READ)
        self.blackboard.register_key("period", access=py_trees.common.Access.READ)

    def update(self) -> py_trees.common.Status:
        """
        获取黑板变量并打印摘要。

        返回:
            总是返回:data:`~py_trees.common.Status.SUCCESS`。
        """
        print(console.green + "---------------------------" + console.reset)
        print(console.bold + "        完成器" + console.reset)
        print(
            console.green + "  计数 : {}".format(self.blackboard.count) + console.reset
        )
        print(
            console.green
            + "  周期: {}".format(self.blackboard.period)
            + console.reset
        )
        print(console.green + "---------------------------" + console.reset)
        return py_trees.common.Status.SUCCESS


def create_tree() -> py_trees.behaviour.Behaviour:
    """
    创建根行为及其子树。

    返回:
        根行为
    """
    every_n_success = SuccessEveryN()
    sequence = py_trees.composites.Sequence(name="Sequence", memory=True)
    guard = py_trees.behaviours.Success("Guard")
    periodic_success = PeriodicSuccess()
    finisher = Finisher()
    sequence.add_child(guard)
    sequence.add_child(periodic_success)
    sequence.add_child(finisher)
    idle = py_trees.behaviours.Success("Idle")
    root = py_trees.composites.Selector(name="Demo Tree", memory=False)
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
    tree = create_tree()
    print(description())

    ####################
    # 渲染
    ####################
    if args.render:
        py_trees.display.render_dot_tree(tree)
        sys.exit()

    if args.render_with_blackboard_variables:
        py_trees.display.render_dot_tree(tree, with_blackboard_variables=True)
        sys.exit()

    ####################
    # 树管理
    ####################
    py_trees.blackboard.Blackboard.enable_activity_stream(100)
    behaviour_tree = py_trees.trees.BehaviourTree(tree)
    behaviour_tree.add_pre_tick_handler(pre_tick_handler)
    behaviour_tree.visitors.append(py_trees.visitors.DebugVisitor())
    behaviour_tree.visitors.append(
        py_trees.visitors.DisplaySnapshotVisitor(
            display_blackboard=True, display_activity_stream=True
        )
    )
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
