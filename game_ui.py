"""
「是谁在撒谎？」图形界面 — 侦探主题
基于 tkinter，无需额外依赖。
"""

import tkinter as tk
from tkinter import font as tkfont
from game_engine import GameEngine, TIME_LIMITS

# ============================================================
# 配色与尺寸
# ============================================================
BG_DARK = "#0d1117"
BG_SURFACE = "#161b22"
BG_CARD = "#1c2333"
BG_BTN = "#212b3e"
BG_BTN_HOVER = "#2a3855"
GOLD = "#c9a96e"
GOLD_DIM = "#8b7355"
RED = "#c0392b"
GREEN = "#27ae60"
YELLOW = "#f0c040"
TEXT = "#e6e6e6"
TEXT2 = "#9ca3af"
BORDER = "#2a3344"
FONT = "Microsoft YaHei"

W, H = 700, 580


def _lighten(hex_color, factor=0.15):
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = min(255, int(r + (255 - r) * factor))
    g = min(255, int(g + (255 - g) * factor))
    b = min(255, int(b + (255 - b) * factor))
    return f"#{r:02x}{g:02x}{b:02x}"


class WhoIsLyingApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("是谁在撒谎？")
        self.root.geometry(f"{W}x{H}")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_DARK)

        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"+{(sw - W) // 2}+{(sh - H) // 2}")

        self.engine = GameEngine()
        self.selected_mode = tk.StringVar(value="normal")

        self._time_left = 0.0
        self._time_limit = 10.0
        self._timer_running = False
        self._after_id = None
        self._answer_locked = False
        self._current_statements = []
        self._current_false_index = -1
        self._current_q_type = ""

        self._main_frame = tk.Frame(self.root, bg=BG_DARK)
        self._main_frame.pack(fill=tk.BOTH, expand=True)

        self._show_start_screen()

    # ================================================================
    #  开始画面
    # ================================================================

    def _clear(self):
        for w in self._main_frame.winfo_children():
            w.destroy()

    def _show_start_screen(self):
        self._clear()

        # 徽章
        tk.Label(
            self._main_frame, text="案 件 编 号   # 2 0 2 6",
            font=tkfont.Font(family=FONT, size=10), fg=GOLD_DIM, bg=BG_DARK,
        ).pack(pady=(50, 0))

        # 图标 + 标题
        tk.Label(
            self._main_frame, text="\U0001f50d", font=tkfont.Font(family=FONT, size=40),
            fg=GOLD, bg=BG_DARK,
        ).pack(pady=(8, 0))

        tk.Label(
            self._main_frame, text="是谁在撒谎？",
            font=tkfont.Font(family=FONT, size=34, weight="bold"),
            fg=GOLD, bg=BG_DARK,
        ).pack(pady=(0, 2))

        tk.Label(
            self._main_frame, text="DETECTIVE  INTERROGATION",
            font=tkfont.Font(family=FONT, size=10), fg=TEXT2, bg=BG_DARK,
        ).pack()

        # 背景故事
        story_frame = tk.Frame(self._main_frame, bg=BG_SURFACE, highlightbackground=BORDER, highlightthickness=1)
        story_frame.pack(pady=(20, 16), padx=60, fill=tk.X)
        tk.Label(
            story_frame,
            text="城市中接连发生离奇案件。作为特别调查组的侦探，\n"
                 "你需要审讯每一位目击者 —— 他们的陈述中，\n"
                 "恰好有一句是谎言。找出说谎者，揭开案件真相。",
            font=tkfont.Font(family=FONT, size=10), fg=TEXT2, bg=BG_SURFACE,
            justify=tk.CENTER, wraplength=560,
        ).pack(pady=(14, 14))

        # 模式选择标签
        tk.Label(
            self._main_frame, text="选择调查模式",
            font=tkfont.Font(family=FONT, size=11), fg=TEXT2, bg=BG_DARK,
        ).pack(pady=(0, 10))

        # 模式卡片行
        mode_row = tk.Frame(self._main_frame, bg=BG_DARK)
        mode_row.pack()

        n_times = f"常识 {TIME_LIMITS['normal']['common']:.0f}s · 推理 {TIME_LIMITS['normal']['logic3']:.0f}s · 高难 {TIME_LIMITS['normal']['logic4']:.0f}s"
        c_times = f"常识 {TIME_LIMITS['challenge']['common']:.0f}s · 推理 {TIME_LIMITS['challenge']['logic3']:.0f}s · 高难 {TIME_LIMITS['challenge']['logic4']:.0f}s"

        self._make_mode_card(mode_row, "normal", "\U0001f50d", "普通模式",
                             "时间充裕，轻松推理", n_times).pack(side=tk.LEFT, padx=(0, 6))
        self._make_mode_card(mode_row, "challenge", "⚡", "挑战模式",
                             "时间紧迫，极限反应", c_times).pack(side=tk.LEFT, padx=(6, 0))

        # 开始按钮
        self._make_btn(
            self._main_frame, "开始调查", self._start_game,
            bg=GOLD, fg="#1a1a1a", font_size=16, width=14, height=2,
        ).pack(pady=(24, 0))

        tk.Label(
            self._main_frame, text="Python + Tkinter  |  桌面版 v2.0",
            font=tkfont.Font(family=FONT, size=9), fg=TEXT2, bg=BG_DARK,
        ).pack(side=tk.BOTTOM, pady=16)

    def _make_mode_card(self, parent, mode, icon, name, desc, times):
        active = mode == self.selected_mode.get()
        bg = "#1e2640" if active else BG_CARD
        bd_color = GOLD if active else BORDER

        frame = tk.Frame(parent, bg=bg, cursor="hand2",
                         highlightbackground=bd_color, highlightthickness=2)
        frame.configure(width=240, height=130)
        frame.pack_propagate(False)

        tk.Label(frame, text=icon, font=tkfont.Font(family=FONT, size=22),
                 fg=GOLD if active else TEXT2, bg=bg).pack(pady=(16, 2))
        tk.Label(frame, text=name, font=tkfont.Font(family=FONT, size=13, weight="bold"),
                 fg=TEXT, bg=bg).pack()
        tk.Label(frame, text=desc, font=tkfont.Font(family=FONT, size=9),
                 fg=TEXT2, bg=bg).pack()
        tk.Label(frame, text=times, font=tkfont.Font(family=FONT, size=8),
                 fg=TEXT2, bg=bg).pack(pady=(2, 0))

        def select(m=mode):
            self.selected_mode.set(m)
            self._show_start_screen()

        for w in [frame] + list(frame.winfo_children()):
            w.bind("<Button-1>", lambda e, m=mode: select(m))

        return frame

    # ================================================================
    #  游戏画面
    # ================================================================

    def _start_game(self):
        self.engine.reset()
        self.engine.mode = self.selected_mode.get()
        self._answer_locked = False
        self._show_game_screen()
        self._load_next_question()

    def _show_game_screen(self):
        self._clear()

        # 顶部栏
        top_bar = tk.Frame(self._main_frame, bg=BG_SURFACE, height=52,
                           highlightbackground=BORDER, highlightthickness=1)
        top_bar.pack(fill=tk.X, padx=0, pady=0)
        top_bar.pack_propagate(False)

        self._lbl_level = tk.Label(
            top_bar, text="", font=tkfont.Font(family=FONT, size=12, weight="bold"),
            fg=TEXT, bg=BG_SURFACE,
        )
        self._lbl_level.pack(side=tk.LEFT, padx=22, pady=12)

        self._lbl_phase = tk.Label(
            top_bar, text="", font=tkfont.Font(family=FONT, size=10),
            fg=TEXT2, bg=BG_SURFACE,
        )
        self._lbl_phase.pack(side=tk.LEFT, padx=(0, 0), pady=12)

        # 模式标签
        self._lbl_mode_badge = tk.Label(
            top_bar, text="", font=tkfont.Font(family=FONT, size=9, weight="bold"),
            fg=TEXT, bg=BG_SURFACE, padx=8, pady=2,
        )
        self._lbl_mode_badge.pack(side=tk.LEFT, padx=(8, 0), pady=12)

        self._lbl_score = tk.Label(
            top_bar, text="", font=tkfont.Font(family=FONT, size=12, weight="bold"),
            fg=GOLD, bg=BG_SURFACE,
        )
        self._lbl_score.pack(side=tk.RIGHT, padx=22, pady=12)

        # 题目区域
        self._question_area = tk.Frame(self._main_frame, bg=BG_DARK)
        self._question_area.pack(fill=tk.BOTH, expand=True, padx=40, pady=(18, 8))

        # 底部计时区域
        bottom_bar = tk.Frame(self._main_frame, bg=BG_DARK, height=60)
        bottom_bar.pack(fill=tk.X, padx=40, pady=(0, 18))
        bottom_bar.pack_propagate(False)

        # 计时文字行
        timer_header = tk.Frame(bottom_bar, bg=BG_DARK)
        timer_header.pack(fill=tk.X)
        self._lbl_timer = tk.Label(
            timer_header, text="10.0 秒",
            font=tkfont.Font(family=FONT, size=15, weight="bold"),
            fg=TEXT, bg=BG_DARK,
        )
        self._lbl_timer.pack(side=tk.LEFT)
        self._lbl_qtype = tk.Label(
            timer_header, text="",
            font=tkfont.Font(family=FONT, size=9), fg=TEXT2, bg=BG_DARK,
        )
        self._lbl_qtype.pack(side=tk.RIGHT)

        # 进度条
        self._bar_canvas = tk.Canvas(
            bottom_bar, height=8, bg=BG_SURFACE,
            highlightthickness=1, highlightbackground=BORDER, bd=0,
        )
        self._bar_canvas.pack(fill=tk.X, pady=(5, 0))

    def _load_next_question(self):
        if self._answer_locked:
            return

        statements, false_index, time_limit, q_type = self.engine.next_question()
        self._current_statements = statements
        self._current_false_index = false_index
        self._current_time_limit = time_limit
        self._current_q_type = q_type

        # 状态栏
        self._lbl_level.config(text=f"第 {self.engine.level + 1} 题")
        self._lbl_score.config(text=f"得分: {self.engine.score}")
        self._lbl_phase.config(text=self.engine.phase_desc)

        mode_label = "普通" if self.engine.mode == "normal" else "挑战"
        if self.engine.mode == "normal":
            self._lbl_mode_badge.config(text=mode_label, fg=GREEN, bg="#1a3a2a")
        else:
            self._lbl_mode_badge.config(text=mode_label, fg=RED, bg="#3a1a1a")

        # 清空题目区
        for w in self._question_area.winfo_children():
            w.destroy()

        num_opts = len(statements)
        labels = ["A", "B", "C", "D"]
        btn_font = tkfont.Font(family=FONT, size=12)

        for i, stmt in enumerate(statements):
            frame = tk.Frame(self._question_area, bg=BG_BTN, cursor="hand2",
                             highlightbackground=BORDER, highlightthickness=1)

            if num_opts == 3:
                frame.pack(fill=tk.X, pady=5, ipady=12)
            else:
                r, c = i // 2, i % 2
                frame.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")
                self._question_area.grid_rowconfigure(r, weight=1)
                self._question_area.grid_columnconfigure(c, weight=1)

            tk.Label(
                frame, text=labels[i],
                font=tkfont.Font(family=FONT, size=13, weight="bold"),
                fg=GOLD, bg=BG_BTN,
            ).pack(side=tk.LEFT, padx=(18, 10), pady=8)

            tk.Label(
                frame, text=stmt, font=btn_font,
                fg=TEXT, bg=BG_BTN, justify=tk.LEFT, anchor=tk.W,
                wraplength=530 if num_opts == 3 else 250,
            ).pack(side=tk.LEFT, padx=(0, 16), pady=8, fill=tk.X, expand=True)

            frame.bind("<Button-1>", lambda e, idx=i: self._on_answer(idx))
            for child in frame.winfo_children():
                child.bind("<Button-1>", lambda e, idx=i: self._on_answer(idx))

            hover_bg = _lighten(BG_BTN)
            frame.bind("<Enter>", lambda e, f=frame: f.configure(bg=hover_bg))
            frame.bind("<Leave>", lambda e, f=frame: f.configure(bg=BG_BTN))
            for child in frame.winfo_children():
                child.bind("<Enter>", lambda e, f=frame: f.configure(bg=hover_bg))
                child.bind("<Leave>", lambda e, f=frame: f.configure(bg=BG_BTN))

        # 计时器
        self._start_timer(time_limit, q_type)

    def _start_timer(self, seconds, q_type):
        self._stop_timer()
        self._time_left = seconds
        self._time_limit = seconds
        self._timer_running = True
        self._lbl_qtype.config(text=self._qtype_label(q_type))
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
            w = 618
        h = 8
        ratio = self._time_left / self._time_limit

        if ratio > 0.5:
            color = GREEN
        elif ratio > 0.25:
            color = YELLOW
        else:
            color = RED

        fill_w = max(0, int(w * ratio))
        if fill_w > 0:
            self._bar_canvas.create_rectangle(0, 0, fill_w, h, fill=color, outline="", width=0)

        self._lbl_timer.config(text=f"{self._time_left:.1f} 秒")
        if ratio <= 0.25:
            self._lbl_timer.config(fg=RED)
        elif ratio <= 0.5:
            self._lbl_timer.config(fg=YELLOW)
        else:
            self._lbl_timer.config(fg=TEXT)

    # ================================================================
    #  交互
    # ================================================================

    def _on_answer(self, index):
        if self._answer_locked:
            return
        self._answer_locked = True
        self._stop_timer()

        correct, score = self.engine.answer(index)

        for i, w in enumerate(self._question_area.winfo_children()):
            if i == self._current_false_index:
                w.configure(bg="#0d2b1e", highlightbackground=GREEN)
            elif i == index and not correct:
                w.configure(bg="#2b0d0d", highlightbackground=RED)

        if correct:
            self._lbl_score.config(text=f"得分: {score}")
            self.root.after(600, self._advance)
        else:
            self.root.after(1200, lambda: self._show_game_over("选错了证人！"))

    def _on_timeout(self):
        if self._answer_locked:
            return
        self._answer_locked = True
        self.engine.timeout()
        for i, w in enumerate(self._question_area.winfo_children()):
            if i == self._current_false_index:
                w.configure(bg="#0d2b1e", highlightbackground=GREEN)
        self.root.after(1200, lambda: self._show_game_over("时间耗尽！"))

    def _advance(self):
        self._answer_locked = False
        self._load_next_question()

    # ================================================================
    #  结算
    # ================================================================

    def _show_game_over(self, reason):
        self._stop_timer()
        self._clear()

        # 徽章
        tk.Label(
            self._main_frame, text="案 件 归 档",
            font=tkfont.Font(family=FONT, size=10), fg=GOLD_DIM, bg=BG_DARK,
        ).pack(pady=(60, 12))

        tk.Label(
            self._main_frame, text="调查结束",
            font=tkfont.Font(family=FONT, size=30, weight="bold"),
            fg=RED, bg=BG_DARK,
        ).pack()

        tk.Label(
            self._main_frame, text=reason,
            font=tkfont.Font(family=FONT, size=13),
            fg=TEXT2, bg=BG_DARK,
        ).pack(pady=(4, 28))

        tk.Label(
            self._main_frame, text=str(self.engine.score),
            font=tkfont.Font(family=FONT, size=52, weight="bold"),
            fg=GOLD, bg=BG_DARK,
        ).pack()

        tk.Label(
            self._main_frame, text="案件解决得分",
            font=tkfont.Font(family=FONT, size=11),
            fg=TEXT2, bg=BG_DARK,
        ).pack(pady=(2, 6))

        mode_label = "普通模式" if self.engine.mode == "normal" else "挑战模式"
        tk.Label(
            self._main_frame,
            text=f"{mode_label}  ·  {self.engine.phase}  ·  共调查 {self.engine.level + 1} 名目击者",
            font=tkfont.Font(family=FONT, size=10),
            fg=TEXT2, bg=BG_DARK,
        ).pack(pady=(0, 36))

        self._make_btn(
            self._main_frame, "重新调查", self._start_game,
            bg=GOLD, fg="#1a1a1a", font_size=16, width=12, height=2,
        ).pack(pady=(0, 8))

        self._make_btn(
            self._main_frame, "返回档案室", self._show_start_screen,
            bg=BG_SURFACE, fg=TEXT, font_size=12, width=10, height=2,
        ).pack()

    # ================================================================
    #  工具
    # ================================================================

    def _make_btn(self, parent, text, command, *, bg, fg, font_size, width, height):
        btn = tk.Frame(parent, bg=bg, cursor="hand2")
        if bg not in (GOLD,):
            btn.configure(highlightbackground=BORDER, highlightthickness=1)
        btn.configure(width=width * 14, height=height * 24)
        btn.pack_propagate(False)

        lbl = tk.Label(
            btn, text=text,
            font=tkfont.Font(family=FONT, size=font_size, weight="bold"),
            fg=fg, bg=bg,
        )
        lbl.pack(expand=True)

        btn.bind("<Button-1>", lambda e: command())
        lbl.bind("<Button-1>", lambda e: command())
        hover_bg = _lighten(bg)
        btn.bind("<Enter>", lambda e: btn.configure(bg=hover_bg))
        btn.bind("<Leave>", lambda e: btn.configure(bg=bg))
        lbl.bind("<Enter>", lambda e: btn.configure(bg=hover_bg))
        lbl.bind("<Leave>", lambda e: btn.configure(bg=bg))
        return btn

    @staticmethod
    def _qtype_label(q_type):
        if q_type == "common":
            return "常识判断"
        elif q_type == "logic3":
            return "三人逻辑"
        elif q_type == "logic4":
            return "四人推理"
        return ""
