"""
ResultExporter 类：结果导出器
职责：将分析结果以多种格式导出（TXT、CSV、JSON），支持文件保存和展示
体现：面向对象封装 + 多种数据结构应用 + 文件 I/O 异常处理
"""

import os
import csv
import json
import time
from datetime import datetime


class ResultExporter:
    """结果导出器 —— 支持 TXT / CSV / JSON 三种导出格式"""

    # 导出格式常量
    FORMAT_TXT = 'txt'
    FORMAT_CSV = 'csv'
    FORMAT_JSON = 'json'

    def __init__(self, output_dir="reports"):
        """初始化导出器

        参数:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _generate_filename(self, prefix, extension):
        """生成唯一文件名

        数据结构：字符串格式化（f-string）
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        return f"{prefix}_{timestamp}.{extension}"

    def to_txt(self, question, report, filename=None):
        """导出为 TXT 格式

        文件结构（三段式）：
        【科学遐思提问】
        {问题}
        ========================
        【AI 研究报告】
        {报告内容}

        参数:
            question: 用户提问
            report: 报告内容
            filename: 指定文件名（可选，不指定则自动生成）

        返回:
            filepath: 保存的文件路径
        """
        if filename is None:
            filename = self._generate_filename("科学遐思", "txt")

        filepath = os.path.join(self.output_dir, filename)

        content = (
            f"【科学遐思提问】\n{question}\n"
            f"{'=' * 40}\n"
            f"【AI 研究报告】\n{report}"
        )

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except IOError as e:
            raise IOError(f"TXT 文件写入失败: {e}")

        return filepath

    def to_csv(self, reports_data, filename=None):
        """导出为 CSV 格式

        适合批量导出报告元数据（文件名、时间、大小）

        参数:
            reports_data: list[dict] — 报告列表数据
            filename: 指定文件名（可选）

        返回:
            filepath: 保存的文件路径
        """
        if filename is None:
            filename = self._generate_filename("报告列表", "csv")

        filepath = os.path.join(self.output_dir, filename)

        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                if reports_data:
                    writer = csv.DictWriter(f, fieldnames=reports_data[0].keys())
                    writer.writeheader()
                    writer.writerows(reports_data)
                else:
                    f.write("暂无报告数据\n")
        except IOError as e:
            raise IOError(f"CSV 文件写入失败: {e}")

        return filepath

    def to_json(self, data, filename=None):
        """导出为 JSON 格式

        适合结构化数据的导出，便于程序解析

        参数:
            data: 任意可 JSON 序列化的数据
            filename: 指定文件名（可选）

        返回:
            filepath: 保存的文件路径
        """
        if filename is None:
            filename = self._generate_filename("分析结果", "json")

        filepath = os.path.join(self.output_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (IOError, TypeError) as e:
            raise IOError(f"JSON 文件写入失败: {e}")

        return filepath

    def export_all(self, question, report, metadata=None):
        """同时导出 TXT + JSON 两种格式

        参数:
            question: 问题文本
            report: 报告内容
            metadata: 可选的元数据 dict

        返回:
            dict: {txt_path, json_path}
        """
        result = {}

        # 导出 TXT
        result['txt_path'] = self.to_txt(question, report)

        # 导出 JSON（包含结构化数据）
        json_data = {
            'question': question,
            'report': report,
            'export_time': datetime.now().isoformat(),
        }
        if metadata:
            json_data['metadata'] = metadata
        result['json_path'] = self.to_json(json_data)

        return result
