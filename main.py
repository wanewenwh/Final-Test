#!/usr/bin/env python3
"""
科学遐思精灵（桌面版）
Tkinter 双栏布局 —— 异步灵感收集与 AI 深度研究工具
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import sys
import threading
import time

from data_reader import DataReader
from report_analyzer import ReportAnalyzer
from result_exporter import ResultExporter
from task_manager import TaskManager
from file_storage import FileStorage
from ai_service import AIService

# 默认 API Key（用户可在设置界面修改）
DEFAULT_API_KEY = "sk-46b44cd5bd9e4d849ab73b908d3d3876"


class ScienceGenieApp(tk.Tk):
    """科学遐思精灵 —— 桌面主窗口"""

    def __init__(self):
        super().__init__()
        self.title("科学遐思精灵 v2.0")
        self.geometry("1200x750")
        self.minsize(900, 600)
        self.configure(bg='#f0f2f5')

        # ---------- 读取 API Key ----------
        self._load_api_key()

        # ---------- 核心实例 ----------
        use_real_ai = bool(self.api_key) and self.api_key != "your-api-key-here"

        # 尝试设置控制台 UTF-8 编码
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass

        if use_real_ai:
            ai_service = AIService(api_key=self.api_key)
            self.analyzer = ReportAnalyzer(use_ai=True, ai_service=ai_service)
            print("[配置] DeepSeek API 已连接，模型: " + ai_service.model)
        else:
            self.analyzer = ReportAnalyzer(use_ai=False)
            print("[配置] 使用本地算法（未检测到有效 API Key）")
            if not self.api_key:
                print("[提示] 在 .env 文件中配置 DEEPSEEK_API_KEY 可启用 AI 增强")

        self.storage = FileStorage(report_dir="reports")
        self.exporter = ResultExporter(output_dir="reports")
        self.reader = DataReader()

        # 暂存区
        self.stash_texts = []
        self.current_task_id = None

        self._build_ui()
        self._refresh_report_list()

        # 状态栏显示当前模式
        mode_text = "DeepSeek AI" if use_real_ai else "local"
        self._set_status("[模式] " + mode_text + " | 输入灵感 -> 暂存累积 -> 一键生成报告", 'info')

    # ============================================================
    #  界面构建
    # ============================================================

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=0)  # 标题
        self.grid_rowconfigure(1, weight=1)  # 主区域
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # ---- 标题栏（grid 布局，从左到右：标题 | 副标题 | 弹性区 | 设置按钮 | 版本号）----
        title_f = tk.Frame(self, bg='#1a1a2e', height=48)
        title_f.grid(row=0, column=0, columnspan=2, sticky='ew')
        title_f.grid_propagate(False)
        title_f.grid_columnconfigure(2, weight=1)  # 中间弹性空间

        tk.Label(title_f, text="  \U0001f52c \u79d1\u5b66\u9050\u60f3\u7cbe\u7075", bg='#1a1a2e', fg='white',
                 font=('TkDefaultFont', 16, 'bold')).grid(row=0, column=0, padx=(15, 5))
        tk.Label(title_f, text="Inspiration Storage Genie", bg='#1a1a2e',
                 fg='#88aadd', font=('TkDefaultFont', 9)).grid(row=0, column=1, padx=(0, 5))

        # 设置按钮（用普通文本颜色，hover 效果）
        settings_btn = tk.Button(title_f, text="\u2699 \u8bbe\u7f6e",
                                 bg='#1a1a2e', fg='#88aadd', activebackground='#2a2a4e',
                                 font=('TkDefaultFont', 10), relief=tk.FLAT, padx=10, pady=4,
                                 cursor='hand2', command=self._open_settings)
        settings_btn.grid(row=0, column=3, padx=(0, 5))

        tk.Label(title_f, text="v2.0", bg='#1a1a2e', fg='#667788',
                 font=('TkDefaultFont', 9)).grid(row=0, column=4, padx=(0, 15))

        # ---- 主区域 ----
        main_f = tk.Frame(self, bg='#f0f2f5')
        main_f.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=8, pady=8)
        main_f.grid_columnconfigure(0, weight=1)
        main_f.grid_columnconfigure(1, weight=0)
        main_f.grid_rowconfigure(0, weight=1)

        # ====== 左侧面板 ======
        left_f = tk.Frame(main_f, bg='white', relief=tk.SOLID, borderwidth=1)
        left_f.grid(row=0, column=0, sticky='nsew', padx=(0, 4))
        left_f.grid_rowconfigure(2, weight=1)
        left_f.grid_columnconfigure(0, weight=1)

        # 输入区
        tk.Label(left_f, text="✍️ 记录你的科学遐想", bg='white',
                 font=('TkDefaultFont', 13, 'bold')).grid(row=0, column=0, sticky='w', padx=12, pady=(10, 2))

        self.input_text = tk.Text(left_f, height=5, font=('TkDefaultFont', 12),
                                   relief=tk.SOLID, borderwidth=1, padx=8, pady=6)
        self.input_text.grid(row=1, column=0, sticky='ew', padx=12, pady=(0, 5))
        self.input_text.bind('<Control-Return>', lambda e: self._stash())

        btn_f = tk.Frame(left_f, bg='white')
        btn_f.grid(row=1, column=0, sticky='e', padx=12, pady=(0, 5))
        ttk.Button(btn_f, text="📌 暂存此句 (Ctrl+Enter)", command=self._stash).pack(side=tk.LEFT, padx=1)
        ttk.Button(btn_f, text="清空输入", command=lambda: self.input_text.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=1)

        # 暂存区
        stash_label_f = tk.Frame(left_f, bg='white')
        stash_label_f.grid(row=2, column=0, sticky='ew', padx=12, pady=(0, 2))
        stash_label_f.grid_columnconfigure(1, weight=1)
        tk.Label(stash_label_f, text="📋 当前暂存区", bg='white',
                 font=('TkDefaultFont', 11, 'bold')).pack(side=tk.LEFT)
        self.stash_count_label = tk.Label(stash_label_f, text="0 条", bg='white',
                                           fg='#999', font=('TkDefaultFont', 10))
        self.stash_count_label.pack(side=tk.RIGHT)

        self.stash_box = tk.Text(left_f, height=6, font=('TkDefaultFont', 11),
                                  bg='#f8f9fa', relief=tk.SOLID, borderwidth=1,
                                  state=tk.DISABLED, padx=8, pady=6, wrap=tk.WORD)
        self.stash_box.grid(row=3, column=0, sticky='nsew', padx=12, pady=(0, 5))

        # 发送按钮
        send_f = tk.Frame(left_f, bg='white')
        send_f.grid(row=4, column=0, sticky='ew', padx=12, pady=(0, 8))
        self.send_btn = tk.Button(send_f, text="🚀 发送给 AI 生成报告",
                                   command=self._send_to_ai,
                                   bg='#2ed573', fg='white',
                                   font=('TkDefaultFont', 13, 'bold'),
                                   relief=tk.FLAT, padx=20, pady=6, cursor='hand2')
        self.send_btn.pack(fill=tk.X)

        # 状态栏
        self.status_var = tk.StringVar(value="💡 输入灵感碎片 → 暂存累积 → 一键AI分析")
        self.status_label = tk.Label(left_f, textvariable=self.status_var,
                                      bg='#e8f4fd', fg='#1a73e8',
                                      font=('TkDefaultFont', 10),
                                      relief=tk.FLAT, padx=8, pady=4)
        self.status_label.grid(row=5, column=0, sticky='ew', padx=12, pady=(0, 10))

        # ====== 右侧面板 ======
        right_f = tk.Frame(main_f, bg='white', relief=tk.SOLID, borderwidth=1, width=360)
        right_f.grid(row=0, column=1, sticky='nsew', padx=(4, 0))
        right_f.grid_propagate(False)
        right_f.grid_rowconfigure(1, weight=1)
        right_f.grid_columnconfigure(0, weight=1)

        # 报告库标题
        report_header = tk.Frame(right_f, bg='white')
        report_header.grid(row=0, column=0, sticky='ew', padx=12, pady=(10, 5))
        tk.Label(report_header, text="📚 报告库", bg='white',
                 font=('TkDefaultFont', 13, 'bold')).pack(side=tk.LEFT)
        self.report_count_label = tk.Label(report_header, text="0 份", bg='white',
                                            fg='#999', font=('TkDefaultFont', 10))
        self.report_count_label.pack(side=tk.LEFT, padx=8)
        ttk.Button(report_header, text="🔄 刷新", command=self._refresh_report_list).pack(side=tk.RIGHT)

        # 报告列表
        list_f = tk.Frame(right_f, bg='white')
        list_f.grid(row=1, column=0, sticky='nsew', padx=12, pady=(0, 5))
        list_f.grid_rowconfigure(0, weight=1)
        list_f.grid_columnconfigure(0, weight=1)

        self.report_listbox = tk.Listbox(list_f, font=('TkDefaultFont', 10),
                                          relief=tk.SOLID, borderwidth=1,
                                          activestyle='none', selectbackground='#e8f4fd')
        self.report_listbox.grid(row=0, column=0, sticky='nsew')
        scroll_r = ttk.Scrollbar(list_f, command=self.report_listbox.yview)
        scroll_r.grid(row=0, column=1, sticky='ns')
        self.report_listbox.configure(yscrollcommand=scroll_r.set)
        self.report_listbox.bind('<Double-Button-1>', lambda e: self._view_report())

        ttk.Button(right_f, text="📄 查看选中报告", command=self._view_report).grid(
            row=2, column=0, sticky='ew', padx=12, pady=(0, 10))

    # ============================================================
    #  功能逻辑
    # ============================================================

    def _stash(self):
        """暂存当前输入"""
        text = self.input_text.get(1.0, tk.END).strip()
        if not text:
            self._set_status("请输入内容后再暂存", 'error')
            return
        self.stash_texts.append(text)
        self.input_text.delete(1.0, tk.END)
        self.input_text.focus()
        self._update_stash_display()
        self._set_status(f"✅ 已暂存第 {len(self.stash_texts)} 条", 'success')

    def _update_stash_display(self):
        """刷新暂存区显示"""
        self.stash_box.config(state=tk.NORMAL)
        self.stash_box.delete(1.0, tk.END)
        for i, t in enumerate(self.stash_texts, 1):
            self.stash_box.insert(tk.END, f"[{i}] {t}\n")
        self.stash_box.see(tk.END)
        self.stash_box.config(state=tk.DISABLED)
        self.stash_count_label.config(text=f"{len(self.stash_texts)} 条")

    def _send_to_ai(self):
        """发送给 AI 分析（自动选择本地算法或 DeepSeek API）"""
        if not self.stash_texts:
            messagebox.showwarning("提示", "暂存区为空，请先输入并暂存内容")
            return

        full_text = '\n'.join(self.stash_texts)

        # 清空暂存区（释放UI）
        self.stash_texts = []
        self._update_stash_display()
        self.send_btn.config(state=tk.DISABLED, text="⏳ 生成中...")
        self._set_status("⏳ 报告生成中，请稍后...", 'generating')

        # 回调：成功
        def on_complete(report_text):
            try:
                filepath = self.exporter.to_txt(full_text, report_text)
                filename = os.path.basename(filepath)
                self.after(0, lambda: self._on_task_done(filename, None))
            except Exception as e:
                self.after(0, lambda: self._on_task_done(None, str(e)))

        # 回调：失败
        def on_error(error_msg):
            try:
                filepath = self.exporter.to_txt(
                    full_text, f"[分析失败]\n{error_msg}")
                filename = os.path.basename(filepath)
                self.after(0, lambda: self._on_task_done(filename, None))
            except Exception as e:
                self.after(0, lambda: self._on_task_done(None, str(e)))

        # 判断模式：本地（同步）vs AI（异步）
        if not self.analyzer.use_ai or self.analyzer.ai_service is None:
            # 本地模式：后台线程执行同步分析
            thread = threading.Thread(
                target=lambda: self._run_local_analysis(full_text, on_complete, on_error),
                daemon=True
            )
            thread.start()
        else:
            # AI 模式：直接调用 analyze()（内部自动异步）
            self.analyzer.analyze(
                text=full_text,
                on_complete=on_complete,
                on_error=on_error,
            )

    def _run_local_analysis(self, text, on_complete, on_error):
        """后台线程：本地算法分析"""
        try:
            report = self.analyzer.generate_local_report(text)
            self.after(0, lambda: on_complete(report))
        except Exception as e:
            self.after(0, lambda: on_error(str(e)))

    def _on_task_done(self, filename, error):
        """任务完成后的UI更新"""
        self.send_btn.config(state=tk.NORMAL, text="🚀 发送给 AI 生成报告")
        if filename:
            self._set_status(f"✅ 报告已生成：{filename}", 'success')
        else:
            self._set_status(f"❌ 生成失败：{error}", 'error')
        self._refresh_report_list()

    def _refresh_report_list(self):
        """刷新报告列表"""
        self.report_listbox.delete(0, tk.END)
        reports = self.storage.list_reports()
        if not reports:
            self.report_listbox.insert(tk.END, "(暂无报告)")
            self.report_count_label.config(text="0 份")
        else:
            for r in reports:
                display = f"📄 {r['name']}  ({r['time']}, {r['size']}B)"
                self.report_listbox.insert(tk.END, display)
            self.report_count_label.config(text=f"{len(reports)} 份")

    def _view_report(self):
        """查看选中的报告"""
        sel = self.report_listbox.curselection()
        if not sel:
            messagebox.showinfo("提示", "请先在列表中选择一份报告")
            return
        text = self.report_listbox.get(sel[0])
        if "(暂无报告)" in text:
            return

        # 从显示文本中提取文件名
        filename = text.split("  (")[0].replace("📄 ", "")
        filepath = os.path.join("reports", filename)

        if not os.path.exists(filepath):
            messagebox.showerror("错误", "报告文件不存在")
            return

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        self._show_report_modal(filename, content)

    def _show_report_modal(self, filename, content):
        """模态框展示报告内容"""
        modal = tk.Toplevel(self)
        modal.title(f"📄 {filename}")
        modal.geometry("750x600")
        modal.minsize(500, 400)
        modal.transient(self)
        modal.grab_set()

        modal.grid_rowconfigure(1, weight=1)
        modal.grid_columnconfigure(0, weight=1)

        tk.Label(modal, text=f"📄 {filename}", font=('TkDefaultFont', 13, 'bold'),
                 anchor=tk.W).grid(row=0, column=0, sticky='ew', padx=12, pady=(10, 5))

        text_w = scrolledtext.ScrolledText(modal, font=('Courier New', 11),
                                            wrap=tk.WORD, padx=10, pady=10)
        text_w.grid(row=1, column=0, sticky='nsew', padx=12, pady=(0, 5))
        text_w.insert(tk.END, content)
        text_w.config(state=tk.DISABLED)

        tk.Button(modal, text="关闭", command=modal.destroy,
                  bg='#4a6cf7', fg='white', font=('TkDefaultFont', 10, 'bold'),
                  relief=tk.FLAT, padx=20, pady=4).grid(row=2, column=0, pady=(0, 10))

    # ============================================================
    #  API Key 管理
    # ============================================================

    def _load_api_key(self):
        """从 .env 文件加载 API Key，不存在则使用默认值"""
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        if k.strip() == 'DEEPSEEK_API_KEY':
                            self.api_key = v.strip()
                            return
        # 无 .env 文件或未配置 → 使用默认 Key
        self.api_key = DEFAULT_API_KEY
        self._save_api_key()

    def _save_api_key(self):
        """将当前 API Key 写入 .env 文件"""
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(f"DEEPSEEK_API_KEY={self.api_key}\n")

    def _reload_analyzer(self):
        """更换 API Key 后重新初始化分析器"""
        use_real_ai = bool(self.api_key) and self.api_key != "your-api-key-here"
        if use_real_ai:
            ai_service = AIService(api_key=self.api_key)
            self.analyzer = ReportAnalyzer(use_ai=True, ai_service=ai_service)
            mode_text = "DeepSeek AI"
        else:
            self.analyzer = ReportAnalyzer(use_ai=False)
            mode_text = "local"
        self._set_status("[模式] " + mode_text + " | Key 已更新", 'success')

    def _open_settings(self):
        """打开设置对话框"""
        dialog = tk.Toplevel(self)
        dialog.title("\u2699\ufe0f 设置 - API Key")
        dialog.geometry("520x220")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg='white')

        # 标题
        tk.Label(dialog, text="DeepSeek API Key \u8bbe\u7f6e",
                 font=('TkDefaultFont', 14, 'bold'), bg='white').pack(pady=(15, 5))

        tk.Label(dialog, text="\u8bf7\u8f93\u5165\u4f60\u7684 DeepSeek API Key\uff0c\u5b58\u50a8\u540e\u751f\u6548\uff1a",
                 font=('TkDefaultFont', 10), bg='white', fg='#666').pack()

        # 输入框
        entry_f = tk.Frame(dialog, bg='white')
        entry_f.pack(pady=(10, 5), padx=20, fill=tk.X)
        tk.Label(entry_f, text="API Key:", bg='white',
                 font=('TkDefaultFont', 10, 'bold')).pack(anchor=tk.W)
        key_entry = tk.Entry(entry_f, font=('TkDefaultFont', 11),
                              relief=tk.SOLID, borderwidth=1, show='*')
        key_entry.pack(fill=tk.X, ipady=4, pady=(2, 0))
        key_entry.insert(0, self.api_key)

        # 显示/隐藏切换
        show_var = tk.BooleanVar(value=False)
        def toggle_show():
            key_entry.config(show='' if show_var.get() else '*')
        tk.Checkbutton(entry_f, text="\u663e\u793a API Key", variable=show_var,
                       command=toggle_show, bg='white').pack(anchor=tk.W, pady=(2, 0))

        # 按钮
        btn_f = tk.Frame(dialog, bg='white')
        btn_f.pack(pady=(5, 15))

        def on_save():
            new_key = key_entry.get().strip()
            if not new_key:
                messagebox.showwarning("\u63d0\u793a", "API Key \u4e0d\u80fd\u4e3a\u7a7a")
                return
            self.api_key = new_key
            self._save_api_key()
            self._reload_analyzer()
            dialog.destroy()
            messagebox.showinfo("\u6210\u529f", "API Key \u5df2\u66f4\u65b0\uff0c\u4e0b\u6b21\u53d1\u9001\u65f6\u751f\u6548")

        def on_reset():
            key_entry.delete(0, tk.END)
            key_entry.insert(0, DEFAULT_API_KEY)

        tk.Button(btn_f, text="\u4fdd\u5b58", command=on_save,
                  bg='#4a6cf7', fg='white', font=('TkDefaultFont', 10, 'bold'),
                  relief=tk.FLAT, padx=25, pady=4, cursor='hand2').pack(side=tk.LEFT, padx=4)
        tk.Button(btn_f, text="\u6062\u590d\u9ed8\u8ba4", command=on_reset,
                  bg='#e8e8e8', fg='#555', font=('TkDefaultFont', 10),
                  relief=tk.FLAT, padx=15, pady=4, cursor='hand2').pack(side=tk.LEFT, padx=4)
        tk.Button(btn_f, text="\u53d6\u6d88", command=dialog.destroy,
                  bg='#e8e8e8', fg='#555', font=('TkDefaultFont', 10),
                  relief=tk.FLAT, padx=15, pady=4, cursor='hand2').pack(side=tk.LEFT, padx=4)

    def _set_status(self, msg, msg_type='info'):
        """设置状态栏"""
        colors = {
            'info': ('#e8f4fd', '#1a73e8'),
            'success': ('#e6f9ed', '#1a8d4a'),
            'error': ('#fde8e8', '#d63031'),
            'generating': ('#fff8e1', '#e6a800'),
        }
        bg, fg = colors.get(msg_type, ('#e8f4fd', '#1a73e8'))
        self.status_label.config(text=msg, bg=bg, fg=fg)
        self.status_var.set(msg)


if __name__ == "__main__":
    app = ScienceGenieApp()
    app.mainloop()
