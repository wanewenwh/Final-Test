"""FileStorage 类：封装报告文件的读写、列表、存储逻辑"""
import os
import time
from datetime import datetime


class FileStorage:
    """文件存储类——高内聚，负责所有报告文件的磁盘操作"""

    def __init__(self, report_dir="reports"):
        """初始化存储目录，不存在则自动创建"""
        self.report_dir = report_dir
        os.makedirs(self.report_dir, exist_ok=True)

    def save_report(self, question, ai_response):
        """保存一份报告到文件

        参数:
            question: 用户的科学遐思文本
            ai_response: DeepSeek 返回的结构化报告（或错误信息）

        返回:
            filename: 生成的文件名
        """
        # 用纳秒级时间戳确保文件名唯一
        ns = time.time_ns()
        dt = datetime.fromtimestamp(ns // 1_000_000_000)
        timestamp = dt.strftime("%Y%m%d_%H%M%S") + f"_{ns % 1_000_000_000:09d}"
        filename = f"科学遐思_{timestamp}.txt"
        filepath = os.path.join(self.report_dir, filename)

        content = (
            f"【科学遐思提问】\n{question}\n"
            f"{'=' * 40}\n"
            f"【AI 研究报告】\n{ai_response}"
        )

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
        except IOError as e:
            raise IOError(f"文件写入失败: {e}")

        return filename

    def list_reports(self):
        """返回报告列表，按时间倒序

        返回:
            [{name, time, size}, ...]
        """
        if not os.path.isdir(self.report_dir):
            return []

        files = []
        for fname in os.listdir(self.report_dir):
            if fname.endswith('.txt'):
                fpath = os.path.join(self.report_dir, fname)
                try:
                    mtime = os.path.getmtime(fpath)
                    size = os.path.getsize(fpath)
                    files.append({
                        'name': fname,
                        'time': datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S"),
                        'size': size
                    })
                except OSError:
                    continue

        # 按时间倒序
        files.sort(key=lambda x: x['time'], reverse=True)
        return files

    def get_report(self, filename):
        """读取并返回报告文件的纯文本内容"""
        # 安全检查：防止路径穿越
        safe_name = os.path.basename(filename)
        filepath = os.path.join(self.report_dir, safe_name)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"报告文件不存在: {filename}")

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError as e:
            raise IOError(f"文件读取失败: {e}")
