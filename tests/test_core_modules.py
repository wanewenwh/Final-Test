"""ReportAnalyzer + TaskManager + ResultExporter 单元测试"""
import os, sys, time, json, tempfile, shutil
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import unittest
from report_analyzer import ReportAnalyzer
from task_manager import TaskManager
from result_exporter import ResultExporter


class TestReportAnalyzer(unittest.TestCase):
    """ReportAnalyzer 核心算法测试 5 个用例"""

    def setUp(self):
        self.analyzer = ReportAnalyzer(use_ai=False)

    def test_01_keyword_analysis(self):
        """TC-01: 关键词频率分析应返回分类结果"""
        result = self.analyzer.analyze_keywords("量子纠缠与DNA基因编辑的关系")
        self.assertIn('total_keywords', result)
        self.assertIn('categories', result)
        self.assertGreater(result['total_keywords'], 0)

    def test_02_complexity_analysis(self):
        """TC-02: 文本复杂度评估应返回评分和等级"""
        text = "量子纠缠是一种奇特的量子力学现象。" * 5
        result = self.analyzer.analyze_complexity(text)
        self.assertIn('score', result)
        self.assertIn('level', result)
        self.assertGreater(result['score'], 0)

    def test_03_local_report_generation(self):
        """TC-03: 本地报告应包含全部5个章节"""
        report = self.analyzer.generate_local_report("量子纠缠能否实现超光速通信？")
        for section in self.analyzer.REPORT_SECTIONS:
            self.assertIn(section, report, f"报告应包含「{section}」章节")

    def test_04_local_report_not_empty(self):
        """TC-04: 本地报告不应为空"""
        report = self.analyzer.generate_local_report("人工智能的未来发展方向")
        self.assertTrue(len(report) > 100, "报告长度应超过100字")

    def test_05_analyze_callback_local(self):
        """TC-05: analyze() 应触发成功回调（本地模式）"""
        results = {}
        self.analyzer.analyze("测试文本", 
            on_complete=lambda r: results.update({'report': r}),
            on_error=lambda e: results.update({'error': e}))
        self.assertIn('report', results)
        self.assertIsNotNone(results['report'])


class TestTaskManager(unittest.TestCase):
    """TaskManager 测试 4 个用例"""

    def setUp(self):
        self.mgr = TaskManager()

    def test_01_create_task(self):
        """TC-06: create_task 应返回唯一 task_id"""
        t1 = self.mgr.create_task()
        t2 = self.mgr.create_task()
        self.assertNotEqual(t1, t2, "两次创建的任务ID应不同")
        self.assertTrue(t1.startswith('task_'))

    def test_02_update_and_get_status(self):
        """TC-07: update_status 后 get_status 应返回更新后的值"""
        task_id = self.mgr.create_task()
        self.mgr.update_status(task_id, 'completed', {'filename': 'test.txt'})
        status = self.mgr.get_status(task_id)
        self.assertEqual(status['status'], 'completed')
        self.assertEqual(status['data']['filename'], 'test.txt')

    def test_03_get_nonexistent(self):
        """TC-08: 查询不存在任务应返回 None"""
        self.assertIsNone(self.mgr.get_status('nonexistent'))

    def test_04_statistics(self):
        """TC-09: get_statistics 应返回正确计数"""
        for _ in range(3):
            tid = self.mgr.create_task()
        stats = self.mgr.get_statistics()
        self.assertEqual(stats['total'], 3)
        self.assertEqual(stats['active'], 3)


class TestResultExporter(unittest.TestCase):
    """ResultExporter 测试 4 个用例"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.exporter = ResultExporter(output_dir=self.temp_dir)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_export_txt(self):
        """TC-10: to_txt 应生成正确的TXT文件"""
        path = self.exporter.to_txt("问题", "报告内容")
        self.assertTrue(os.path.exists(path))
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertIn("【科学遐思提问】", content)
        self.assertIn("【AI 研究报告】", content)
        self.assertIn("问题", content)
        self.assertIn("报告内容", content)

    def test_02_export_csv(self):
        """TC-11: to_csv 应生成CSV文件"""
        data = [{'name': 'a.txt', 'size': 100}, {'name': 'b.txt', 'size': 200}]
        path = self.exporter.to_csv(data)
        self.assertTrue(os.path.exists(path))
        self.assertTrue(path.endswith('.csv'))

    def test_03_export_json(self):
        """TC-12: to_json 应生成JSON文件"""
        data = {'key': 'value', 'number': 42}
        path = self.exporter.to_json(data)
        self.assertTrue(os.path.exists(path))
        with open(path, 'r', encoding='utf-8') as f:
            loaded = json.load(f)
        self.assertEqual(loaded['key'], 'value')
        self.assertEqual(loaded['number'], 42)

    def test_04_export_all(self):
        """TC-13: export_all 应同时导出TXT和JSON"""
        result = self.exporter.export_all("问题", "报告", {'version': '1.0'})
        self.assertIn('txt_path', result)
        self.assertIn('json_path', result)
        self.assertTrue(os.path.exists(result['txt_path']))
        self.assertTrue(os.path.exists(result['json_path']))


if __name__ == '__main__':
    unittest.main(verbosity=2)
