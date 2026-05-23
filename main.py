"""
「是谁在撒谎？」— PC 桌面小游戏
入口文件，启动 tkinter 窗口。
"""

import tkinter as tk
from game_ui import WhoIsLyingApp


def main():
    root = tk.Tk()
    WhoIsLyingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
