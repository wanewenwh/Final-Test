# 科学遐思精灵 (Inspiration Storage Genie)

## 项目简介

一款基于 Web 的异步灵感收集与 AI 深度研究工具。允许用户碎片化记录科学遐想，一键触发 AI 分析（DeepSeek API），AI 生成过程不阻塞用户的实时创作流。

## 运行方式

### 桌面版（推荐，无需浏览器）

```bash
python main.py
```

直接弹出 Tkinter 桌面窗口，双栏布局：
- 左侧：输入灵感 → 暂存累积 → 发送给AI → 状态提示
- 右侧：报告列表 → 双击查看完整报告

### Web 版（需要浏览器）

```bash
pip install flask
python app.py
```

浏览器访问: http://127.0.0.1:5000

### 4. 运行测试

```bash
cd tests
python -m unittest test_file_storage.py -v
python -m unittest test_ai_service.py -v
python -m unittest discover -v   # 运行所有测试
```

## 项目结构

```
科学遐思精灵/
├── app.py                    # Flask 主入口
├── ai_service.py             # AI 调用服务（OOP）
├── file_storage.py           # 文件存储服务（OOP）
├── requirements.txt          # 依赖清单
├── .env.example              # 环境变量模板
├── .gitignore
├── README.md
│
├── templates/
│   └── index.html            # 前端界面（双栏布局）
│
├── reports/                  # 报告存储目录（自动生成）
│
├── tests/
│   ├── test_file_storage.py  # 文件存储单元测试
│   └── test_ai_service.py    # AI 服务单元测试
│
└── docs/
    ├── 01_需求分析.md
    ├── 02_总体设计.md
    ├── 03_详细设计.md
    ├── 04_测试报告.md
    └── 05_用户手册.md
```

## 使用流程

1. 在左侧文本框输入灵感碎片
2. 点击「暂存此句」或按 Ctrl+Enter 暂存
3. 重复步骤 1-2 累积完整想法
4. 点击「🚀 发送给 AI 生成报告」
5. 暂存区自动清空，可继续输入新想法
6. 右侧报告列表自动刷新，点击查看 AI 生成的结构化报告
