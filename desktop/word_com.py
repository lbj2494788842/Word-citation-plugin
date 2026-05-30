"""
Word COM 自动化控制模块
单 COM 线程架构：所有 COM 操作在专用线程执行，避免跨线程问题
"""

import queue
import threading
import pythoncom
import win32com.client
import time


class WordController:
    """控制 Word 插入脚注（线程安全）"""

    def __init__(self):
        self.connected = False
        self._cmd_queue = queue.Queue()
        self._result_queue = queue.Queue()
        self.word = None

        # 启动专用 COM 线程
        self._com_thread = threading.Thread(target=self._com_loop, daemon=True)
        self._com_thread.start()

    # ---- 公共 API ----

    def connect(self) -> tuple[bool, str]:
        """连接到 Word"""
        return self._send_cmd("connect")

    def insert_footnote(self, text: str) -> tuple[bool, str]:
        """在光标位置插入脚注"""
        return self._send_cmd("insert_footnote", text)

    def get_status(self) -> str:
        """获取连接状态（线程安全，走 COM 队列）"""
        ok, msg = self._send_cmd("get_status")
        return msg

    # ---- 内部 ----

    def _send_cmd(self, cmd: str, *args) -> tuple[bool, str]:
        """向 COM 线程发送命令并等待结果（阻塞）"""
        self._cmd_queue.put((cmd, args))
        return self._result_queue.get()

    def _com_loop(self):
        """COM 专用线程主循环"""
        pythoncom.CoInitialize()

        while True:
            cmd, args = self._cmd_queue.get()

            try:
                if cmd == "connect":
                    result = self._do_connect()
                elif cmd == "insert_footnote":
                    result = self._do_insert_footnote(args[0])
                elif cmd == "get_status":
                    result = self._do_get_status()
                elif cmd == "stop":
                    break
                else:
                    result = (False, f"未知命令：{cmd}")
            except Exception as e:
                result = (False, f"COM 错误：{e}")

            self._result_queue.put(result)

    def _do_connect(self) -> tuple[bool, str]:
        """在 COM 线程中连接 Word"""
        # 先试 GetActiveObject（连已有实例）
        try:
            self.word = win32com.client.GetActiveObject("Word.Application")
            self.connected = True
            return True, "已连接到 Word"
        except Exception:
            pass

        # 再试 Dispatch（启动新实例）
        try:
            self.word = win32com.client.Dispatch("Word.Application")
            self.word.Visible = True
            self.connected = True
            return True, "已启动新的 Word 实例"
        except Exception as e:
            self.connected = False
            return False, f"无法连接到 Word：{e}"

    def _do_insert_footnote(self, text: str) -> tuple[bool, str]:
        """在 COM 线程中插入脚注"""
        if not self.connected or self.word is None:
            return (False, "未连接 Word，请先连接")

        try:
            doc = self.word.ActiveDocument
            if doc is None:
                return (False, "Word 中没有打开的文档")

            selection = self.word.Selection
            if selection is None:
                return (False, "无法获取 Word 光标位置")

            # 核心：插入原生脚注
            footnote = selection.Footnotes.Add(selection.Range)
            footnote.Range.Text = text

            return (True, "脚注插入成功")

        except Exception as e:
            return (False, f"插入脚注失败：{e}")

    def _do_get_status(self) -> tuple[bool, str]:
        """获取连接状态"""
        if not self.connected:
            return (False, "未连接")
        try:
            name = self.word.ActiveDocument.Name
            return (True, f"已连接 - {name}")
        except Exception:
            return (True, "已连接（无活动文档）")
