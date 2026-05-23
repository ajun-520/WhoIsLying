# 是谁在撒谎？

PC 桌面推理小游戏 — 找出唯一的假话，在倒计时结束前做出选择。

## 在线试玩

**[ajun-520.github.io/WhoIsLying](https://ajun-520.github.io/WhoIsLying/)**

纯 HTML/CSS/JS 网页版，无需下载，手机和电脑都能玩。

## 桌面版运行

```bash
# 源码运行
python main.py

# 或直接运行打包好的 exe
dist/是谁在撒谎.exe
```

纯 Python + tkinter 实现，无第三方依赖。

## 游戏截图

| 开始画面 | 游戏中 | 结算画面 |
|---------|--------|---------|
| ![开始画面](screenshots/01_start.png) | ![游戏中](screenshots/02_gameplay.png) | ![结算画面](screenshots/03_gameover.png) |

## 游戏规则

每轮显示 **3 条陈述**，其中恰好 **1 条为假**。玩家需在倒计时结束前点选假话：

- 答对：+10 分，自动进入下一题
- 答错或超时：游戏结束，显示最终得分

## 难度递进

| 关卡 | 阶段 | 题目类型 | 限时 |
|------|------|----------|------|
| 1~5 | 常识判断 | 3 条常识陈述（30+ 组题库） | 5 秒 |
| 6~10 | 逻辑推理 | 3 人逻辑谜题（4 种模板随机） | 5 秒 |
| 11+ | 高难挑战 | 40% 常识 + 60% 四人逻辑题（3 种模板） | 4 秒 |

## 项目结构

```
是谁在撒谎？/
├── index.html        # 网页版（GitHub Pages）
├── main.py           # 桌面版入口
├── game_engine.py    # 游戏引擎：题库、题目生成、计分
├── game_ui.py        # 桌面版 UI（tkinter）
├── screenshots/      # 游戏截图
└── dist/
    └── 是谁在撒谎.exe  # 打包后的独立可执行文件
```

## 打包

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "是谁在撒谎" main.py
```

输出文件在 `dist/` 目录下。
