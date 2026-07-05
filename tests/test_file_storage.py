"""FileStorage 单元测试"""
import os
import sys
import tempfile
import unittest

# 添加项目根到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from file_storage import FileStorage


class TestFileStorage(unittest.TestCase):
    """FileStorage 类单元测试"""

    def setUp(self):
        """每个测试前创建临时目录"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = FileStorage(report_dir=self.temp_dir)

    def tearDown(self):
        """每个测试后清理临时文件"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_save_report_creates_file(self):
        """TC-01: 保存报告应生成文件"""
        filename = self.storage.save_report("测试问题", "测试回答")
        filepath = os.path.join(self.temp_dir, filename)
        self.assertTrue(os.path.exists(filepath), "文件应被创建")
        self.assertTrue(filename.endswith('.txt'), "文件应以 .txt 结尾")

    def test_02_save_report_content(self):
        """TC-02: 保存的报告内容应完整"""
        q = "人类能否实现光速旅行？"
        a = "根据相对论，有质量物体无法达到光速。"
        filename = self.storage.save_report(q, a)
        content = self.storage.get_report(filename)
        self.assertIn(q, content, "内容应包含提问")
        self.assertIn(a, content, "内容应包含回答")
        self.assertIn("【科学遐思提问】", content, "应有提问标记")
        self.assertIn("【AI 研究报告】", content, "应有报告标记")

    def test_03_list_reports_empty(self):
        """TC-03: 空目录应返回空列表"""
        reports = self.storage.list_reports()
        self.assertEqual(reports, [], "空目录应返回空列表")

    def test_04_list_reports_after_save(self):
        """TC-04: 保存后列表应包含新文件"""
        self.storage.save_report("问题1", "回答1")
        import time; time.sleep(0.01)  # 避免纳秒级文件名冲突
        self.storage.save_report("问题2", "回答2")
        reports = self.storage.list_reports()
        self.assertEqual(len(reports), 2, f"应有2份报告，实际{len(reports)}")
        self.assertIn('name', reports[0], "报告应有 name 字段")
        self.assertIn('time', reports[0], "报告应有 time 字段")
        self.assertIn('size', reports[0], "报告应有 size 字段")

    def test_05_get_nonexistent_file_raises(self):
        """TC-05: 读取不存在的文件应抛出异常"""
        with self.assertRaises(FileNotFoundError):
            self.storage.get_report("不存在的文件.txt")

    def test_06_path_traversal_prevention(self):
        """TC-06: 路径穿越攻击应被阻止"""
        with self.assertRaises(FileNotFoundError):
            self.storage.get_report("../../etc/passwd")

    def test_07_save_report_with_empty_strings(self):
        """TC-07: 空提问和空回答也应能保存"""
        filename = self.storage.save_report("", "")
        content = self.storage.get_report(filename)
        self.assertIsNotNone(content, "空内容也应能保存")


if __name__ == '__main__':
    unittest.main(verbosity=2)
