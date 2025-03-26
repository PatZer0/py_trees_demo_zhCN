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
   :module: py_trees.demos.blackboard_remappings
   :func: command_line_argument_parser
   :prog: py-trees-demo-blackboard-remappings

.. figure:: images/blackboard_remappings.png
   :align: center

   控制台截图
"""

##############################################################################
# 导入
##############################################################################

import argparse
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
    content = "演示黑板重映射的使用。\n"
    content += "\n"
    content += "通过使用重映射的示例行为进行演示。\n"

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
    return parser


class Remap(py_trees.behaviour.Behaviour):
    """向黑板提交更复杂变量的自定义写入器。"""

    def __init__(self, name: str, remap_to: typing.Dict[str, str]):
        """
        设置黑板和重映射变量。

        参数:
            name: 行为名称
            remap_to: 重映射（从变量名到变量名）
        """
        super().__init__(name=name)
        self.logger.debug("%s.__init__()" % (self.__class__.__name__))
        self.blackboard = self.attach_blackboard_client()
        self.blackboard.register_key(
            key="/foo/bar/wow",
            access=py_trees.common.Access.WRITE,
            remap_to=remap_to["/foo/bar/wow"],
        )

    def update(self) -> py_trees.common.Status:
        """向黑板写入一个字典。

        这个行为总是返回 :data:`~py_trees.common.Status.SUCCESS`。
        """
        self.logger.debug("%s.update()" % (self.__class__.__name__))
        self.blackboard.foo.bar.wow = "colander"

        return py_trees.common.Status.SUCCESS


##############################################################################
# 主程序
##############################################################################


def main() -> None:
    """演示脚本的入口点。"""
    _ = (
        command_line_argument_parser().parse_args()
    )  # 仅配置，无需处理参数
    print(description())
    py_trees.logging.level = py_trees.logging.Level.DEBUG
    py_trees.blackboard.Blackboard.enable_activity_stream(maximum_size=100)
    root = Remap(name="重映射", remap_to={"/foo/bar/wow": "/parameters/wow"})

    ####################
    # 执行
    ####################
    root.tick_once()
    print(root.blackboard)
    print(py_trees.display.unicode_blackboard())
    print(py_trees.display.unicode_blackboard_activity_stream())
