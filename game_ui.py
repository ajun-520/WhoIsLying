"""
「是谁在撒谎？」图形界面 — 侦探主题 · 三套视觉可选
基于 tkinter，无需额外依赖。
"""

import tkinter as tk
from tkinter import font as tkfont
from game_engine import GameEngine, TIME_LIMITS

FONT = "Microsoft YaHei"
W, H = 700, 600

# ============================================================
#  三套主题配色
# ============================================================
THEMES = {
    "classic": {
        "name": "经典侦探", "icon": "\U0001f50d",
        "bg": "#0d1117", "surface": "#161b22", "card": "#1c2333",
        "btn": "#212b3e", "btn_hover": "#2a3855",
        "accent": "#c9a96e", "accent_dim": "#8b7355",
        "red": "#c0392b", "green": "#27ae60", "yellow": "#f0c040",
        "text": "#e6e6e6", "text2": "#9ca3af", "border": "#2a3344",
        "glow": "#1a2235",
    },
    "night": {
        "name": "暗夜追踪", "icon": "\U0001f319",
        "bg": "#0a0e17", "surface": "#111827", "card": "#151d2e",
        "btn": "#1a2540", "btn_hover": "#243356",
        "accent": "#4da6ff", "accent_dim": "#3b6fa0",
        "red": "#e74c3c", "green": "#2ecc71", "yellow": "#f39c12",
        "text": "#e8ecf1", "text2": "#8899aa", "border": "#1e3a5f",
        "glow": "#0f1a2e",
    },
    "rose": {
        "name": "蔷薇推理", "icon": "\U0001f339",
        "bg": "#1a1124", "surface": "#1f1830", "card": "#261d38",
        "btn": "#2d2240", "btn_hover": "#3d2e56",
        "accent": "#e8739e", "accent_dim": "#9e5a7a",
        "red": "#e74c6f", "green": "#2ecc71", "yellow": "#f0c040",
        "text": "#ede6f0", "text2": "#b8a8c4", "border": "#3d2a4a",
        "glow": "#1f1630",
    },
}

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
        self.root.configure(bg=THEMES["classic"]["bg"])

        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"+{(sw - W) // 2}+{(sh - H) // 2}")

        self.engine = GameEngine()
        self.selected_mode = tk.StringVar(value="normal")
        self.selected_theme = "classic"

        self._time_left = 0.0
        self._time_limit = 10.0
        self._timer_running = False
        self._after_id = None
        self._answer_locked = False
        self._current_statements = []
        self._current_false_index = -1
        self._current_q_type = ""

        self._main_frame = tk.Frame(self.root)
        self._main_frame.pack(fill=tk.BOTH, expand=True)

        self._show_start_screen()

    @property
    def c(self):
        """快捷访问当前主题色。"""
        return THEMES[self.selected_theme]

    # ================================================================
    #  开始画面
    # ================================================================

    def _clear(self):
        for w in self._main_frame.winfo_children():
            w.destroy()

    def _refresh_bg(self):
        """根据当前主题刷新根窗口和主框架背景。"""
        bg = self.c["bg"]
        self.root.configure(bg=bg)
        self._main_frame.configure(bg=bg)

    def _show_start_screen(self):
        self._clear()
        self._refresh_bg()
        c = self.c

        # 徽章
        tk.Label(self._main_frame, text="案 件 编 号   # 2 0 2 6",
                 font=tkfont.Font(family=FONT, size=10), fg=c["accent_dim"], bg=c["bg"],
                 ).pack(pady=(40, 0))

        # 图标 + 标题
        tk.Label(self._main_frame, text=c["icon"], font=tkfont.Font(family=FONT, size=38),
                 fg=c["accent"], bg=c["bg"]).pack(pady=(6, 0))

        tk.Label(self._main_frame, text="是谁在撒谎？",
                 font=tkfont.Font(family=FONT, size=32, weight="bold"),
                 fg=c["accent"], bg=c["bg"]).pack(pady=(0, 2))

        tk.Label(self._main_frame, text="DETECTIVE  INTERROGATION",
                 font=tkfont.Font(family=FONT, size=9), fg=c["text2"], bg=c["bg"]).pack()

        # 背景故事
        sf = tk.Frame(self._main_frame, bg=c["surface"],
                       highlightbackground=c["border"], highlightthickness=1)
        sf.pack(pady=(14, 10), padx=50, fill=tk.X)
        tk.Label(sf,
                 text="城市中接连发生离奇案件。作为特别调查组的侦探，\n"
                      "你需要审讯每一位目击者 —— 他们的陈述中，\n"
                      "恰好有一句是谎言。找出说谎者，揭开案件真相。",
                 font=tkfont.Font(family=FONT, size=9), fg=c["text2"], bg=c["surface"],
                 justify=tk.CENTER, wraplength=580,
                 ).pack(pady=(12, 12))

        # ---- 主题选择 ----
        tk.Label(self._main_frame, text="界面风格",
                 font=tkfont.Font(family=FONT, size=9), fg=c["text2"], bg=c["bg"]).pack()
        theme_row = tk.Frame(self._main_frame, bg=c["bg"])
        theme_row.pack(pady=(4, 8))

        for key in ("classic", "night", "rose"):
            t = THEMES[key]
            dot = tk.Label(theme_row, text=t["icon"], font=tkfont.Font(family=FONT, size=20),
                           bg=c["bg"], fg=t["accent"], cursor="hand2")
            dot.pack(side=tk.LEFT, padx=10)
            if key == self.selected_theme:
                dot.configure(font=tkfont.Font(family=FONT, size=22, weight="bold"))
            dot.bind("<Button-1>", lambda e, k=key: self._set_theme(k))

        # ---- 模式选择 ----
        tk.Label(self._main_frame, text="选择调查模式",
                 font=tkfont.Font(family=FONT, size=10), fg=c["text2"], bg=c["bg"],
                 ).pack(pady=(0, 8))

        mode_row = tk.Frame(self._main_frame, bg=c["bg"])
        mode_row.pack()

        n_times = f"常识 {TIME_LIMITS['normal']['common']:.0f}s · 推理 {TIME_LIMITS['normal']['logic3']:.0f}s · 高难 {TIME_LIMITS['normal']['logic4']:.0f}s"
        c_times = f"常识 {TIME_LIMITS['challenge']['common']:.0f}s · 推理 {TIME_LIMITS['challenge']['logic3']:.0f}s · 高难 {TIME_LIMITS['challenge']['logic4']:.0f}s"

        self._make_mode_card(mode_row, "normal", c["icon"], "普通模式",
                             "时间充裕，轻松推理", n_times).pack(side=tk.LEFT, padx=(0, 6))
        self._make_mode_card(mode_row, "challenge", "⚡", "挑战模式",
                             "时间紧迫，极限反应", c_times).pack(side=tk.LEFT, padx=(6, 0))

        # 开始按钮
        self._make_btn(self._main_frame, "开始调查", self._start_game,
                       bg=c["accent"], fg="#1a1a1a", font_size=15, width=14, height=2,
                       ).pack(pady=(20, 0))

        tk.Label(self._main_frame, text="Python + Tkinter  |  桌面版 v2.1",
                 font=tkfont.Font(family=FONT, size=8), fg=c["text2"], bg=c["bg"],
                 ).pack(side=tk.BOTTOM, pady=12)

    def _set_theme(self, key):
        self.selected_theme = key
        self._show_start_screen()

    def _make_mode_card(self, parent, mode, icon, name, desc, times):
        c = self.c
        active = mode == self.selected_mode.get()
        bg = _lighten(c["card"]) if active else c["card"]
        bd_color = c["accent"] if active else c["border"]

        frame = tk.Frame(parent, bg=bg, cursor="hand2",
                         highlightbackground=bd_color, highlightthickness=2)
        frame.configure(width=230, height=120)
        frame.pack_propagate(False)

        tk.Label(frame, text=icon, font=tkfont.Font(family=FONT, size=20),
                 fg=c["accent"] if active else c["text2"], bg=bg).pack(pady=(14, 2))
        tk.Label(frame, text=name, font=tkfont.Font(family=FONT, size=12, weight="bold"),
                 fg=c["text"], bg=bg).pack()
        tk.Label(frame, text=desc, font=tkfont.Font(family=FONT, size=8),
                 fg=c["text2"], bg=bg).pack()
        tk.Label(frame, text=times, font=tkfont.Font(family=FONT, size=7),
                 fg=c["text2"], bg=bg).pack(pady=(2, 0))

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
        self._refresh_bg()
        c = self.c

        # 顶部栏
        top_bar = tk.Frame(self._main_frame, bg=c["surface"], height=50,
                           highlightbackground=c["border"], highlightthickness=1)
        top_bar.pack(fill=tk.X)
        top_bar.pack_propagate(False)

        self._lbl_level = tk.Label(top_bar, text="",
                                   font=tkfont.Font(family=FONT, size=11, weight="bold"),
                                   fg=c["text"], bg=c["surface"])
        self._lbl_level.pack(side=tk.LEFT, padx=20, pady=12)

        self._lbl_phase = tk.Label(top_bar, text="",
                                   font=tkfont.Font(family=FONT, size=9),
                                   fg=c["text2"], bg=c["surface"])
        self._lbl_phase.pack(side=tk.LEFT, pady=12)

        self._lbl_mode_badge = tk.Label(top_bar, text="",
                                        font=tkfont.Font(family=FONT, size=8, weight="bold"),
                                        fg=c["text"], bg=c["surface"], padx=6, pady=1)
        self._lbl_mode_badge.pack(side=tk.LEFT, padx=(8, 0), pady=12)

        self._lbl_score = tk.Label(top_bar, text="",
                                   font=tkfont.Font(family=FONT, size=11, weight="bold"),
                                   fg=c["accent"], bg=c["surface"])
        self._lbl_score.pack(side=tk.RIGHT, padx=20, pady=12)

        # 题目区
        self._question_area = tk.Frame(self._main_frame, bg=c["bg"])
        self._question_area.pack(fill=tk.BOTH, expand=True, padx=36, pady=(16, 6))

        # 计时区
        bottom_bar = tk.Frame(self._main_frame, bg=c["bg"], height=55)
        bottom_bar.pack(fill=tk.X, padx=36, pady=(0, 16))
        bottom_bar.pack_propagate(False)

        timer_header = tk.Frame(bottom_bar, bg=c["bg"])
        timer_header.pack(fill=tk.X)
        self._lbl_timer = tk.Label(timer_header, text="10.0 秒",
                                   font=tkfont.Font(family=FONT, size=14, weight="bold"),
                                   fg=c["text"], bg=c["bg"])
        self._lbl_timer.pack(side=tk.LEFT)
        self._lbl_qtype = tk.Label(timer_header, text="",
                                   font=tkfont.Font(family=FONT, size=8),
                                   fg=c["text2"], bg=c["bg"])
        self._lbl_qtype.pack(side=tk.RIGHT)

        self._bar_canvas = tk.Canvas(bottom_bar, height=7, bg=c["surface"],
                                     highlightthickness=1, highlightbackground=c["border"], bd=0)
        self._bar_canvas.pack(fill=tk.X, pady=(4, 0))

    def _load_next_question(self):
        if self._answer_locked:
            return
        c = self.c

        statements, false_index, time_limit, q_type = self.engine.next_question()
        self._current_statements = statements
        self._current_false_index = false_index
        self._current_time_limit = time_limit
        self._current_q_type = q_type

        self._lbl_level.config(text=f"第 {self.engine.level + 1} 题")
        self._lbl_score.config(text=f"得分: {self.engine.score}")
        self._lbl_phase.config(text=self.engine.phase_desc)

        mode_label = "普通" if self.engine.mode == "normal" else "挑战"
        if self.engine.mode == "normal":
            self._lbl_mode_badge.config(text=mode_label, fg=c["green"], bg="#1a3a2a")
        else:
            self._lbl_mode_badge.config(text=mode_label, fg=c["red"], bg="#3a1a1a")

        for w in self._question_area.winfo_children():
            w.destroy()

        num_opts = len(statements)
        labels = ["A", "B", "C", "D"]
        btn_font = tkfont.Font(family=FONT, size=12)

        for i, stmt in enumerate(statements):
            frame = tk.Frame(self._question_area, bg=c["btn"], cursor="hand2",
                             highlightbackground=c["border"], highlightthickness=1)

            if num_opts == 3:
                frame.pack(fill=tk.X, pady=4, ipady=11)
            else:
                r, col = i // 2, i % 2
                frame.grid(row=r, column=col, padx=4, pady=4, sticky="nsew")
                self._question_area.grid_rowconfigure(r, weight=1)
                self._question_area.grid_columnconfigure(col, weight=1)

            tk.Label(frame, text=labels[i],
                     font=tkfont.Font(family=FONT, size=12, weight="bold"),
                     fg=c["accent"], bg=c["btn"],
                     ).pack(side=tk.LEFT, padx=(16, 10), pady=8)

            tk.Label(frame, text=stmt, font=btn_font,
                     fg=c["text"], bg=c["btn"], justify=tk.LEFT, anchor=tk.W,
                     wraplength=540 if num_opts == 3 else 250,
                     ).pack(side=tk.LEFT, padx=(0, 14), pady=8, fill=tk.X, expand=True)

            frame.bind("<Button-1>", lambda e, idx=i: self._on_answer(idx))
            for child in frame.winfo_children():
                child.bind("<Button-1>", lambda e, idx=i: self._on_answer(idx))

            hover = _lighten(c["btn"])
            frame.bind("<Enter>", lambda e, f=frame: f.configure(bg=hover))
            frame.bind("<Leave>", lambda e, f=frame: f.configure(bg=c["btn"]))
            for child in frame.winfo_children():
                child.bind("<Enter>", lambda e, f=frame: f.configure(bg=hover))
                child.bind("<Leave>", lambda e, f=frame: f.configure(bg=c["btn"]))

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
        c = self.c
        self._bar_canvas.delete("all")
        w = self._bar_canvas.winfo_width()
        if w < 2:
            w = 626
        ratio = self._time_left / self._time_limit

        if ratio > 0.5:
            color = c["green"]
        elif ratio > 0.25:
            color = c["yellow"]
        else:
            color = c["red"]

        fill_w = max(0, int(w * ratio))
        if fill_w > 0:
            self._bar_canvas.create_rectangle(0, 0, fill_w, 7, fill=color, outline="", width=0)

        self._lbl_timer.config(text=f"{self._time_left:.1f} 秒")
        if ratio <= 0.25:
            self._lbl_timer.config(fg=c["red"])
        elif ratio <= 0.5:
            self._lbl_timer.config(fg=c["yellow"])
        else:
            self._lbl_timer.config(fg=c["text"])

    # ================================================================
    #  交互
    # ================================================================

    def _on_answer(self, index):
        if self._answer_locked:
            return
        self._answer_locked = True
        self._stop_timer()

        correct, score = self.engine.answer(index)
        c = self.c

        for i, w in enumerate(self._question_area.winfo_children()):
            if i == self._current_false_index:
                w.configure(bg="#0d2b1e", highlightbackground=c["green"])
            elif i == index and not correct:
                w.configure(bg="#2b0d0d", highlightbackground=c["red"])

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
        c = self.c
        for i, w in enumerate(self._question_area.winfo_children()):
            if i == self._current_false_index:
                w.configure(bg="#0d2b1e", highlightbackground=c["green"])
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
        self._refresh_bg()
        c = self.c

        tk.Label(self._main_frame, text="案 件 归 档",
                 font=tkfont.Font(family=FONT, size=10), fg=c["accent_dim"], bg=c["bg"],
                 ).pack(pady=(50, 10))

        tk.Label(self._main_frame, text="调查结束",
                 font=tkfont.Font(family=FONT, size=28, weight="bold"),
                 fg=c["red"], bg=c["bg"]).pack()

        tk.Label(self._main_frame, text=reason,
                 font=tkfont.Font(family=FONT, size=12),
                 fg=c["text2"], bg=c["bg"]).pack(pady=(4, 24))

        tk.Label(self._main_frame, text=str(self.engine.score),
                 font=tkfont.Font(family=FONT, size=50, weight="bold"),
                 fg=c["accent"], bg=c["bg"]).pack()

        tk.Label(self._main_frame, text="案件解决得分",
                 font=tkfont.Font(family=FONT, size=10),
                 fg=c["text2"], bg=c["bg"]).pack(pady=(2, 4))

        mode_label = "普通模式" if self.engine.mode == "normal" else "挑战模式"
        tk.Label(self._main_frame,
                 text=f"{mode_label}  ·  {self.engine.phase}  ·  共调查 {self.engine.level + 1} 名目击者",
                 font=tkfont.Font(family=FONT, size=9),
                 fg=c["text2"], bg=c["bg"]).pack(pady=(0, 32))

        self._make_btn(self._main_frame, "重新调查", self._start_game,
                       bg=c["accent"], fg="#1a1a1a", font_size=15, width=12, height=2,
                       ).pack(pady=(0, 8))

        self._make_btn(self._main_frame, "返回档案室", self._show_start_screen,
                       bg=c["surface"], fg=c["text"], font_size=11, width=10, height=2,
                       ).pack()

    # ================================================================
    #  工具
    # ================================================================

    def _make_btn(self, parent, text, command, *, bg, fg, font_size, width, height):
        c = self.c
        btn = tk.Frame(parent, bg=bg, cursor="hand2")
        if bg != c["accent"]:
            btn.configure(highlightbackground=c["border"], highlightthickness=1)
        btn.configure(width=width * 14, height=height * 24)
        btn.pack_propagate(False)

        lbl = tk.Label(btn, text=text,
                       font=tkfont.Font(family=FONT, size=font_size, weight="bold"),
                       fg=fg, bg=bg)
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
