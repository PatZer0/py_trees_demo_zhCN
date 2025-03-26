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
   :module: py_trees.demos.blackboard_namespaces
   :func: command_line_argument_parser
   :prog: py-trees-demo-blackboard-namespaces

.. figure:: images/blackboard_namespaces.png
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
    content = "演示黑板命名空间的使用。\n"
    content += "\n"

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
    blackboard = py_trees.blackboard.Client(name="黑板")
    blackboard.register_key(key="dude", access=py_trees.common.Access.WRITE)
    blackboard.register_key(key="/dudette", access=py_trees.common.Access.WRITE)
    blackboard.register_key(key="/foo/bar/wow", access=py_trees.common.Access.WRITE)
    print(blackboard)
    print(
        "-------------------------------------------------------------------------------"
    )
    print("$ blackboard.dude = 'Bob'")
    print("$ blackboard.dudette = 'Jade'")
    print(
        "-------------------------------------------------------------------------------"
    )
    blackboard.dude = "Bob"
    blackboard.dudette = "Jade"
    print(py_trees.display.unicode_blackboard())
    print(
        "-------------------------------------------------------------------------------"
    )
    print("$ blackboard.foo.bar.wow = 'foobar'")
    print(
        "-------------------------------------------------------------------------------"
    )
    blackboard.foo.bar.wow = "foobar"
    print(py_trees.display.unicode_blackboard())
    print(
        "-------------------------------------------------------------------------------"
    )
    print("$ py_trees.blackboard.Client(name='Foo', namespace='foo')")
    print("$ foo.register_key(key='awesome', access=py_trees.common.Access.WRITE)")
    print("$ foo.register_key(key='/brilliant', access=py_trees.common.Access.WRITE)")
    print("$ foo.register_key(key='/foo/clever', access=py_trees.common.Access.WRITE)")
    print(
        "-------------------------------------------------------------------------------"
    )
    foo = py_trees.blackboard.Client(name="Foo", namespace="foo")
    foo.register_key(key="awesome", access=py_trees.common.Access.WRITE)
    # TODO: 是否应该将/brilliant命名空间化或直接到根？
    foo.register_key(key="/brilliant", access=py_trees.common.Access.WRITE)
    # 绝对名称也可以，只要它们包含命名空间
    foo.register_key(key="/foo/clever", access=py_trees.common.Access.WRITE)
    print(foo)
    print(
        "-------------------------------------------------------------------------------"
    )
    print("$ foo.awesome = True")
    print("$ foo.set('/brilliant', False)")
    print("$ foo.clever = True")
    print(
        "-------------------------------------------------------------------------------"
    )
    foo.awesome = True
    # 只能通过set访问，因为它不在命名空间中
    foo.set("/brilliant", False)
    # 这将失败，因为它寻找命名空间化的/foo/brilliant键
    # foo.brilliant = False
    foo.clever = True
    print(py_trees.display.unicode_blackboard())
