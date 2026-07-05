"""AIService 类：封装 DeepSeek API 调用逻辑"""
import os
import time
import threading


class AIService:
    """AI 服务类——负责调用 DeepSeek API 生成研究报告（异步）"""

    # 固定的 System Prompt
    SYSTEM_PROMPT = (
        "你是一位顶尖的科研灵感分析专家。用户会提交一段关于科学问题的遐想或猜测"
        "（称为\"科学遐思\"）。请根据这段内容，生成一份详细的研究报告。"
        "报告需包含以下结构（纯文本，仅用换行和空格）：\n\n"
        "核心假说\n\n"
        "理论背景\n\n"
        "可行性分析\n\n"
        "潜在价值\n\n"
        "下一步建议"
    )

    def __init__(self, api_key=None, model="deepseek-chat"):
        """初始化 AI 服务

        参数:
            api_key: DeepSeek API Key，默认从环境变量 DEEPSEEK_API_KEY 读取
            model: 模型名称
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY", "")
        self.model = model
        self.base_url = "https://api.deepseek.com"

        # 回调函数注册表：{task_id: callback}
        self._callbacks = {}
        self._lock = threading.Lock()

    def generate_report_async(self, user_text, on_complete=None, on_error=None):
        """异步生成报告，立即返回 task_id，后台线程完成实际调用

        参数:
            user_text: 用户暂存的科学遐思文本
            on_complete: 成功回调 fn(filename)
            on_error: 失败回调 fn(error_msg)

        返回:
            task_id: 任务ID，可用于追踪
        """
        task_id = f"task_{int(time.time() * 1000)}_{threading.get_ident()}"

        # 后台线程执行
        thread = threading.Thread(
            target=self._do_generate,
            args=(task_id, user_text, on_complete, on_error),
            daemon=True
        )
        thread.start()

        return task_id

    def _do_generate(self, task_id, user_text, on_complete, on_error):
        """后台线程执行的生成逻辑"""
        try:
            report = self._call_api(user_text)
            if on_complete:
                on_complete(report)
        except Exception as e:
            error_msg = f"AI 生成失败：{str(e)}"
            if on_error:
                on_error(error_msg)

    def _call_api(self, user_text):
        """实际调用 DeepSeek API（同步阻塞，在子线程中执行）

        使用 Python 内置 urllib 直接调用 DeepSeek API，
        无需安装任何第三方库。
        """
        if not self.api_key or self.api_key == "your-api-key-here":
            return self._mock_response(user_text)

        import json
        import urllib.request

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": f"科学遐思：{user_text}"}
            ],
            "temperature": 0.7,
            "max_tokens": 2048
        }

        req = urllib.request.Request(
            url=f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode('utf-8'),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                return result["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            status = e.code
            body = e.read().decode('utf-8', errors='ignore')
            raise Exception(f"API 返回错误 {status}: {body}")
        except urllib.error.URLError as e:
            raise Exception(f"网络连接失败: {e.reason}")
        except Exception as e:
            raise Exception(f"API 调用失败: {e}")

    def _mock_response(self, user_text):
        """模拟 AI 回复（当 API Key 未配置时使用）"""
        import textwrap
        return textwrap.dedent(f"""
        【核心假说】
        基于您的描述：「{user_text[:50]}...」，初步推测该想法涉及一个尚未被充分探索的科学机制。

        【理论背景】
        该想法与以下已知理论存在关联：
        1. 相关领域的基础研究进展
        2. 已有实验数据的支持与矛盾
        3. 当前理论框架下的解释局限性

        【可行性分析】
        优势：想法具有一定创新性，与现有技术路线部分兼容。
        挑战：需要进一步设计验证实验，当前可获取的数据量可能不足。
        风险评估：中等，建议从小规模验证开始。

        【潜在价值】
        若该假说成立，可能对相关领域产生以下影响：
        - 提供新的理论解释框架
        - 启发新的实验设计方向
        - 推动跨学科研究合作

        【下一步建议】
        1. 检索相关文献，确认该想法的新颖性
        2. 设计初步验证实验方案
        3. 与领域内同行讨论可行性
        4. 考虑申请预研项目资助
        """).strip()
