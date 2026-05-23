"""
「是谁在撒谎？」游戏引擎
负责题目生成、状态管理、计分逻辑。
"""

import random

# ============================================================
# 常识题库：每条题目 = (陈述1, 陈述2, 陈述3, 假话索引 0/1/2)
# ============================================================

COMMON_SENSE_QUESTIONS = [
    # 自然与地理
    ("太阳从东边升起", "太阳从西边落下", "太阳绕着地球转", 2),
    ("太平洋是地球上最大的洋", "死海是地球上最低的湖泊", "撒哈拉沙漠在南美洲", 2),
    ("珠穆朗玛峰是世界最高峰", "尼罗河是世界上最长的河流", "亚马逊河在非洲", 2),
    ("地球绕太阳公转一周约365天", "地球自转一周约24小时", "地球到月球的距离约38万公里", None),  # 全部为真，需替换
    ("北极熊生活在北极", "企鹅生活在南极", "北极熊和企鹅是邻居", 2),
    ("光速约为每秒30万公里", "声速约为每秒340米", "声速比光速快", 2),
    ("月球本身不发光", "月球绕地球运行", "月球比地球大", 2),

    # 生物与人体
    ("人类正常体温约37摄氏度", "人类有两只眼睛", "人类有三个肾脏", 2),
    ("成年人有32颗恒牙", "人体最长的骨头是股骨", "人体有206块骨头", None),  # 全为真（approx），需替换
    ("蜘蛛有八条腿", "昆虫有六条腿", "蜘蛛是昆虫", 2),
    ("鲸鱼是哺乳动物", "蝙蝠是哺乳动物", "企鹅是哺乳动物", 2),
    ("猫是食肉动物", "牛是食草动物", "猪是食草动物", 2),  # 猪是杂食
    ("DNA携带遗传信息", "红细胞没有细胞核", "人体细胞都有细胞核", 2),
    ("植物通过光合作用产生氧气", "植物只在白天进行呼吸", "叶绿素使叶子呈绿色", 1),

    # 物理与化学
    ("水在100摄氏度时沸腾", "冰在0摄氏度时融化", "水在4摄氏度时密度最大", None),
    ("铁的密度比水大", "木头的密度比水小", "铁的密度比木头小", 2),
    ("黄金是电的良导体", "橡胶是绝缘体", "铜是绝缘体", 2),
    ("重力加速度约为9.8m/s²", "月球引力约为地球的1/6", "太空中没有重力", 2),
    ("H₂O是水的化学式", "CO₂是二氧化碳的化学式", "O₂是一氧化碳的化学式", 2),

    # 历史与人文
    ("第二次世界大战结束于1945年", "第一次世界大战开始于1914年", "柏林墙于1999年倒塌", 2),
    ("秦始皇统一了中国", "唐朝定都长安", "宋朝定都南京", 2),
    ("造纸术是中国古代四大发明之一", "指南针是中国古代四大发明之一", "蒸汽机是中国古代四大发明之一", 2),
    ("北京是中国的首都", "上海是中国的经济中心", "广州是中国的首都", 2),
    ("莎士比亚写了《罗密欧与朱丽叶》", "马尔克斯写了《百年孤独》", "海明威写了《战争与和平》", 2),

    # 数学与逻辑
    ("1+1=2", "2×3=6", "10÷2=3", 2),
    ("三角形内角和为180度", "正方形有四个直角", "圆形有三条边", 2),
    ("圆周率约等于3.14", "自然对数的底e约等于2.72", "圆周率恰好等于3", 2),
    ("质数只能被1和自身整除", "2是最小的质数", "1是质数", 2),

    # 食物与日常
    ("苹果富含维生素C", "香蕉富含钾", "西瓜长在树上", 2),
    ("咖啡含有咖啡因", "茶含有咖啡因", "牛奶含有咖啡因", 2),
    ("米饭的主要成分是碳水化合物", "鸡蛋富含蛋白质", "面包的主要成分是脂肪", 2),
    ("胡萝卜富含维生素A", "橙子富含维生素C", "土豆富含维生素D", 2),

    # 更多常识
    ("一年有十二个月", "一周有七天", "一年有十三个月", 2),
    ("中国的国旗是五星红旗", "美国的国旗是星条旗", "日本的国旗是太阳旗", None),
    ("万里长城在中国", "金字塔在埃及", "自由女神像在法国", None),  # 自由女神像在美国
    ("莫扎特是音乐家", "达芬奇是画家", "贝多芬是作家", 2),
    ("网球是用球拍打的", "足球是用脚踢的", "篮球是用手投的", None),

    # 补充
    ("巴西的官方语言是葡萄牙语", "阿根廷的官方语言是西班牙语", "墨西哥的官方语言是葡萄牙语", 2),
    ("南极是世界上最冷的大陆", "非洲是世界上最热的大陆", "欧洲是世界上最大的大陆", 2),  # 亚洲最大
    ("电灯的发明者是爱迪生", "电话的发明者是贝尔", "无线电的发明者是牛顿", 2),
    ("蛇是爬行动物", "青蛙是两栖动物", "乌龟是两栖动物", 2),  # 乌龟是爬行动物
    ("企鹅不会飞", "鸵鸟不会飞", "鸡不会飞", None),  # 鸡能短距离飞
    ("人的血液是红色的", "章鱼的血液是蓝色的", "所有动物的血液都是红色的", 2),
    ("声音在空气中传播需要介质", "声音不能在真空中传播", "声音在真空中传播最快", 2),
]

# 筛选出有效的题目（false_index 不为 None）
COMMON_SENSE_QUESTIONS = [q for q in COMMON_SENSE_QUESTIONS if q[3] is not None]


def _generate_logic_question():
    """生成一道逻辑推理题。三个人 A/B/C 各说一句话，恰好一人说谎。"""
    people = ["A", "B", "C"]
    liar = random.choice(people)
    t1, t2 = [p for p in people if p != liar]

    template_id = random.randint(0, 3)

    if template_id == 0:
        # 说谎者指控诚实者在说谎，诚实者互相证明
        items = [
            (f"{liar}说：{t1}在说谎", False),
            (f"{t1}说：{t2}在说真话", True),
            (f"{t2}说：{liar}在说谎", True),
        ]
    elif template_id == 1:
        # 说谎者指控诚实者，诚实者自称说真话，另一诚实者作证
        items = [
            (f"{liar}说：{t1}在说谎", False),
            (f"{t1}说：我在说真话", True),
            (f"{t2}说：{t1}在说真话", True),
        ]
    elif template_id == 2:
        # 诚实者陈述客观事实，说谎者否认，另一诚实者作证
        truth_facts = ["1+1=2", "地球绕太阳运行", "水往低处流", "一年有十二个月"]
        fact = random.choice(truth_facts)
        items = [
            (f"{liar}说：{t1}在说谎", False),
            (f"{t1}说：{fact}", True),
            (f"{t2}说：{t1}在说真话", True),
        ]
    else:
        # 说谎者声称自己在说真话（自相矛盾），诚实者揭穿
        items = [
            (f"{liar}说：我在说真话", False),
            (f"{t1}说：{t2}在说真话", True),
            (f"{t2}说：{liar}在说谎", True),
        ]

    random.shuffle(items)
    statements = [it[0] for it in items]
    false_index = next(i for i, it in enumerate(items) if not it[1])
    return statements, false_index


def _generate_hard_logic_question():
    """生成高难度逻辑题（4 条陈述，恰好 1 条假）。"""
    people = ["A", "B", "C", "D"]
    liar = random.choice(people)
    truth_tellers = [p for p in people if p != liar]

    template_id = random.randint(0, 2)
    templates = []

    if template_id == 0:
        # 说谎者指控诚实者在说谎，诚实者循环互证
        templates.append((f"{liar}说：{truth_tellers[0]}在说谎", False))
        templates.append((f"{truth_tellers[0]}说：{truth_tellers[1]}在说真话", True))
        templates.append((f"{truth_tellers[1]}说：{truth_tellers[2]}在说真话", True))
        templates.append((f"{truth_tellers[2]}说：{liar}在说谎", True))
    elif template_id == 1:
        # 说谎者自称说真话，诚实者揭穿并互相证明
        templates.append((f"{liar}说：我在说真话", False))
        templates.append((f"{truth_tellers[0]}说：{liar}在说谎", True))
        templates.append((f"{truth_tellers[1]}说：{truth_tellers[0]}在说真话", True))
        templates.append((f"{truth_tellers[2]}说：{truth_tellers[1]}在说真话", True))
    else:
        # 说谎者指控诚实者，诚实者互相证明，一人陈述客观事实
        templates.append((f"{liar}说：{truth_tellers[0]}在说谎", False))
        templates.append((f"{truth_tellers[0]}说：{truth_tellers[1]}在说真话", True))
        templates.append((f"{truth_tellers[1]}说：我想的和{truth_tellers[0]}一样", True))
        truth_facts = ["1+1=2", "地球绕太阳运行", "一年有十二个月", "三角形内角和为180度"]
        templates.append((f"{truth_tellers[2]}说：{random.choice(truth_facts)}", True))

    random.shuffle(templates)
    statements = [t[0] for t in templates]
    false_index = next(i for i, t in enumerate(templates) if not t[1])
    return statements, false_index


class GameEngine:
    """游戏引擎：管理题目生成、状态和计分。"""

    def __init__(self):
        self.level = 0
        self.score = 0
        self.current_question = None  # (statements, false_index, num_options)
        self._used_common_sense = []  # 已使用的常识题索引，避免短期重复

    # ----- 对外接口 -----

    def next_question(self):
        """生成下一道题，返回 (statements, false_index, time_limit)。"""
        if self.level < 5:
            question = self._gen_common_sense()
            time_limit = 5.0
        elif self.level < 10:
            question = self._gen_logic()
            time_limit = 5.0
        else:
            question = self._gen_hard()
            time_limit = 4.0

        self.current_question = question
        return (question[0], question[1], time_limit)

    def answer(self, index: int):
        """处理玩家选择，返回 (正确?, 得分)。"""
        if self.current_question is None:
            return False, 0
        false_index = self.current_question[1]
        if index == false_index:
            self.level += 1
            self.score += 10
            self.current_question = None
            return True, self.score
        else:
            self.current_question = None
            return False, self.score

    def timeout(self):
        """超时处理，返回当前得分。"""
        self.current_question = None
        return self.score

    def reset(self):
        """重置游戏状态。"""
        self.level = 0
        self.score = 0
        self.current_question = None
        self._used_common_sense.clear()

    # ----- 题目生成 -----

    def _gen_common_sense(self):
        """从常识题库中选题，优先选未用过的。"""
        available = [i for i in range(len(COMMON_SENSE_QUESTIONS))
                     if i not in self._used_common_sense]
        if not available:
            self._used_common_sense.clear()
            available = list(range(len(COMMON_SENSE_QUESTIONS)))

        idx = random.choice(available)
        self._used_common_sense.append(idx)

        q = COMMON_SENSE_QUESTIONS[idx]
        statements = list(q[:3])
        false_index = q[3]
        # 随机打乱陈述顺序
        shuffled = list(enumerate(statements))
        random.shuffle(shuffled)
        new_false_index = next(i for i, (orig_idx, _) in enumerate(shuffled) if orig_idx == false_index)
        statements = [s for _, s in shuffled]
        return (statements, new_false_index, 3)

    def _gen_logic(self):
        """生成逻辑题。"""
        statements, false_index = _generate_logic_question()
        return (statements, false_index, 3)

    def _gen_hard(self):
        """生成高难度题：40% 常识（但限时更紧），60% 4人逻辑题。"""
        if random.random() < 0.4:
            # 常识题，但时间压力更大（由调用方设置 4 秒）
            return self._gen_common_sense()
        else:
            statements, false_index = _generate_hard_logic_question()
            shuffled = list(enumerate(statements))
            random.shuffle(shuffled)
            new_false_index = next(i for i, (orig_idx, _) in enumerate(shuffled) if orig_idx == false_index)
            statements = [s for _, s in shuffled]
            return (statements, new_false_index, 4)

    @property
    def difficulty_phase(self):
        """当前难度阶段描述。"""
        if self.level < 5:
            return "常识判断"
        elif self.level < 10:
            return "逻辑推理"
        else:
            return "高难挑战"
