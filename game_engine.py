"""
「是谁在撒谎？」游戏引擎
负责题目生成、状态管理、计分逻辑。
支持普通模式（时间充裕）和挑战模式（极限反应）。
"""

import random

# ============================================================
# 常识题库：每组 = (陈述1, 陈述2, 陈述3, 假话索引 0/1/2)
# 共 70 组，分布：科学自然 23 + 历史人文 13 + 日常逻辑 14 + 侦探犯罪 15 + 补充 5
# ============================================================

COMMON_SENSE_QUESTIONS = [
    # ============ 科学自然 (23) ============
    # 天文地理
    ("太阳从东边升起", "太阳从西边落下", "太阳绕着地球转", 2),
    ("太阳是一颗恒星", "火星是太阳系中的一颗行星", "太阳是一颗行星", 2),
    ("喜马拉雅山脉仍在缓慢升高", "死海位于海平面以下", "珠穆朗玛峰每年在明显降低", 2),
    ("太平洋是地球上最大的洋", "死海是地球上最低的湖泊", "撒哈拉沙漠在南美洲", 2),
    ("珠穆朗玛峰是世界最高峰", "尼罗河是世界上最长的河流", "亚马逊河在非洲", 2),
    ("北极熊生活在北极", "企鹅生活在南极", "北极熊和企鹅是邻居", 2),
    ("地球大气中含量最多的气体是氮气", "氧气约占地球大气的21%", "地球大气中含量最多的气体是氧气", 2),
    ("南极是世界上最冷的大陆", "非洲是世界上最热的大陆", "欧洲是世界上最大的大陆", 2),
    # 物理化学
    ("光速约为每秒30万公里", "声速约为每秒340米", "声速比光速快", 2),
    ("月球本身不发光", "月球绕地球运行", "月球比地球大", 2),
    ("铁的密度比水大", "木头的密度比水小", "铁的密度比木头小", 2),
    ("黄金是电的良导体", "橡胶是绝缘体", "铜是绝缘体", 2),
    ("重力加速度约为9.8m/s²", "月球引力约为地球的1/6", "太空中没有重力", 2),
    ("H₂O是水的化学式", "CO₂是二氧化碳的化学式", "O₂是一氧化碳的化学式", 2),
    ("声音在空气中传播需要介质", "声音不能在真空中传播", "声音在真空中传播最快", 2),
    # 生物人体
    ("人类正常体温约37摄氏度", "人类有两只眼睛", "人类有三个肾脏", 2),
    ("人体最大的器官是皮肤", "肝脏是人体最大的内脏器官", "心脏是人体最大的内脏器官", 2),
    ("人的胃中有胃酸帮助消化食物", "人体小肠是吸收营养的主要场所", "人体大肠是吸收营养的主要场所", 2),
    ("蜘蛛有八条腿", "昆虫有六条腿", "蜘蛛是昆虫", 2),
    ("鲸鱼是哺乳动物", "蝙蝠是哺乳动物", "企鹅是哺乳动物", 2),
    ("鸭嘴兽是卵生的哺乳动物", "蝙蝠是唯一会飞的哺乳动物", "所有哺乳动物都是胎生的", 2),
    ("大象是陆地上现存最大的动物", "蓝鲸是地球上现存最大的动物", "大象比蓝鲸更大", 2),
    ("DNA携带遗传信息", "红细胞没有细胞核", "人体细胞都有细胞核", 2),

    # ============ 历史人文 (13) ============
    ("第二次世界大战结束于1945年", "第一次世界大战开始于1914年", "柏林墙于1999年倒塌", 2),
    ("秦始皇统一了中国", "唐朝定都长安", "宋朝定都南京", 2),
    ("造纸术是中国古代四大发明之一", "指南针是中国古代四大发明之一", "蒸汽机是中国古代四大发明之一", 2),
    ("北京是中国的首都", "上海是中国的经济中心", "广州是中国的首都", 2),
    ("莎士比亚写了《罗密欧与朱丽叶》", "马尔克斯写了《百年孤独》", "海明威写了《战争与和平》", 2),
    ("莫扎特是音乐家", "达芬奇是画家", "贝多芬是作家", 2),
    ("《蒙娜丽莎》是达芬奇的作品", "梵高是荷兰画家", "《蒙娜丽莎》的作者是梵高", 2),
    ("奥林匹克运动会起源于古希腊", "马拉松长跑的距离约为42公里", "马拉松的距离是100公里", 2),
    ("围棋起源于中国", "国际象棋起源于印度", "国际象棋起源于中国", 2),
    ("《论语》记录了孔子的言行", "《史记》的作者是司马迁", "《史记》的作者是孔子", 2),
    ("交响乐通常由管弦乐队演奏", "莫扎特是古典主义时期的作曲家", "莫扎特是浪漫主义时期的作曲家", 2),
    ("巴西的官方语言是葡萄牙语", "阿根廷的官方语言是西班牙语", "墨西哥的官方语言是葡萄牙语", 2),
    ("电灯的发明者是爱迪生", "电话的发明者是贝尔", "无线电的发明者是牛顿", 2),

    # ============ 日常逻辑 (14) ============
    # 数学
    ("1+1=2", "2×3=6", "10÷2=3", 2),
    ("三角形内角和为180度", "正方形有四个直角", "圆形有三条边", 2),
    ("圆周率约等于3.14", "自然对数的底e约等于2.72", "圆周率恰好等于3", 2),
    ("质数只能被1和自身整除", "2是最小的质数", "1是质数", 2),
    # 食物
    ("苹果富含维生素C", "香蕉富含钾", "西瓜长在树上", 2),
    ("咖啡含有咖啡因", "茶含有咖啡因", "牛奶含有咖啡因", 2),
    ("米饭的主要成分是碳水化合物", "鸡蛋富含蛋白质", "面包的主要成分是脂肪", 2),
    ("胡萝卜富含维生素A", "橙子富含维生素C", "土豆富含维生素D", 2),
    ("食盐的主要成分是氯化钠", "醋的主要成分是醋酸", "食盐的主要成分是碳酸钠", 2),
    # 生活科技
    ("手机屏幕发出蓝光可能影响睡眠", "每天适量运动有益于健康", "长时间看手机不会对眼睛造成任何影响", 2),
    ("冰箱通过制冷剂循环来保持低温", "微波炉通过微波使食物水分子振动加热", "微波炉是通过火焰来加热食物的", 2),
    ("维生素C有助于增强免疫力", "缺钙可能导致骨质疏松", "多喝可乐可以补钙", 2),
    ("WiFi信号可以穿墙传输", "蓝牙的传输距离通常比WiFi短", "蓝牙的传输距离比WiFi更远", 2),
    ("交通信号灯中红灯表示停止", "绿灯表示可以通行", "黄灯表示加速通过", 2),

    # ============ 侦探犯罪 (15) ============
    ("福尔摩斯是柯南·道尔创作的虚构角色", "指纹具有唯一性，每个人的指纹都不相同", "福尔摩斯是真实存在的历史人物", 2),
    ("DNA检测可用于锁定犯罪嫌疑人", "测谎仪通过检测生理指标来判断是否说谎", "测谎仪的准确率是100%", 2),
    ("不在场证明可以帮助嫌疑人排除嫌疑", "警察审讯时会记录嫌疑人的口供", "只要嫌疑人自己认罪，不需要其他证据就能定罪", 2),
    ("阿加莎·克里斯蒂是著名的侦探小说作家", "密室杀人是侦探小说中的经典推理类型", "《福尔摩斯探案集》的作者是阿加莎·克里斯蒂", 2),
    ("法医可以通过尸检确定死因", "监控录像是刑事侦查中的重要证据", "所有犯罪现场都会留下指纹", 2),
    ("人说谎时可能出现微表情变化", "逻辑上自相矛盾的陈述必然为假", "证词前后完全一致就说明一定是真话", 2),
    ("弹道分析可以确定子弹来自哪把枪", "目击者证词可能受到记忆偏差的影响", "所有的侦探都是警察", 2),
    ("犯罪现场需要保护不被破坏", "推理分为演绎推理和归纳推理两种类型", "演绎推理的结论一定100%正确", 2),
    ("笔迹鉴定可以用于识别伪造签名", "监控摄像头拍到的人脸可作为证据", "只要戴上口罩，监控就完全无法识别人脸", 2),
    ("真话和假话在逻辑上不能同时为真", "说谎的人通常需要记住自己编造的假话", "说谎的人眼睛一定会往右上方看", 2),
    ("不在场证明需要时间地点人证三个要素", "被告人有权保持沉默", "被告人保持沉默就等于默认有罪", 2),
    ("脚印是犯罪现场常见的物证", "DNA存在于人的血液唾液和头发中", "DNA鉴定只需要一根头发就能100%确定凶手", 2),
    ("侦探小说中红鲱鱼是一种转移注意力的误导线索", "本格派推理注重公平地向读者提供线索", "所有侦探小说的结局都是凶手自杀", 2),
    ("法医人类学可通过骨骼判断死者年龄和性别", "刑侦画像师可根据目击者描述画出嫌疑人肖像", "一群人指认同一个嫌疑人就说明一定是罪犯", 2),
    ("测谎结果在大多数国家的法庭上不能单独作为定罪证据", "间接证据需要多个相互印证才能形成证据链", "法庭上只要测谎仪显示说谎就可以直接定罪", 2),

    # ============ 补充杂项 (5) ============
    ("一年有十二个月", "一周有七天", "一年有十三个月", 2),
    ("猫是食肉动物", "牛是食草动物", "猪是食草动物", 2),
    ("植物通过光合作用产生氧气", "叶绿素使叶子呈绿色", "植物只在白天进行呼吸", 2),
    ("蛇是爬行动物", "青蛙是两栖动物", "乌龟是两栖动物", 2),
    ("人的血液是红色的", "章鱼的血液是蓝色的", "所有动物的血液都是红色的", 2),
]

# 共 70 题，无需过滤 None

# ============================================================
# 每类题型的独立计时 (普通模式 / 挑战模式)
# ============================================================
TIME_LIMITS = {
    "normal":    {"common": 8.0, "logic3": 10.0, "logic4": 12.0},
    "challenge": {"common": 5.0, "logic3":  5.0, "logic4":  4.0},
}


def _generate_logic_question():
    """生成一道逻辑推理题。三个人 A/B/C 各说一句话，恰好一人说谎。"""
    people = ["A", "B", "C"]
    liar = random.choice(people)
    t1, t2 = [p for p in people if p != liar]
    template_id = random.randint(0, 5)  # 6 套模板

    if template_id == 0:
        # 说谎者指控诚实者，诚实者互相证明
        items = [
            (f"{liar}说：{t1}在说谎", False),
            (f"{t1}说：{t2}在说真话", True),
            (f"{t2}说：{liar}在说谎", True),
        ]
    elif template_id == 1:
        # 说谎者指控诚实者，诚实者自称说真话
        items = [
            (f"{liar}说：{t1}在说谎", False),
            (f"{t1}说：我在说真话", True),
            (f"{t2}说：{t1}在说真话", True),
        ]
    elif template_id == 2:
        # 诚实者陈述客观事实，说谎者否认
        truth_facts = ["1+1=2", "地球绕太阳运行", "水往低处流", "一年有十二个月"]
        items = [
            (f"{liar}说：{t1}在说谎", False),
            (f"{t1}说：{random.choice(truth_facts)}", True),
            (f"{t2}说：{t1}在说真话", True),
        ]
    elif template_id == 3:
        # 说谎者自称说真话（自相矛盾），诚实者揭穿
        items = [
            (f"{liar}说：我在说真话", False),
            (f"{t1}说：{t2}在说真话", True),
            (f"{t2}说：{liar}在说谎", True),
        ]
    elif template_id == 4:
        # 说谎者声称两个诚实者都在说谎
        items = [
            (f"{liar}说：{t1}和{t2}都在说谎", False),
            (f"{t1}说：{liar}在说谎", True),
            (f"{t2}说：{t1}在说真话", True),
        ]
    else:
        # 说谎者否认一个事实，诚实者证明
        facts = ["指纹是破案的重要线索", "监控可以记录犯罪过程", "说谎者在陈述时可能露出破绽", "不在场证明是嫌疑人自证清白的方式"]
        items = [
            (f"{liar}说：'{random.choice(facts)}'这句话是错的", False),
            (f"{t1}说：{liar}在说谎", True),
            (f"{t2}说：{t1}在说真话", True),
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
    template_id = random.randint(0, 3)  # 4 套模板
    templates = []

    if template_id == 0:
        templates.append((f"{liar}说：{truth_tellers[0]}在说谎", False))
        templates.append((f"{truth_tellers[0]}说：{truth_tellers[1]}在说真话", True))
        templates.append((f"{truth_tellers[1]}说：{truth_tellers[2]}在说真话", True))
        templates.append((f"{truth_tellers[2]}说：{liar}在说谎", True))
    elif template_id == 1:
        templates.append((f"{liar}说：我在说真话", False))
        templates.append((f"{truth_tellers[0]}说：{liar}在说谎", True))
        templates.append((f"{truth_tellers[1]}说：{truth_tellers[0]}在说真话", True))
        templates.append((f"{truth_tellers[2]}说：{truth_tellers[1]}在说真话", True))
    elif template_id == 2:
        templates.append((f"{liar}说：{truth_tellers[0]}在说谎", False))
        templates.append((f"{truth_tellers[0]}说：{truth_tellers[1]}在说真话", True))
        templates.append((f"{truth_tellers[1]}说：我想的和{truth_tellers[0]}一样", True))
        truth_facts = ["1+1=2", "地球绕太阳运行", "一年有十二个月", "三角形内角和为180度"]
        templates.append((f"{truth_tellers[2]}说：{random.choice(truth_facts)}", True))
    else:
        templates.append((f"{liar}说：{truth_tellers[0]}和{truth_tellers[1]}都在说谎", False))
        templates.append((f"{truth_tellers[0]}说：{truth_tellers[1]}在说真话", True))
        templates.append((f"{truth_tellers[1]}说：{truth_tellers[2]}在说真话", True))
        templates.append((f"{truth_tellers[2]}说：{liar}在说谎", True))

    random.shuffle(templates)
    statements = [t[0] for t in templates]
    false_index = next(i for i, t in enumerate(templates) if not t[1])
    return statements, false_index


class GameEngine:
    """游戏引擎：管理题目生成、状态和计分。"""

    def __init__(self):
        self.level = 0
        self.score = 0
        self.mode = "normal"  # "normal" | "challenge"
        self.current_question = None
        self._used_common_sense = []

    # ----- 对外接口 -----

    def next_question(self):
        """生成下一道题，返回 (statements, false_index, time_limit, q_type)。"""
        tm = TIME_LIMITS[self.mode]

        if self.level < 5:
            question = self._gen_common_sense()
            time_limit = tm["common"]
            q_type = "common"
        elif self.level < 10:
            statements, false_index = _generate_logic_question()
            question = (statements, false_index, 3)
            time_limit = tm["logic3"]
            q_type = "logic3"
        else:
            if random.random() < 0.4:
                question = self._gen_common_sense()
                time_limit = tm["common"]
                q_type = "common"
            else:
                statements, false_index = _generate_hard_logic_question()
                shuffled = list(enumerate(statements))
                random.shuffle(shuffled)
                false_index = next(i for i, (orig_idx, _) in enumerate(shuffled) if orig_idx == false_index)
                statements = [s for _, s in shuffled]
                question = (statements, false_index, 4)
                time_limit = tm["logic4"]
                q_type = "logic4"

        self.current_question = (*question, q_type)
        return (question[0], question[1], time_limit, q_type)

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
        shuffled = list(enumerate(statements))
        random.shuffle(shuffled)
        new_false_index = next(i for i, (orig_idx, _) in enumerate(shuffled) if orig_idx == false_index)
        statements = [s for _, s in shuffled]
        return (statements, new_false_index, 3)

    # ----- 属性 -----

    @property
    def phase(self):
        """侦探主题的阶段名。"""
        if self.level < 5:
            return "初步调查"
        if self.level < 10:
            return "深入审讯"
        return "核心案件"

    @property
    def phase_desc(self):
        """难度描述。"""
        if self.level < 5:
            return "常识判断"
        if self.level < 10:
            return "逻辑推理"
        return "高难挑战"
