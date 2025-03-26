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
   :module: py_trees.demos.blackboard
   :func: command_line_argument_parser
   :prog: py-trees-demo-blackboard

.. graphviz:: dot/demo-blackboard.dot
   :align: center
   :caption: Dot图

.. figure:: images/blackboard_demo.png
   :align: center

   控制台截图
"""

##############################################################################
# 导入
##############################################################################

import argparse
import operator
import sys
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
    content = "演示黑板及相关行为的使用。\n"
    content += "\n"
    content += "一个序列被填充了几个以有趣方式\n"
    content += "在黑板上进行读写的行为。\n"

    if py_trees.console.has_colours:
        banner_line = console.green + "*" * 79 + "\n" + console.reset
        s = banner_line
        s += console.bold_white + "黑板".center(79) + "\n" + console.reset
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
    render_group = parser.add_mutually_exclusive_group()
    render_group.add_argument(
        "-r", "--render", action="store_true", help="将dot树渲染到文件"
    )
    render_group.add_argument(
        "--render-with-blackboard-variables",
        action="store_true",
        help="将dot树渲染到文件，包含黑板变量",
    )
    return parser


class Nested(object):
    """一个用于在黑板上交互的更复杂对象。"""

    def __init__(self) -> None:
        """将变量初始化为一些任意默认值。"""
        self.foo = "bar"

    def __str__(self) -> str:
        return str({"foo": self.foo})


class BlackboardWriter(py_trees.behaviour.Behaviour):
    """向黑板写入一些更有趣/复杂的类型。"""

    def __init__(self, name: str):
        """设置黑板。

        参数:
            name: 行为名称
        """
        super().__init__(name=name)
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(key="dude", access=py_trees.common.Access.READ)
        self.blackboard.register_key(
            key="spaghetti", access=py_trees.common.Access.WRITE
        )

        self.logger.debug("%s.__init__()" % (self.__class__.__name__))

    def update(self) -> py_trees.common.Status:
        """向黑板写入一个字典。

        这个行为总是返回 :data:`~py_trees.common.Status.SUCCESS`。
        """
        self.logger.debug("%s.update()" % (self.__class__.__name__))
        try:
            _ = self.blackboard.dude
        except KeyError:
            pass
        try:
            _ = self.blackboard.dudette
        except AttributeError:
            pass
        try:
            self.blackboard.dudette = "Jane"
        except AttributeError:
            pass
        self.blackboard.spaghetti = {"type": "Carbonara", "quantity": 1}
        self.blackboard.spaghetti = {"type": "Gnocchi", "quantity": 2}
        try:
            self.blackboard.set(
                "spaghetti", {"type": "Bolognese", "quantity": 3}, overwrite=False
            )
        except AttributeError:
            pass
        return py_trees.common.Status.SUCCESS


class ParamsAndState(py_trees.behaviour.Behaviour):
    """参数和状态在黑板上的存储。

    此行为演示了使用命名空间和
    多个客户端来以简洁和方便的方式
    执行参数和状态的获取和设置。
    """

    def __init__(self, name: str):
        """为参数和状态设置单独的黑板客户端。

        参数:
           name: 行为名称
        """
        super().__init__(name=name)
        # 命名空间可以包括分隔符，也可以省略
        # 它们也可以嵌套，例如 /agent/state, /agent/parameters
        self.parameters = self.attach_blackboard_client("参数", "parameters")
        self.state = self.attach_blackboard_client("状态", "state")
        self.parameters.register_key(
            key="default_speed", access=py_trees.common.Access.READ
        )
        self.state.register_key(
            key="current_speed", access=py_trees.common.Access.WRITE
        )

    def initialise(self) -> None:
        """从黑板上存储的参数变量初始化速度。"""
        try:
            self.state.current_speed = self.parameters.default_speed
        except KeyError as e:
            raise RuntimeError(
                "未找到参数 'default_speed' [{}]".format(str(e))
            )

    def update(self) -> py_trees.common.Status:
        """
        检查速度并递增，或在达到阈值时完成。

        返回:
            如果正在递增则返回 :data:`~py_trees.common.Status.RUNNING`，否则返回 :data:`~py_trees.common.Status.SUCCESS`。
        """
        if self.state.current_speed > 40.0:
            return py_trees.common.Status.SUCCESS
        else:
            self.state.current_speed += 1.0
            return py_trees.common.Status.RUNNING


def create_root() -> py_trees.behaviour.Behaviour:
    """
    创建根行为及其子树。

    返回:
        根行为
    """
    root = py_trees.composites.Sequence(name="黑板演示", memory=True)
    set_blackboard_variable = py_trees.behaviours.SetBlackboardVariable(
        name="设置嵌套",
        variable_name="nested",
        variable_value=Nested(),
        overwrite=True,
    )
    write_blackboard_variable = BlackboardWriter(name="写入器")
    check_blackboard_variable = py_trees.behaviours.CheckBlackboardVariableValue(
        name="检查嵌套Foo",
        check=py_trees.common.ComparisonExpression(
            variable="nested.foo", value="bar", operator=operator.eq
        ),
    )
    params_and_state = ParamsAndState(name="参数和状态")
    root.add_children(
        [
            set_blackboard_variable,
            write_blackboard_variable,
            check_blackboard_variable,
            params_and_state,
        ]
    )
    return root


##############################################################################
# 主程序
##############################################################################


def main() -> None:
    """演示脚本的入口点。"""
    args = command_line_argument_parser().parse_args()
    print(description())
    py_trees.logging.level = py_trees.logging.Level.DEBUG
    py_trees.blackboard.Blackboard.enable_activity_stream(maximum_size=100)
    blackboard = py_trees.blackboard.Client(name="配置")
    blackboard.register_key(key="dude", access=py_trees.common.Access.WRITE)
    blackboard.register_key(
        key="/parameters/default_speed", access=py_trees.common.Access.EXCLUSIVE_WRITE
    )
    blackboard.dude = "Bob"
    blackboard.parameters.default_speed = 30.0

    root = create_root()

    ####################
    # 渲染
    ####################
    if args.render:
        py_trees.display.render_dot_tree(root, with_blackboard_variables=False)
        sys.exit()
    if args.render_with_blackboard_variables:
        py_trees.display.render_dot_tree(root, with_blackboard_variables=True)
        sys.exit()

    ####################
    # 执行
    ####################
    root.setup_with_descendants()
    unset_blackboard = py_trees.blackboard.Client(name="取消设置者")
    unset_blackboard.register_key(key="foo", access=py_trees.common.Access.WRITE)
    print("\n--------- Tick 0 ---------\n")
    root.tick_once()
    print("\n")
    print(py_trees.display.unicode_tree(root, show_status=True))
    print("--------------------------\n")
    print(py_trees.display.unicode_blackboard())
    print("--------------------------\n")
    print(py_trees.display.unicode_blackboard(display_only_key_metadata=True))
    print("--------------------------\n")
    unset_blackboard.unset("foo")
    print(py_trees.display.unicode_blackboard_activity_stream())
