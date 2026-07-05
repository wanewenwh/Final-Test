"""
DataReader 类：数据输入与验证
职责：接收用户输入，验证合法性，提取结构化信息
体现：面向对象封装 + 数据结构应用（字符串操作、集合运算）
"""

import re


class DataReader:
    """数据读取器 —— 封装用户输入的读取、清洗、关键词提取"""

    # 科学相关关键词库（用于关键词匹配分析）
    SCIENCE_KEYWORDS = {
        "物理": ["量子", "相对论", "引力", "粒子", "能量", "力", "电磁", "光速",
                "时空", "黑洞", "暗物质", "暗能量", "熵", "弦理论"],
        "生物": ["基因", "DNA", "细胞", "进化", "蛋白质", "酶", "细菌",
                "病毒", "免疫", "神经", "脑", "生态"],
        "化学": ["分子", "原子", "化学反应", "催化剂", "元素", "化合", "分解",
                "氧化", "还原", "pH"],
        "计算机": ["算法", "数据", "神经网络", "AI", "人工智能", "机器学习",
                  "深度学习", "量子计算", "编程", "模型"],
        "天文": ["恒星", "行星", "星系", "宇宙", "太阳系", "陨石", "卫星",
                "轨道", "航天", "探测器"],
    }

    def __init__(self):
        """初始化读取器"""
        self.raw_text = ""
        self.cleaned_text = ""
        self.keywords = set()
        self.sentence_count = 0
        self.word_count = 0

    def read(self, text):
        """读取并清洗用户输入

        参数:
            text: 原始用户输入字符串

        返回:
            self (支持链式调用)

        数据结构：字符串预处理（strip、去空行、正则清洗）
        """
        self.raw_text = text

        # 去除首尾空白
        cleaned = text.strip()

        # 去除多余空行（多个换行合并为两个）
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

        # 去除行首行尾多余空格
        lines = [line.strip() for line in cleaned.split('\n')]
        self.cleaned_text = '\n'.join(lines)

        # 统计信息
        self.sentence_count = len(re.findall(r'[。！？.!?]', self.cleaned_text))
        self.word_count = len(self.cleaned_text)

        return self

    def validate(self):
        """验证输入是否合法

        返回:
            (is_valid: bool, message: str)

        验证规则：
        - 不能为空
        - 最少 2 个字符
        - 不能全是标点符号
        """
        if not self.cleaned_text:
            return False, "输入内容为空，请先输入科学遐想"

        if len(self.cleaned_text) < 2:
            return False, "内容太短（至少2个字符），请补充更多细节"

        # 检查是否全是标点符号
        if re.match(r'^[\s\W]+$', self.cleaned_text):
            return False, "输入内容不包含有效文字，请输入科学相关遐想"

        return True, "输入有效"

    def extract_keywords(self):
        """提取科学关键词

        返回:
            keywords: set[str] — 匹配到的科学关键词集合

        数据结构：集合（set）—— 关键词去重、可用于后续交集运算
        算法：遍历预定义分类关键词库，匹配用户输入中的关键词
        """
        self.keywords = set()

        for category, words in self.SCIENCE_KEYWORDS.items():
            for word in words:
                if word in self.cleaned_text:
                    self.keywords.add(word)

        return self.keywords

    def classify(self):
        """对输入内容进行科学分类

        返回:
            categories: dict[str, int] — {分类名: 匹配关键词数量}

        数据结构：字典（dict）—— 分类名到匹配数的映射
        """
        self.extract_keywords()
        categories = {}

        for category, words in self.SCIENCE_KEYWORDS.items():
            matched = self.keywords & set(words)
            if matched:
                categories[category] = len(matched)

        return dict(sorted(categories.items(), key=lambda x: x[1], reverse=True))

    def get_stats(self):
        """获取输入文本的统计信息

        返回:
            dict: {sentence_count, word_count, keyword_count, categories}
        """
        return {
            'sentence_count': self.sentence_count,
            'word_count': self.word_count,
            'keyword_count': len(self.keywords),
            'categories': self.classify(),
        }

    def summary(self, max_len=100):
        """生成输入文本摘要

        参数:
            max_len: 摘要最大长度

        返回:
            str: 截断后的摘要文本
        """
        if len(self.cleaned_text) <= max_len:
            return self.cleaned_text
        return self.cleaned_text[:max_len] + "..."

    def reset(self):
        """重置读取器状态"""
        self.raw_text = ""
        self.cleaned_text = ""
        self.keywords = set()
        self.sentence_count = 0
        self.word_count = 0
        return self
