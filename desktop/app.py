"""
Word 引用插入 - 紧凑版
无标题 · 设置弹窗 · 固定+按钮 · 水平滚动
"""

import tkinter as tk
from tkinter import messagebox
import threading

import customtkinter as ctk

from parser import parse_citations
from word_com import WordController

# ============================================================
#  设计 Token
# ============================================================
PRIMARY = "#3B82F6"
PRIMARY_HOVER = "#2563EB"
PRIMARY_LIGHT = "#EFF6FF"

BG_PAGE = "#F8FAFC"
BG_CARD = "#FFFFFF"
BG_INPUT = "#FFFFFF"
BG_RESULT = "#F1F5F9"
BG_SECONDARY = "#F1F5F9"
BG_HOVER = "#E2E8F0"

TEXT_PRIMARY = "#1E293B"
TEXT_SECONDARY = "#64748B"
TEXT_PLACEHOLDER = "#94A3B8"

BORDER_DEFAULT = "#E2E8F0"
BORDER_FOCUS = "#3B82F6"

R = 6
R_NONE = 0

S = 6
S2 = 10
S3 = 16
S4 = 24

# 基础字体（会被字号设置缩放）
F_BASE = ("Microsoft YaHei", 10)
F_SM_BASE = ("Microsoft YaHei", 9)
F_XS_BASE = ("Microsoft YaHei", 8)
F_BOLD_BASE = ("Microsoft YaHei", 10, "bold")
F_MONO_BASE = ("Consolas", 10)
F_TITLE_BASE = ("Microsoft YaHei", 13, "bold")

FONT_SIZES = {
    "小": 0.9,
    "中": 1.0,
    "大": 1.15,
}


def scale_font(font_spec, scale):
    """按比例缩放字号"""
    name = font_spec[0]
    size = font_spec[1]
    rest = font_spec[2:] if len(font_spec) > 2 else ()
    return (name, max(7, int(size * scale)), *rest)


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class CitationApp:
    """主程序"""

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Word 引用插入工具")
        self.root.geometry("380x560")
        self.root.minsize(340, 440)

        self.root.attributes("-topmost", True)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.tray_icon = None
        self._setup_tray()

        # 配置
        self.config = {
            "font_size": "中",
            "theme": "light",
        }
        self.font_scale = 1.0
        self.citations: list = []
        self.word_ctrl = WordController()
        self._btn_frames = []  # 左侧 + 按钮栏引用

        self._build_top_bar()
        self._build_input_section()
        self._build_result_section()
        self._build_footer()
        self._try_connect_word()

    # ================================================================
    #  顶部：只有状态 + 设置图标
    # ================================================================

    def _get_font(self, base):
        return scale_font(base, self.font_scale)

    def _build_top_bar(self):
        bar = ctk.CTkFrame(self.root, height=32, corner_radius=R_NONE,
                            fg_color="#F1F4F9")
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # 左：Word 状态
        ctk.CTkLabel(
            bar, text="Word：", font=F_XS_BASE, text_color=TEXT_SECONDARY,
        ).pack(side="left", padx=(S2, 2))

        self.status_label = ctk.CTkLabel(
            bar, text="检测中...", font=F_XS_BASE, text_color=TEXT_PLACEHOLDER,
        )
        self.status_label.pack(side="left")

        # 右：设置图标（最右）
        ctk.CTkButton(
            bar, text="⚙", font=("Microsoft YaHei", 13),
            fg_color="transparent", hover_color=BG_HOVER,
            text_color=TEXT_SECONDARY, width=28, height=20,
            corner_radius=R, command=self._open_settings,
        ).pack(side="right", padx=(0, S2))

        # 右：重连
        self.reconnect_btn = ctk.CTkButton(
            bar, text="重连", font=F_XS_BASE,
            fg_color=BG_SECONDARY, hover_color=BG_HOVER,
            text_color=TEXT_PRIMARY, width=44, height=20,
            corner_radius=R, command=self._try_connect_word,
        )
        self.reconnect_btn.pack(side="right", padx=(S, 0))

        # 底部分隔线
        ctk.CTkFrame(bar, height=1, corner_radius=R_NONE,
                      fg_color=BORDER_DEFAULT).pack(fill="x", side="bottom")

    # ================================================================
    #  输入区
    # ================================================================

    def _build_input_section(self):
        self.input_text = ctk.CTkTextbox(
            self.root, height=100, font=self._get_font(F_MONO_BASE),
            corner_radius=R, border_width=1,
            border_color=BORDER_DEFAULT,
            fg_color=BG_INPUT, text_color=TEXT_PRIMARY,
            padx=8, pady=8,
        )
        self.input_text.pack(fill="x", padx=S2, pady=(S, 0))
        self.input_text.bind("<FocusIn>",
                             lambda e: self.input_text.configure(border_color=BORDER_FOCUS))
        self.input_text.bind("<FocusOut>",
                             lambda e: self.input_text.configure(border_color=BORDER_DEFAULT))

        btn_row = ctk.CTkFrame(self.root, fg_color=BG_PAGE)
        btn_row.pack(fill="x", padx=S2, pady=(S, 0))

        self.parse_btn = ctk.CTkButton(
            btn_row, text="解析引用", font=self._get_font(F_BOLD_BASE),
            fg_color=PRIMARY, hover_color=PRIMARY_HOVER,
            text_color="white", height=30, width=100, corner_radius=R,
            command=self._parse,
        )
        self.parse_btn.pack(side="left")

        self.clear_btn = ctk.CTkButton(
            btn_row, text="清空内容", font=self._get_font(F_BASE),
            fg_color=BG_SECONDARY, hover_color=BG_HOVER,
            text_color=TEXT_PRIMARY, height=30, width=90, corner_radius=R,
            command=self._clear_input,
        )
        self.clear_btn.pack(side="left", padx=(S, 0))

        self.paste_btn = ctk.CTkButton(
            btn_row, text="粘贴", font=self._get_font(F_BASE),
            fg_color=BG_SECONDARY, hover_color=BG_HOVER,
            text_color=TEXT_PRIMARY, height=30, width=64, corner_radius=R,
            command=self._paste_from_clipboard,
        )
        self.paste_btn.pack(side="left", padx=(S, 0))

        self.count_label = ctk.CTkLabel(
            btn_row, text="", font=F_XS_BASE, text_color=TEXT_PLACEHOLDER,
        )
        self.count_label.pack(side="right", padx=(0, S))

    # ================================================================
    #  结果区：左侧固定 + 按钮 + 右侧可水平滚动内容
    # ================================================================

    CARD_HEIGHT = 28  # 左右单行统一高度 px
    CARD_GAP = 3      # 行间距 px

    def _build_result_section(self):
        """双栏：左固定 + 按钮 | 右可水平滚动文本"""
        container = ctk.CTkFrame(self.root, fg_color=BG_RESULT)
        container.pack(fill="both", padx=S2, pady=(S, 0), expand=True)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)

        # — 左侧固定栏（34px，不自收缩） —
        self.left_canvas = tk.Canvas(container, width=34,
                                      bg=BG_RESULT, bd=0, highlightthickness=0)
        self.left_inner = tk.Frame(self.left_canvas, bg=BG_RESULT)
        self._left_win = self.left_canvas.create_window(
            (0, 0), window=self.left_inner, anchor="nw", width=34
        )

        # — 右侧可水平滚动 —
        self.right_canvas = tk.Canvas(container,
                                       bg=BG_RESULT, bd=0, highlightthickness=0)
        # 使用 tk.Frame 避免 CTkFrame 自动收缩到 Canvas 宽度
        self.right_inner = tk.Frame(self.right_canvas, bg=BG_RESULT)
        self._right_win = self.right_canvas.create_window(
            (0, 0), window=self.right_inner, anchor="nw"
        )

        # — 垂直滚动条（两边同步） —
        def _sync_scroll(*args):
            self.left_canvas.yview(*args)
            self.right_canvas.yview(*args)

        self.v_scroll = ctk.CTkScrollbar(container, command=_sync_scroll, width=8)
        self.left_canvas.configure(yscrollcommand=self.v_scroll.set)
        self.right_canvas.configure(yscrollcommand=self.v_scroll.set)

        # — 水平滚动条（右侧，固定轨道大小） —
        self.h_scroll = ctk.CTkScrollbar(container, orientation="horizontal",
                                          command=self.right_canvas.xview, height=8)
        self.right_canvas.configure(xscrollcommand=self.h_scroll.set)
        # 固定高度让轨道始终可见
        self.h_scroll.configure(height=8)

        # grid 布局
        self.left_canvas.grid(row=0, column=0, sticky="ns")
        self.right_canvas.grid(row=0, column=1, sticky="nsew")
        self.v_scroll.grid(row=0, column=2, sticky="ns", padx=(2, 0))
        self.h_scroll.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(2, 0))

        # —— 滚轮同步滚动 ——
        def _on_mousewheel(event):
            """全局滚轮：只有当鼠标在结果区内才滚动"""
            x, y = event.x_root, event.y_root
            try:
                w = event.widget.winfo_containing(x, y)
            except Exception:
                return
            p = w
            while p and p is not container:
                try:
                    p = p.master
                except Exception:
                    break
            if p is container:
                self.left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
                self.right_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.root.bind_all("<MouseWheel>", _on_mousewheel)

        # —— 更新左右 scrollregion ——
        def _conf_left(e):
            self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))
        self.left_inner.bind("<Configure>", _conf_left)

        def _conf_right(e):
            self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all"))
            # 让 inner 保留自然宽度，不收缩到 Canvas 宽度
            req_w = self.right_inner.winfo_reqwidth()
            cw = self.right_canvas.winfo_width()
            if req_w > cw:
                self.right_canvas.itemconfig(self._right_win, width=req_w)
            else:
                self.right_canvas.itemconfig(self._right_win, width=cw)
        self.right_inner.bind("<Configure>", _conf_right)

        # 空白提示
        self.empty_label = ctk.CTkLabel(
            self.right_inner, text="在上方输入参考文献，点击「解析引用」",
            font=F_BASE, text_color=TEXT_PLACEHOLDER, fg_color=BG_RESULT,
        )
        self.empty_label.pack(pady=S4 * 2)

    # ================================================================
    #  引用卡片（左右严格同行等高）
    # ================================================================

    def _create_citation_card(self, cit):
        """在双栏同步创建行：左 + 按钮 · 右文本，高度对齐"""
        H = self.CARD_HEIGHT
        G = self.CARD_GAP

        # —— 左侧 + 按钮（place 居中） ——
        lf = tk.Frame(self.left_inner, bg=BG_RESULT, height=H)
        lf.pack(fill="x", pady=(0, G))
        lf.pack_propagate(False)

        ctk.CTkButton(
            lf, text="＋", font=("Microsoft YaHei", 11),
            fg_color=PRIMARY, hover_color=PRIMARY_HOVER,
            text_color="white", width=24, height=22,
            corner_radius=4,
            command=lambda c=cit: self._insert_footnote(c),
        ).place(relx=0.5, rely=0.5, anchor="center")

        # —— 右侧文本 ——
        rf = tk.Frame(self.right_inner, bg=BG_CARD, height=H,
                       highlightbackground=BORDER_DEFAULT, highlightthickness=1)
        rf.pack(fill="x", pady=(0, G))
        rf.pack_propagate(False)

        # 编号
        tk.Label(rf, text=f" {cit.id} ", font=("Consolas", 9, "bold"),
                  fg=PRIMARY, bg=PRIMARY_LIGHT).pack(side="left", padx=(4, 4), pady=4)

        # 文本（不截断以触发水平滚动）
        tk.Label(rf, text=cit.text, font=("Microsoft YaHei", 9),
                  fg=TEXT_PRIMARY, bg=BG_CARD, anchor="w").pack(side="left", padx=(0, 8))

    # ================================================================
    #  底部
    # ================================================================

    def _build_footer(self):
        ctk.CTkFrame(self.root, height=1, corner_radius=R_NONE,
                      fg_color=BORDER_DEFAULT).pack(fill="x", side="bottom")
        footer = ctk.CTkFrame(self.root, height=24, corner_radius=R_NONE,
                               fg_color=BG_PAGE)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        self.footer_label = ctk.CTkLabel(
            footer, text="就绪", font=F_XS_BASE, text_color=TEXT_PLACEHOLDER,
        )
        self.footer_label.pack(side="right", padx=S2)

    # ================================================================
    #  设置弹窗
    # ================================================================

    def _open_settings(self):
        win = ctk.CTkToplevel(self.root)
        win.title("设置")
        win.geometry("320x340")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()
        win.attributes("-topmost", True)

        title_font = ("Microsoft YaHei", 12, "bold")

        # ── 字体大小 ──
        y = 18
        ctk.CTkLabel(win, text="字体大小", font=title_font,
                      text_color=TEXT_PRIMARY).place(x=18, y=y)

        size_var = tk.StringVar(value=self.config["font_size"])
        sizes = ["小", "中", "大"]
        for i, sz in enumerate(sizes):
            ctk.CTkRadioButton(
                win, text=sz, variable=size_var, value=sz,
                font=F_BASE, radiobutton_width=14, radiobutton_height=14,
                command=lambda: self._apply_font_size(size_var.get()),
            ).place(x=40 + i * 80, y=y + 26)

        # ── 显示模式 ──
        y = 110
        ctk.CTkLabel(win, text="显示模式", font=title_font,
                      text_color=TEXT_PRIMARY).place(x=18, y=y)

        theme_var = tk.StringVar(value=self.config["theme"])
        themes = [("浅色", "light"), ("深色", "dark"), ("护眼", "eye")]
        cx = 40
        for label, val in themes:
            ctk.CTkRadioButton(
                win, text=label, variable=theme_var, value=val,
                font=F_BASE, radiobutton_width=14, radiobutton_height=14,
                command=lambda v=val: self._apply_theme(v),
            ).place(x=cx, y=y + 26)
            cx += 70 + (20 if val == "eye" else 0)

        # ── 更多 ──
        y = 200
        ctk.CTkLabel(win, text="—— 更多 ——", font=("Microsoft YaHei", 10),
                      text_color=TEXT_SECONDARY).place(x=18, y=y)

        y += 30
        ctk.CTkButton(
            win, text="📖  使用说明", font=F_BASE,
            fg_color=BG_SECONDARY, hover_color=BG_HOVER,
            text_color=TEXT_PRIMARY, height=28, width=160,
            corner_radius=R, anchor="w",
            command=lambda: self._show_help(),
        ).place(x=18, y=y)

        y += 40
        ctk.CTkLabel(win, text="联系：lbj@example.com",
                      font=F_XS_BASE, text_color=TEXT_PLACEHOLDER).place(x=18, y=y)

    def _apply_font_size(self, size):
        self.config["font_size"] = size
        self.font_scale = FONT_SIZES[size]
        # 只是存储，下次重建 UI 时生效
        self.footer_label.configure(text=f"字号已设为 {size}，下次启动生效")

    def _apply_theme(self, theme):
        self.config["theme"] = theme
        if theme == "dark":
            ctk.set_appearance_mode("dark")
        elif theme == "eye":
            ctk.set_appearance_mode("light")
            # 护眼模式：降低对比度，背景偏暖
            self.root.configure(fg="#F5F0E8")
        else:
            ctk.set_appearance_mode("light")

    def _show_help(self):
        messagebox.showinfo(
            "使用说明",
            "Word 引用插入工具\n\n"
            "1. 打开 Word 文档\n"
            "2. 粘贴参考文献到输入框\n"
            "3. 点击「解析引用」\n"
            "4. 点击引用左侧的 + 按钮\n"
            "5. 脚注自动插入到 Word 光标位置\n\n"
            "联系：lbj@example.com"
        )

    # ================================================================
    #  托盘
    # ================================================================

    def _setup_tray(self):
        try:
            from PIL import Image, ImageDraw
            import pystray
            img = Image.new("RGB", (64, 64), PRIMARY)
            draw = ImageDraw.Draw(img)
            draw.rectangle((14, 10, 50, 54), fill="white")
            draw.text((20, 18), "W", fill=PRIMARY)
            menu = pystray.Menu(
                pystray.MenuItem("显示窗口", self._tray_show),
                pystray.MenuItem("退出", self._tray_quit),
            )
            self.tray_icon = pystray.Icon("word_ref_insert", img,
                                           "Word 引用插入工具", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception:
            pass

    def _tray_show(self):
        self.root.after(0, self._show_window)

    def _show_window(self):
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)

    def _tray_quit(self):
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self._quit)

    def _on_close(self):
        self.root.withdraw()

    def _quit(self):
        self.root.quit()
        self.root.destroy()

    # ================================================================
    #  业务逻辑
    # ================================================================

    def _try_connect_word(self):
        self.status_label.configure(text="检测中...", text_color=TEXT_PLACEHOLDER)
        self.reconnect_btn.configure(state="disabled", text_color=TEXT_PLACEHOLDER)

        def _attempt():
            ok, msg = self.word_ctrl.connect()
            self.root.after(0, lambda: self._on_connect_result(ok, msg))

        threading.Thread(target=_attempt, daemon=True).start()

    @staticmethod
    def _truncate(text, max_len=14):
        """截断长文本，保证右侧按钮始终可见"""
        if len(text) > max_len:
            return text[:max_len-2] + ".."
        return text

    def _on_connect_result(self, ok, msg):
        self.reconnect_btn.configure(state="normal", text_color=TEXT_PRIMARY)
        if ok:
            st = self._truncate(self.word_ctrl.get_status(), 14)
            self.status_label.configure(text=f"已连接 ✓ {st}", text_color="#16A34A")
        else:
            self.status_label.configure(text="未连接", text_color="#EF4444")

    def _paste_from_clipboard(self):
        try:
            text = self.root.clipboard_get()
            if text:
                self.input_text.delete("1.0", "end")
                self.input_text.insert("1.0", text)
                self.footer_label.configure(text=f"已粘贴 {len(text)} 字符")
            else:
                self.footer_label.configure(text="剪贴板为空")
        except Exception:
            self.footer_label.configure(text="无法读取剪贴板内容")

    def _parse(self):
        text = self.input_text.get("1.0", "end-1c")
        self.citations = parse_citations(text)

        # 清空两栏
        for w in self.left_inner.winfo_children():
            w.destroy()
        for w in self.right_inner.winfo_children():
            w.destroy()

        if not self.citations:
            self.empty_label = ctk.CTkLabel(
                self.right_inner,
                text="未能解析出引用，请检查输入格式（支持 [N] 前缀）",
                font=F_BASE, text_color=TEXT_PLACEHOLDER, fg_color=BG_RESULT,
            )
            self.empty_label.pack(pady=S4 * 2)
            self.count_label.configure(text="")
            return

        for cit in self.citations:
            self._create_citation_card(cit)

        self.count_label.configure(text=f"共 {len(self.citations)} 条")

        # 让 canvas 重新计算滚动区域
        self.right_inner.update_idletasks()
        self.left_inner.update_idletasks()
        self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all"))
        self.left_canvas.configure(scrollregion=self.left_canvas.bbox("all"))

    def _insert_footnote(self, cit):
        self.footer_label.configure(text=f"正在插入 [{cit.id}] ...")
        self.root.update_idletasks()

        def _do():
            if not self.word_ctrl.connected:
                ok, msg = self.word_ctrl.connect()
                if not ok:
                    self.root.after(0, lambda: self._on_insert_fail(msg))
                    return
            try:
                ok, msg = self.word_ctrl.insert_footnote(cit.text)
                self.root.after(0, lambda: self._on_insert_result(ok, msg, cit))
            except Exception as e:
                self.root.after(
                    0, lambda: self._on_insert_result(False, f"错误：{e}", cit)
                )

        threading.Thread(target=_do, daemon=True).start()

    def _on_insert_fail(self, msg):
        self.status_label.configure(text="未连接", text_color="#EF4444")
        self.footer_label.configure(text="未连接 Word")
        messagebox.showwarning(
            "Word 未连接",
            "无法连接到 Word。\n\n请确认：\n"
            "1. Word 正在运行\n"
            "2. Word 中已打开一个文档\n\n"
            "解决后点击「重连」按钮。"
        )

    def _on_insert_result(self, ok, msg, cit=None):
        if ok:
            self.footer_label.configure(text=f"[{cit.id}] 脚注已插入 ✓")
            self.status_label.configure(text="已连接 ✓", text_color="#16A34A")
        else:
            self.footer_label.configure(text=f"插入失败：{msg}")
            self.status_label.configure(text="插入失败", text_color="#EF4444")

    def _clear_input(self):
        self.input_text.delete("1.0", "end")
        for w in self.left_inner.winfo_children():
            w.destroy()
        for w in self.right_inner.winfo_children():
            w.destroy()
        self.empty_label = ctk.CTkLabel(
            self.right_inner,
            text="在上方输入参考文献，点击「解析引用」",
            font=F_BASE, text_color=TEXT_PLACEHOLDER, fg_color=BG_RESULT,
        )
        self.empty_label.pack(pady=S4 * 2)
        self.count_label.configure(text="")
        self.citations = []
        self.right_canvas.configure(scrollregion=(0, 0, 0, 0))
        self.left_canvas.configure(scrollregion=(0, 0, 0, 0))

    def run(self):
        self.root.mainloop()


def main():
    app = CitationApp()
    app.run()


if __name__ == "__main__":
    main()
