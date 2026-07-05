"""DataReader 单元测试"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import unittest
from data_reader import DataReader


class TestDataReader(unittest.TestCase):
    """DataReader 类 7 个测试用例"""

    def setUp(self):
        self.reader = DataReader()

    def test_01_read_cleans_text(self):
        """TC-01: read() 应清洗文本（去空行、去首尾空格）"""
        self.reader.read("  量子纠缠   \n\n\n  超光速  ")
        self.assertNotEqual(self.reader.raw_text, self.reader.cleaned_text)
        self.assertIn("量子纠缠", self.reader.cleaned_text)
        self.assertNotIn("  \n\n\n  ", self.reader.cleaned_text)

    def test_02_validate_empty(self):
        """TC-02: 空文本验证应返回 False"""
        is_valid, msg = self.reader.reset().read("").validate()
        self.assertFalse(is_valid)
        self.assertIn("为空", msg)

    def test_03_validate_short(self):
        """TC-03: 过短文本验证应返回 False"""
        is_valid, msg = self.reader.reset().read("a").validate()
        self.assertFalse(is_valid)

    def test_04_validate_valid(self):
        """TC-04: 有效文本应返回 True"""
        is_valid, msg = self.reader.reset().read("量子纠缠能否用于超光速通信？").validate()
        self.assertTrue(is_valid)

    def test_05_extract_keywords_physics(self):
        """TC-05: 应正确提取物理类关键词"""
        self.reader.reset().read("量子纠缠和黑洞的关系")
        kws = self.reader.extract_keywords()
        self.assertIn("量子", kws)
        self.assertIn("黑洞", kws)

    def test_06_classify(self):
        """TC-06: 分类应返回匹配到的科学领域"""
        self.reader.reset().read("DNA基因编辑和神经网络算法")
        cats = self.reader.classify()
        self.assertIn("生物", cats)
        self.assertIn("计算机", cats)

    def test_07_get_stats(self):
        """TC-07: get_stats() 应返回完整统计"""
        self.reader.reset().read("这是第一句。这是第二句？这是第三句！")
        stats = self.reader.get_stats()
        self.assertIn('sentence_count', stats)
        self.assertIn('word_count', stats)
        self.assertIn('keyword_count', stats)
        self.assertIn('categories', stats)
        self.assertGreaterEqual(stats['sentence_count'], 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
