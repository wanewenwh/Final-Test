"""
科学遐思精灵 (Inspiration Storage Genie)
Flask Web 主入口 —— 薄控制器（Controller）

架构说明：
  遵循「薄控制器」设计模式，app.py 仅负责：
  - HTTP 路由分发
  - 请求参数解析与校验
  - 调用业务类完成操作
  - 响应格式化

  所有业务逻辑委托给专门类：
  - DataReader: 输入读取与验证
  - ReportAnalyzer: 核心分析算法
  - ResultExporter: 结果导出
  - TaskManager: 异步任务管理
  - FileStorage: 文件存储
  - AIService: AI API 调用

路由：
  GET  /                   主页
  POST /api/send_to_ai     发送给AI（异步触发）
  GET  /api/reports        获取报告列表
  GET  /api/reports/<name> 获取报告内容
  GET  /api/status/<id>    查询异步任务状态
  GET  /api/stats          获取系统统计信息
"""

import os
from flask import Flask, request, jsonify, render_template, send_from_directory

from file_storage import FileStorage
from report_analyzer import ReportAnalyzer
from result_exporter import ResultExporter
from task_manager import TaskManager

app = Flask(__name__)

# ============================================================
#  全局实例（单例模式）
# ============================================================
storage = FileStorage(report_dir="reports")
analyzer = ReportAnalyzer(use_ai=False)  # 默认使用本地算法
exporter = ResultExporter(output_dir="reports")
task_mgr = TaskManager()


# ============================================================
#  页面路由
# ============================================================

@app.route('/')
def index():
    """渲染主页面"""
    return render_template('index.html')


# ============================================================
#  API 路由
# ============================================================

@app.route('/api/send_to_ai', methods=['POST'])
def api_send_to_ai():
    """接收用户文本，异步触发分析

    请求: {"text": "..."}
    响应: {"task_id": "...", "status": "generating"}
    """
    data = request.get_json(force=True)
    user_text = data.get('text', '').strip()

    if not user_text:
        return jsonify({'status': 'error', 'message': '暂存区为空，请先输入内容'}), 400

    # 创建异步任务
    task_id = task_mgr.create_task()

    # 回调：分析成功 → 保存文件
    def on_complete(report_text):
        try:
            filepath = exporter.to_txt(user_text, report_text)
            filename = os.path.basename(filepath)
            task_mgr.update_status(task_id, task_mgr.STATUS_COMPLETED,
                                   {'filename': filename})
        except Exception as e:
            task_mgr.update_status(task_id, task_mgr.STATUS_FAILED,
                                   {'error': str(e)})

    # 回调：分析失败 → 保存错误文件
    def on_error(error_msg):
        try:
            filepath = exporter.to_txt(
                user_text,
                f"[分析失败]\n{error_msg}"
            )
            filename = os.path.basename(filepath)
            task_mgr.update_status(task_id, task_mgr.STATUS_COMPLETED,
                                   {'filename': filename, 'warning': error_msg})
        except Exception as e:
            task_mgr.update_status(task_id, task_mgr.STATUS_FAILED,
                                   {'error': str(e)})

    # 调用分析器（异步，返回 task_id）
    analyzer.analyze(
        text=user_text,
        on_complete=on_complete,
        on_error=on_error,
    )

    return jsonify({
        'task_id': task_id,
        'status': 'generating',
        'message': '报告生成中，请稍后...',
    })


@app.route('/api/reports', methods=['GET'])
def api_list_reports():
    """获取报告列表"""
    try:
        reports = storage.list_reports()
        return jsonify({'status': 'ok', 'reports': reports})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/reports/<filename>', methods=['GET'])
def api_get_report(filename):
    """获取单份报告内容"""
    try:
        content = storage.get_report(filename)
        return jsonify({'status': 'ok', 'content': content})
    except FileNotFoundError:
        return jsonify({'status': 'error', 'message': '报告文件不存在'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/status/<task_id>', methods=['GET'])
def api_task_status(task_id):
    """查询异步任务状态"""
    status = task_mgr.get_status(task_id)
    if status is None:
        return jsonify({'status': 'unknown', 'message': '任务不存在'}), 404
    return jsonify(status)


@app.route('/api/stats', methods=['GET'])
def api_system_stats():
    """获取系统统计信息"""
    return jsonify({
        'status': 'ok',
        'tasks': task_mgr.get_statistics(),
        'reports': len(storage.list_reports()),
    })


# ============================================================
#  启动
# ============================================================

if __name__ == '__main__':
    import os
    import sys
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    print("=" * 55)
    print("  [科学遐思精灵 v2.0]")
    print("  [访问地址] http://127.0.0.1:5000")
    print("  [分析模式] 本地算法（无需API Key）")
    print("  [报告目录] reports/")
    print("=" * 55)
    app.run(debug=True, host='127.0.0.1', port=5000)
