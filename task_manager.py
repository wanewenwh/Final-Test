"""
TaskManager 类：异步任务队列管理
职责：管理异步任务的创建、状态更新、查询和生命周期
体现：面向对象封装 + 线程安全数据结构 + 回调管理
"""

import os
import time
import threading


class TaskManager:
    """任务管理器 —— 线程安全的异步任务队列管理

    使用数据结构：
    - dict（线程安全，由 Lock 保护）：{task_id: {status, data}}
    - list（历史记录）：已完成的任务ID列表
    """

    # 任务状态常量
    STATUS_GENERATING = 'generating'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'

    def __init__(self):
        """初始化任务管理器"""
        # 线程安全的任务状态字典
        self._status = {}
        self._lock = threading.Lock()

        # 任务计数器（用于生成唯一ID）
        self._counter = 0
        self._counter_lock = threading.Lock()

        # 历史记录
        self._history = []

    def create_task(self):
        """创建新任务

        返回:
            task_id: str（格式: task_{时间戳}_{计数器}）

        数据结构：使用计数器 + 时间戳确保唯一性
        """
        with self._counter_lock:
            self._counter += 1
            counter = self._counter

        # 纳秒级时间戳 + 自增计数器确保完全不重复
        timestamp = time.time_ns()
        task_id = f"task_{timestamp}_{counter}"

        with self._lock:
            self._status[task_id] = {
                'status': self.STATUS_GENERATING,
                'data': None,
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            }
            self._history.append(task_id)

        return task_id

    def update_status(self, task_id, status, data=None):
        """更新任务状态（线程安全）

        参数:
            task_id: 任务ID
            status: 新状态（STATUS_GENERATING / COMPLETED / FAILED）
            data: 附加数据（如文件名、错误信息）
        """
        with self._lock:
            if task_id in self._status:
                self._status[task_id]['status'] = status
                self._status[task_id]['data'] = data
                if status in (self.STATUS_COMPLETED, self.STATUS_FAILED):
                    self._status[task_id]['completed_at'] = time.strftime('%Y-%m-%d %H:%M:%S')

    def get_status(self, task_id):
        """查询任务状态（线程安全）

        参数:
            task_id: 任务ID

        返回:
            dict: {status, data, created_at, completed_at?} 或 None
        """
        with self._lock:
            return self._status.get(task_id)

    def get_active_count(self):
        """获取当前进行中的任务数"""
        with self._lock:
            return sum(
                1 for s in self._status.values()
                if s['status'] == self.STATUS_GENERATING
            )

    def get_statistics(self):
        """获取任务统计信息

        返回:
            dict: {total, completed, failed, active, history_count}
        """
        with self._lock:
            total = len(self._status)
            completed = sum(1 for s in self._status.values()
                          if s['status'] == self.STATUS_COMPLETED)
            failed = sum(1 for s in self._status.values()
                        if s['status'] == self.STATUS_FAILED)
            active = total - completed - failed

        return {
            'total': total,
            'completed': completed,
            'failed': failed,
            'active': active,
            'history_count': len(self._history),
        }

    def cleanup_old_tasks(self, max_age_seconds=3600):
        """清理过期任务（释放内存）

        参数:
            max_age_seconds: 最大存活时间（秒）
        """
        now = time.time()
        with self._lock:
            expired = []
            for task_id, info in self._status.items():
                if info['status'] in (self.STATUS_COMPLETED, self.STATUS_FAILED):
                    if 'completed_at' in info:
                        completed_time = time.mktime(
                            time.strptime(info['completed_at'], '%Y-%m-%d %H:%M:%S')
                        )
                        if now - completed_time > max_age_seconds:
                            expired.append(task_id)

            for task_id in expired:
                del self._status[task_id]

        return len(expired)
