# Word 引用插入

在 Word 中快速插入参考文献脚注。

本项目提供两种方式：

---

## 方案 A：独立桌面版（推荐 ✅）

Python 桌面应用，通过 COM 自动化直接操控 Word，**可以插入原生 Word 脚注**。

### 快速使用

**方法一：直接运行 EXE（已打包）**

1. 打开 `desktop/dist/` 文件夹
2. 双击 `Word引用插入.exe`
3. 确保 Word 已打开一个文档
4. 粘贴参考文献 → 解析 → 点击条目 → 脚注自动插入

**方法二：从源码运行**

```
cd desktop
启动桌面版.bat
```

**打包成 EXE：**

```
cd desktop
构建EXE.bat
```

### 技术原理

```
Python + tkinter GUI → win32com (COM) → Word OOM
                                        ↓
                              Selection.Footnotes.Add(Range)
                                        ↓
                              Word 原生脚注 ✓
```

### 特点

- ✅ **使用 Word 原生脚注**（不是文本模拟）
- ✅ 单一 EXE，无需安装，无需命令行常驻
- ✅ 自动连接正在运行的 Word
- ✅ 支持 `[N]` 前缀解析和自动编号

---

## 方案 B：Office.js 插件（技术验证版 ⚠️）

基于 Office.js 的 Word 任务窗格加载项。

### 快速开始

双击 `启动.bat`，或运行：

```bash
npm install
npm run start
```

启动后访问 `http://localhost:3000` 确认页面正常。

### 注册插件

见 `使用说明.md` 中的详细注册步骤。

### ⚠️ 已知限制

Office.js **不提供原生脚注插入 API**。`useFootnoteInserter.ts` 中使用的 `footnotes.add()` 方法不是真实 API，**此方案的脚注插入功能不可用**。

如需使用原生脚注功能，请使用方案 A（桌面版）。

### 技术栈

- React 18 + TypeScript
- Fluent UI React Components
- Office.js (Word JavaScript API)
- Vite

---

## 项目结构

```
├── desktop/                        # 【推荐】桌面版 (Python + COM)
│   ├── main.py                     # 入口
│   ├── app.py                      # tkinter GUI
│   ├── word_com.py                 # Word COM 自动化
│   ├── parser.py                   # 引用解析
│   ├── dist/Word引用插入.exe       # 打包好的 EXE
│   ├── 构建EXE.bat                 # 重新打包
│   └── 启动桌面版.bat              # 从源码启动
├── src/                            # Office.js 插件 (React)
├── dist/                           # Office.js 构建输出
├── manifest.xml                    # Office 加载项清单
├── 加载项共享目录/                  # 网络共享注册目录
├── 使用说明.md                     # Office.js 注册指南
└── package.json
```
