"""
ReportAnalyzer 类：核心分析算法引擎
职责：实现本地分析算法 + 可选的 AI API 增强分析
体现：算法逻辑自行实现 + 策略模式（本地/AI切换）

核心算法（自实现）：
1. 关键词频率分析 —— 统计输入中科学关键词的出现频次
2. 文本复杂度评估 —— 基于句子长度和词汇多样性的评分
3. 结构化报告生成 —— 将分析结果组装为结构化文本
"""

import os
import re
import time
import threading
from collections import Counter

from data_reader import DataReader


class ReportAnalyzer:
    """报告分析器 —— 核心算法引擎，支持本地分析和 AI 增强"""

    # 分析报告模板章节
    REPORT_SECTIONS = [
        "核心假说",
        "理论背景",
        "可行性分析",
        "潜在价值",
        "下一步建议",
    ]

    def __init__(self, use_ai=True, ai_service=None):
        """初始化分析器

        参数:
            use_ai: 是否使用 AI API 增强分析（False=仅本地算法）
            ai_service: AIService 实例（若 use_ai=True）
        """
        self.use_ai = use_ai
        self.ai_service = ai_service
        self.reader = DataReader()

    # ============================================================
    #  核心算法 1：关键词频率分析
    # ============================================================

    def analyze_keywords(self, text):
        """关键词频率分析 —— 自实现算法

        算法步骤：
        1. 使用 DataReader 提取科学关键词（集合运算）
        2. 按分类统计关键词分布
        3. 计算关键词密度：关键词数 / 总字数

        参数:
            text: 用户输入文本

        返回:
            dict: 关键词分析结果
        """
        self.reader.reset().read(text)
        keywords = self.reader.extract_keywords()
        categories = self.reader.classify()
        word_count = self.reader.word_count

        density = len(keywords) / max(word_count, 1) * 100

        return {
            'total_keywords': len(keywords),
            'keywords': sorted(keywords),
            'categories': categories,
            'density': round(density, 2),
            'primary_category': max(categories, key=categories.get) if categories else "未分类",
        }

    # ============================================================
    #  核心算法 2：文本复杂度评估
    # ============================================================

    def analyze_complexity(self, text):
        """文本复杂度评估 —— 自实现算法

        算法步骤：
        1. 计算平均句子长度（字/句）
        2. 计算长句占比（>50字为长句）
        3. 计算词汇多样性（去重字符比例）
        4. 综合评分（0-100）

        参数:
            text: 用户输入文本

        返回:
            dict: 复杂度评估结果
        """
        self.reader.reset().read(text)

        # 分句
        sentences = re.split(r'[。！？.!?\n]', self.reader.cleaned_text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return {'score': 0, 'level': '无内容', 'detail': {}}

        # 平均句子长度
        avg_len = sum(len(s) for s in sentences) / len(sentences)

        # 长句占比（>50字）
        long_sentences = [s for s in sentences if len(s) > 50]
        long_ratio = len(long_sentences) / len(sentences)

        # 词汇多样性（去重字符比例）
        unique_chars = len(set(self.reader.cleaned_text))
        total_chars = len(self.reader.cleaned_text)
        diversity = unique_chars / max(total_chars, 1)

        # 综合评分（0-100）
        # 因子：平均长度(40%) + 长句占比(30%) + 多样性(30%)
        length_score = min(avg_len / 80, 1) * 40
        long_score = long_ratio * 30
        diversity_score = diversity * 30
        score = round(length_score + long_score + diversity_score, 1)

        # 等级
        if score >= 70:
            level = "高复杂度"
        elif score >= 40:
            level = "中等复杂度"
        else:
            level = "较低复杂度"

        return {
            'score': score,
            'level': level,
            'detail': {
                'sentence_count': len(sentences),
                'avg_length': round(avg_len, 1),
                'long_sentence_ratio': round(long_ratio * 100, 1),
                'diversity': round(diversity * 100, 1),
            }
        }

    # ============================================================
    #  核心算法 3：结构化报告生成（本地）
    # ============================================================

    def generate_local_report(self, text):
        """本地算法生成结构化报告 —— 不依赖外部 API

        算法步骤：
        1. 对输入文本进行预处理和关键词提取
        2. 基于关键词分类生成各章节内容
        3. 组装为完整报告文本

        参数:
            text: 用户输入文本

        返回:
            str: 结构化报告文本
        """
        self.reader.reset().read(text)

        # 提取分析数据
        kw_analysis = self.analyze_keywords(text)
        cx_analysis = self.analyze_complexity(text)

        # 根据关键词分类动态生成报告
        categories = kw_analysis['categories']
        primary = kw_analysis['primary_category']
        keywords_list = kw_analysis['keywords']
        score = cx_analysis['score']
        level = cx_analysis['level']

        lines = []

        # 核心假说
        lines.append("【核心假说】")
        lines.append(f"您提出了一个涉及「{primary}」领域的科学遐想。")
        lines.append(f"该想法共包含 {kw_analysis['total_keywords']} 个科学关键词")
        lines.append(f"（{', '.join(keywords_list[:8])}），")
        lines.append("初步判断具有以下核心假设方向：")
        for i, kw in enumerate(keywords_list[:3], 1):
            lines.append(f"  {i}. 与「{kw}」相关的科学机制探索")
        lines.append("")

        # 理论背景
        lines.append("【理论背景】")
        lines.append(f"文本复杂度评分 {score} 分（{level}），表明您对该问题有一定深度的思考。")
        if categories:
            lines.append("涉及的科学领域分布：")
            for cat, cnt in categories.items():
                bar = "█" * cnt + "░" * (5 - cnt)
                lines.append(f"  {cat}: {bar} ({cnt}个关键词)")
        lines.append("")
        lines.append("基于关键词分析，该想法与以下已有理论可能存在关联：")
        lines.append("  1. 相关领域的基础研究框架")
        lines.append("  2. 已知实验现象的理论解释")
        lines.append("  3. 当前科学范式中尚未解决的问题")
        lines.append("")

        # 可行性分析
        lines.append("【可行性分析】")
        lines.append("基于当前科学认知水平和技术条件：")
        lines.append("  优势：")
        lines.append("    • 想法具有创新性，值得进一步探索")
        lines.append(f"    • 涉及 {len(categories)} 个交叉学科领域，研究视角独特")
        lines.append("  挑战：")
        lines.append("    • 需要进行文献调研确认新颖性")
        lines.append("    • 可能需要跨学科合作")
        lines.append("  风险评估：中等，建议从理论论证和小规模实验开始")
        lines.append("")

        # 潜在价值
        lines.append("【潜在价值】")
        lines.append("若该假说得到验证，可能带来的价值：")
        lines.append("  1. 对「{primary}」领域理论体系的补充或修正")
        lines.append("  2. 启发新的实验方法或技术路线")
        lines.append("  3. 推动相关学科的交叉融合")
        lines.append("  4. 为工程应用提供新的理论基础")
        lines.append("")

        # 下一步建议
        lines.append("【下一步建议】")
        lines.append("  1. 文献调研：检索「{primary}」领域最新研究进展")
        lines.append("  2. 理论建模：构建初步的数学模型或理论框架")
        lines.append("  3. 实验设计：提出可验证的具体实验方案")
        lines.append("  4. 同行讨论：与领域专家交流想法")
        lines.append("  5. 跨学科合作：寻找相关领域的合作伙伴")

        return "\n".join(lines)

    # ============================================================
    #  统一分析接口
    # ============================================================

    def analyze(self, text, on_complete=None, on_error=None):
        """统一分析接口 —— 自动选择本地算法或 AI API

        参数:
            text: 用户输入文本
            on_complete: 成功回调 fn(report_text)
            on_error: 失败回调 fn(error_msg)

        返回:
            task_id: 任务ID（异步时）或 None（同步时）
        """
        if not self.use_ai or self.ai_service is None:
            # 模式1：纯本地算法分析（同步）
            try:
                report = self.generate_local_report(text)
                if on_complete:
                    on_complete(report)
                return None
            except Exception as e:
                if on_error:
                    on_error(f"本地分析失败: {e}")
                return None
        else:
            # 模式2：AI API 增强分析（异步）
            return self.ai_service.generate_report_async(
                user_text=text,
                on_complete=on_complete,
                on_error=on_error,
            )
