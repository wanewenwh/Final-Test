"""AIService 单元测试"""
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from ai_service import AIService


class TestAIService(unittest.TestCase):
    """AIService 类单元测试"""

    def setUp(self):
        self.service = AIService(api_key="test-key")

    def test_01_init_with_env_key(self):
        """TC-01: 初始化可从环境变量读取 API Key"""
        os.environ['DEEPSEEK_API_KEY'] = 'env-test-key'
        s = AIService()
        self.assertEqual(s.api_key, 'env-test-key')
        del os.environ['DEEPSEEK_API_KEY']

    def test_02_mock_response_not_empty(self):
        """TC-02: 无 API Key 时返回模拟响应"""
        service = AIService(api_key="")
        response = service._mock_response("测试问题")
        self.assertIsNotNone(response, "模拟响应不应为空")
        self.assertIn("核心假说", response, "模拟响应应包含核心假说")
        self.assertIn("下一步建议", response, "模拟响应应包含下一步建议")

    def test_03_mock_response_contains_user_text(self):
        """TC-03: 模拟响应应包含用户输入内容"""
        service = AIService(api_key="")
        user_text = "量子纠缠与信息传递的关系"
        response = service._mock_response(user_text)
        self.assertIn(user_text[:20], response, "响应应包含用户输入的前20字")

    def test_04_async_returns_task_id(self):
        """TC-04: 异步调用应返回 task_id"""
        task_id = self.service.generate_report_async("测试")
        self.assertIsNotNone(task_id, "应返回 task_id")
        self.assertTrue(task_id.startswith('task_'), "task_id 应以 task_ 开头")

    def test_05_system_prompt_not_empty(self):
        """TC-05: System Prompt 应包含必要的章节标题"""
        prompt = self.service.SYSTEM_PROMPT
        sections = ["核心假说", "理论背景", "可行性分析", "潜在价值", "下一步建议"]
        for section in sections:
            self.assertIn(section, prompt, f"System Prompt 应包含 {section}")

    def test_06_async_with_callbacks(self):
        """TC-06: 异步调用应触发回调（使用mock模式避免依赖openai库）"""
        service = AIService(api_key="")  # 空 Key → 走 mock 模式
        results = {}

        def on_complete(report):
            results['report'] = report

        def on_error(msg):
            results['error'] = msg

        task_id = service.generate_report_async(
            "测试问题",
            on_complete=on_complete,
            on_error=on_error
        )

        # 等待异步线程完成
        import time
        time.sleep(0.5)

        self.assertIn('report', results, "成功回调应被触发")
        self.assertIsNotNone(results['report'], "报告不应为空")


if __name__ == '__main__':
    unittest.main(verbosity=2)
