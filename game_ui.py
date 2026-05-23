"""
「是谁在撒谎？」图形界面
基于 tkinter，无需额外依赖。
"""

import tkinter as tk
from tkinter import font as tkfont
from game_engine import GameEngine

# ============================================================
# 配色与尺寸常量
# ============================================================
BG_DARK = "#1a1a2e"
BG_CARD = "#16213e"
BG_BUTTON = "#0f3460"
BG_BUTTON_HOVER = "#1a508b"
ACCENT_RED = "#e94560"
ACCENT_GREEN = "#00b894"
ACCENT_YELLOW = "#fdcb6e"
TEXT_PRIMARY = "#dfe6e9"
TEXT_SECONDARY = "#b2bec3"
FONT_FAMILY = "Microsoft YaHei"

WINDOW_WIDTH = 700
WINDOW_HEIGHT = 550


class WhoIsLyingApp:
    """游戏主应用"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("是谁在撒谎？")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_DARK)

        # 居中窗口
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - WINDOW_WIDTH) // 2
        y = (sh - WINDOW_HEIGHT) // 2
        self.root.geometry(f"+{x}+{y}")

        self.engine = GameEngine()

        # 定时器相关
        self._time_left = 0.0
        self._timer_running = False
        self._after_id = None
        self._answer_locked = False  # 防止重复点击

        # 当前题目数据
        self._current_statements = []
        self._current_false_index = -1
        self._current_time_limit = 5.0

        # 界面容器
        self._main_frame = tk.Frame(self.root, bg=BG_DARK)
        self._main_frame.pack(fill=tk.BOTH, expand=True)

        self._show_start_screen()

    # ================================================================
    #  开始画面
    # ================================================================

    def _clear(self):
        """清空主容器。"""
        for w in self._main_frame.winfo_children():
            w.destroy()

    def _show_start_screen(self):
        self._clear()

        # 标题
        title_font = tkfont.Font(family=FONT_FAMILY, size=36, weight="bold")
        tk.Label(
            self._main_frame, text="是谁在撒谎？", font=title_font,
            fg=ACCENT_RED, bg=BG_DARK,
        ).pack(pady=(120, 10))

        # 副标题
        sub_font = tkfont.Font(family=FONT_FAMILY, size=14)
        tk.Label(
            self._main_frame,
            text="每轮 3 条陈述，找出唯一的假话！\n5 秒倒计时，答对加分，答错出局。",
            font=sub_font, fg=TEXT_SECONDARY, bg=BG_DARK, justify=tk.CENTER,
        ).pack(pady=(0, 50))

        # 开始按钮
        self._make_btn(
            self._main_frame, "开始游戏", self._start_game,
            bg=ACCENT_RED, fg="white", font_size=18, width=14, height=2,
        ).pack()

        # 底部版本信息
        tk.Label(
            self._main_frame, text="v1.0  |  Python + Tkinter",
            font=tkfont.Font(family=FONT_FAMILY, size=9),
            fg=TEXT_SECONDARY, bg=BG_DARK,
        ).pack(side=tk.BOTTOM, pady=20)

    # ================================================================
    #  游戏画面
    # ================================================================

    def _start_game(self):
        self.engine.reset()
        self._answer_locked = False
        self._show_game_screen()
        self._load_next_question()

    def _show_game_screen(self):
        self._clear()

        # --- 顶部状态栏 ---
        top_bar = tk.Frame(self._main_frame, bg=BG_CARD, height=60)
        top_bar.pack(fill=tk.X, padx=0, pady=0)
        top_bar.pack_propagate(False)

        # 关卡
        self._lbl_level = tk.Label(
            top_bar, text="", font=tkfont.Font(family=FONT_FAMILY, size=13, weight="bold"),
            fg=TEXT_PRIMARY, bg=BG_CARD,
        )
        self._lbl_level.pack(side=tk.LEFT, padx=25, pady=15)

        # 得分
        self._lbl_score = tk.Label(
            top_bar, text="", font=tkfont.Font(family=FONT_FAMILY, size=13, weight="bold"),
            fg=ACCENT_YELLOW, bg=BG_CARD,
        )
        self._lbl_score.pack(side=tk.RIGHT, padx=25, pady=15)

        # 阶段标签
        self._lbl_phase = tk.Label(
            top_bar, text="", font=tkfont.Font(family=FONT_FAMILY, size=11),
            fg=TEXT_SECONDARY, bg=BG_CARD,
        )
        self._lbl_phase.pack(side=tk.RIGHT, padx=(0, 10), pady=15)

        # --- 中间留白区域（放置题目） ---
        self._question_area = tk.Frame(self._main_frame, bg=BG_DARK)
        self._question_area.pack(fill=tk.BOTH, expand=True, padx=40, pady=(20, 10))

        # --- 底部倒计时区域 ---
        bottom_bar = tk.Frame(self._main_frame, bg=BG_DARK, height=70)
        bottom_bar.pack(fill=tk.X, padx=40, pady=(0, 20))
        bottom_bar.pack_propagate(False)

        # 倒计时文字
        self._lbl_timer = tk.Label(
            bottom_bar, text="5.0 秒", font=tkfont.Font(family=FONT_FAMILY, size=16, weight="bold"),
            fg=TEXT_PRIMARY, bg=BG_DARK,
        )
        self._lbl_timer.pack(anchor=tk.W, pady=(0, 5))

        # 倒计时进度条背景
        self._bar_canvas = tk.Canvas(
            bottom_bar, height=12, bg=BG_CARD, highlightthickness=0, bd=0,
        )
        self._bar_canvas.pack(fill=tk.X)
        self._bar_rect = None

    def _load_next_question(self):
        if self._answer_locked:
            return

        statements, false_index, time_limit = self.engine.next_question()
        self._current_statements = statements
        self._current_false_index = false_index
        self._current_time_limit = time_limit

        # 更新状态栏
        self._lbl_level.config(text=f"第 {self.engine.level + 1} 题")
        self._lbl_score.config(text=f"得分: {self.engine.score}")
        self._lbl_phase.config(text=self.engine.difficulty_phase)

        # 清空题目区域
        for w in self._question_area.winfo_children():
            w.destroy()

        # 根据选项数量决定布局
        num_opts = len(statements)
        if num_opts == 3:
            cols = 1
        else:
            cols = 2  # 4 选项时用 2×2 网格

        btn_font = tkfont.Font(family=FONT_FAMILY, size=13)

        # 字母标签
        labels = ["A", "B", "C", "D"]

        for i, stmt in enumerate(statements):
            frame = tk.Frame(self._question_area, bg=BG_BUTTON, cursor="hand2")
            # 布局
            if cols == 1:
                frame.pack(fill=tk.X, pady=6, ipady=12)
            else:
                r = i // 2
                c = i % 2
                frame.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")
                self._question_area.grid_rowconfigure(r, weight=1)
                self._question_area.grid_columnconfigure(c, weight=1)

            # 标签字母
            tk.Label(
                frame, text=labels[i], font=tkfont.Font(family=FONT_FAMILY, size=14, weight="bold"),
                fg=ACCENT_RED, bg=BG_BUTTON,
            ).pack(side=tk.LEFT, padx=(20, 10), pady=8)

            # 陈述文本
            tk.Label(
                frame, text=stmt, font=btn_font,
                fg=TEXT_PRIMARY, bg=BG_BUTTON, justify=tk.LEFT,
                anchor=tk.W, wraplength=550 if cols == 1 else 260,
            ).pack(side=tk.LEFT, padx=(0, 20), pady=8, fill=tk.X, expand=True)

            # 绑定点击
            frame.bind("<Button-1>", lambda e, idx=i: self._on_answer(idx))
            for child in frame.winfo_children():
                child.bind("<Button-1>", lambda e, idx=i: self._on_answer(idx))

            # 悬停效果
            frame.bind("<Enter>", lambda e, f=frame: f.configure(bg=BG_BUTTON_HOVER))
            frame.bind("<Leave>", lambda e, f=frame: f.configure(bg=BG_BUTTON))
            for child in frame.winfo_children():
                child.bind("<Enter>", lambda e, f=frame: f.configure(bg=BG_BUTTON_HOVER))
                child.bind("<Leave>", lambda e, f=frame: f.configure(bg=BG_BUTTON))

        # 启动倒计时
        self._start_timer(time_limit)

    def _start_timer(self, seconds: float):
        self._stop_timer()
        self._time_left = seconds
        self._timer_running = True
        self._draw_timer_bar()
        self._tick()

    def _stop_timer(self):
        self._timer_running = False
        if self._after_id is not None:
            self.root.after_cancel(self._after_id)
            self._after_id = None

    def _tick(self):
        if not self._timer_running:
            return
        self._time_left -= 0.05
        if self._time_left <= 0:
            self._time_left = 0
            self._timer_running = False
            self._draw_timer_bar()
            self._on_timeout()
            return
        self._draw_timer_bar()
        self._after_id = self.root.after(50, self._tick)

    def _draw_timer_bar(self):
        self._bar_canvas.delete("all")
        w = self._bar_canvas.winfo_width()
        if w < 2:
            w = 620
        h = 12
        ratio = self._time_left / self._current_time_limit

        # 颜色根据剩余时间变化
        if ratio > 0.5:
            color = ACCENT_GREEN
        elif ratio > 0.25:
            color = ACCENT_YELLOW
        else:
            color = ACCENT_RED

        fill_w = int(w * ratio)
        self._bar_canvas.create_rectangle(0, 0, fill_w, h, fill=color, outline="", width=0)

        # 更新文字
        self._lbl_timer.config(text=f"{self._time_left:.1f} 秒")
        if ratio <= 0.25:
            self._lbl_timer.config(fg=ACCENT_RED)
        elif ratio <= 0.5:
            self._lbl_timer.config(fg=ACCENT_YELLOW)
        else:
            self._lbl_timer.config(fg=TEXT_PRIMARY)

    # ================================================================
    #  交互处理
    # ================================================================

    def _on_answer(self, index: int):
        if self._answer_locked:
            return
        self._answer_locked = True
        self._stop_timer()

        correct, score = self.engine.answer(index)

        # 高亮正确答案和玩家选择
        for i, w in enumerate(self._question_area.winfo_children()):
            if i == self._current_false_index:
                w.configure(bg="#004d40")  # 深绿 — 正确答案
            elif i == index and not correct:
                w.configure(bg="#6a1b1b")  # 深红 — 选错了

        if correct:
            self._lbl_score.config(text=f"得分: {score}")
            # 短暂显示反馈后加载下一题
            self.root.after(600, self._advance)
        else:
            self.root.after(1200, lambda: self._show_game_over("选择错误！"))

    def _on_timeout(self):
        if self._answer_locked:
            return
        self._answer_locked = True
        self.engine.timeout()
        # 高亮正确答案
        for i, w in enumerate(self._question_area.winfo_children()):
            if i == self._current_false_index:
                w.configure(bg="#004d40")
        self.root.after(1200, lambda: self._show_game_over("时间到！"))

    def _advance(self):
        self._answer_locked = False
        self._load_next_question()

    # ================================================================
    #  结算画面
    # ================================================================

    def _show_game_over(self, reason: str):
        self._stop_timer()
        self._clear()

        # 标题
        tk.Label(
            self._main_frame, text="游戏结束",
            font=tkfont.Font(family=FONT_FAMILY, size=32, weight="bold"),
            fg=ACCENT_RED, bg=BG_DARK,
        ).pack(pady=(80, 10))

        tk.Label(
            self._main_frame, text=reason,
            font=tkfont.Font(family=FONT_FAMILY, size=14),
            fg=TEXT_SECONDARY, bg=BG_DARK,
        ).pack(pady=(0, 40))

        # 得分展示
        score_font = tkfont.Font(family=FONT_FAMILY, size=48, weight="bold")
        tk.Label(
            self._main_frame, text=str(self.engine.score),
            font=score_font, fg=ACCENT_YELLOW, bg=BG_DARK,
        ).pack()

        tk.Label(
            self._main_frame, text="最终得分",
            font=tkfont.Font(family=FONT_FAMILY, size=13),
            fg=TEXT_SECONDARY, bg=BG_DARK,
        ).pack(pady=(0, 5))

        # 到达关卡
        tk.Label(
            self._main_frame,
            text=f"到达第 {self.engine.level + 1} 题  |  难度: {self.engine.difficulty_phase}",
            font=tkfont.Font(family=FONT_FAMILY, size=11),
            fg=TEXT_SECONDARY, bg=BG_DARK,
        ).pack(pady=(5, 40))

        # 再玩一次
        self._make_btn(
            self._main_frame, "再玩一次", self._start_game,
            bg=ACCENT_RED, fg="white", font_size=16, width=12, height=2,
        ).pack(pady=(0, 10))

        # 返回主页
        self._make_btn(
            self._main_frame, "返回首页", self._show_start_screen,
            bg=BG_CARD, fg=TEXT_PRIMARY, font_size=13, width=10, height=2,
        ).pack()

    # ================================================================
    #  工具方法
    # ================================================================

    def _make_btn(self, parent, text, command, *, bg, fg, font_size, width, height):
        """创建统一样式的按钮。"""
        btn = tk.Frame(parent, bg=bg, cursor="hand2")
        btn.configure(width=width * 15, height=height * 25)
        btn.pack_propagate(False)

        lbl = tk.Label(
            btn, text=text, font=tkfont.Font(family=FONT_FAMILY, size=font_size, weight="bold"),
            fg=fg, bg=bg,
        )
        lbl.pack(expand=True)

        btn.bind("<Button-1>", lambda e: command())
        lbl.bind("<Button-1>", lambda e: command())
        btn.bind("<Enter>", lambda e: btn.configure(bg=self._lighten(bg)))
        btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
        lbl.bind("<Enter>", lambda e: btn.configure(bg=self._lighten(bg)))
        lbl.bind("<Leave>", lambda e: btn.configure(bg=bg))

        return btn

    @staticmethod
    def _lighten(hex_color: str, factor: float = 0.15) -> str:
        """将 hex 颜色变亮一点。"""
        hex_color = hex_color.lstrip("#")
        r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02x}{g:02x}{b:02x}"
