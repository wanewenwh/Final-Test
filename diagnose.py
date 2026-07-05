"""诊断：检查 main.py 中 API Key 加载和 openai 导入"""
import sys, os

# 切换到项目目录
project_dir = '科学遐思精灵'
if os.path.isdir(project_dir):
    os.chdir(project_dir)
    sys.path.insert(0, '.')

print('=' * 50)
print('诊断报告')
print('=' * 50)

# 1. 检查 Python 路径
print(f'\n1. Python 路径: {sys.executable}')
print(f'   Python 版本: {sys.version}')

# 2. 检查 .env 文件
env_path = '.env'
print(f'\n2. .env 文件存在: {os.path.exists(env_path)}')
if os.path.exists(env_path):
    with open(env_path) as f:
        content = f.read().strip()
        print(f'   .env 内容前50字符: {content[:50]}')

# 3. 测试 openai 导入
print('\n3. 测试 openai 导入:')
try:
    from openai import OpenAI
    print('   ✅ from openai import OpenAI 成功')
except ImportError as e:
    print(f'   ❌ 导入失败: {e}')

# 4. 测试 AIService
print('\n4. 测试 AIService:')
try:
    from ai_service import AIService
    ai = AIService(api_key='sk-test')
    print(f'   ✅ AIService 创建成功')
    print(f'   api_key 长度: {len(ai.api_key)}')
    print(f'   base_url: {ai.base_url}')
    print(f'   model: {ai.model}')
except Exception as e:
    print(f'   ❌ 失败: {e}')

# 5. 测试完整调用
print('\n5. 测试 DeepSeek API 调用（5秒超时）:')
try:
    from ai_service import AIService
    ai = AIService(api_key='sk-46b44cd5bd9e4d849ab73b908d3d3876')
    result = ai._call_api('简单测试，请回复OK')
    print(f'   ✅ API 调用成功')
    print(f'   回复: {result[:100]}...')
except Exception as e:
    print(f'   ❌ 失败: {e}')

print('\n' + '=' * 50)
print('诊断完成')
