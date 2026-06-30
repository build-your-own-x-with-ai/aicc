# AICC - ASCII C Compiler

```
╔═══════════════════════════════════════════════╗
║                                               ║
║      █████╗ ██╗ ██████╗ ██████╗              ║
║     ██╔══██╗██║██╔════╝██╔════╝              ║
║     ███████║██║██║     ██║                   ║
║     ██╔══██║██║██║     ██║                   ║
║     ██║  ██║██║╚██████╗╚██████╗              ║
║     ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═════╝              ║
║                                               ║
║          ASCII C Compiler                     ║
║                                               ║
║    C Source → ARM64 Assembly → Executable     ║
║                                               ║
╚═══════════════════════════════════════════════╝
```

[![Tests](https://img.shields.io/badge/tests-78%20passed-brightgreen)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](tests/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

一个从零实现的 **完整、可工作的 C 语言编译器**，用于教学和学习编译器原理。支持真实的 C 程序编译和运行。

## ✨ 特性

- ✅ **完整的编译器流程**：词法 → 语法 → 语义 → 代码生成 → 可执行文件
- ✅ **ARM64 原生支持**：为 Apple Silicon 优化
- ✅ **真实可用**：能够编译并运行真实的 C 程序
- ✅ **测试驱动**：78 个测试，100% 通过率
- ✅ **教学友好**：清晰的代码结构和详细注释
- ✅ **命令行工具**：完整的 CLI 体验

## 🚀 快速开始

```bash
# 1. 克隆并安装
git clone <repository-url>
cd aicc
python3 -m venv venv
source venv/bin/activate
pip install -e .

# 2. 编译你的第一个程序
cat > hello.c << 'EOF'
int main() {
    return 42;
}
EOF

python -m aicc hello.c -o hello

# 3. 运行程序
./hello
echo $?  # 输出: 42
```

## 📦 支持的 C 特性

| 类别 | 支持的特性 |
|------|-----------|
| **数据类型** | `int` |
| **运算符** | 算术 (`+`, `-`, `*`, `/`, `%`)<br>关系 (`==`, `!=`, `<`, `>`, `<=`, `>=`)<br>逻辑 (`&&`, `||`, `!`) |
| **语句** | 变量声明、赋值、`return`<br>`if-else`、`while`、`for`<br>`break`、`continue` |
| **函数** | 函数定义、调用、递归<br>最多 8 个参数 |
| **作用域** | 块级作用域、函数作用域<br>变量遮蔽 |

## 💡 示例

### Hello World
```c
int main() {
    return 42;
}
```

### 递归斐波那契
```c
int fib(int n) {
    if (n <= 1) {
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}

int main() {
    return fib(10);  // 返回 55
}
```

### 循环求和
```c
int main() {
    int sum = 0;
    for (int i = 1; i <= 10; i = i + 1) {
        sum = sum + i;
    }
    return sum;  // 返回 55
}
```

## 🛠️ 使用指南

### 基本用法

```bash
# 编译源文件
aicc source.c -o output

# 详细输出
aicc source.c -o output -v

# 只生成汇编（不链接）
aicc source.c -S -o output.s
```

### 调试选项

```bash
# 只进行词法分析
aicc source.c --lex-only

# 只进行语法分析（打印 AST）
aicc source.c --parse-only
```

### 运行示例

```bash
# 编译并运行示例程序
aicc examples/hello.c -o hello && ./hello; echo $?       # 42
aicc examples/fib.c -o fib && ./fib; echo $?             # 55
aicc examples/arithmetic.c -o arithmetic && ./arithmetic; echo $?  # 1
```

## 🏗️ 架构设计

```
┌─────────────┐
│  C Source   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Lexer (词法)   │  ← 206 行
│  tokens.py      │
└──────┬──────────┘
       │ Token 流
       ▼
┌─────────────────┐
│  Parser (语法)  │  ← 419 行
│  ast_nodes.py   │
└──────┬──────────┘
       │ AST
       ▼
┌─────────────────┐
│ Semantic (语义) │  ← 481 行
│ 符号表 + 类型   │
└──────┬──────────┘
       │ 带类型的 AST
       ▼
┌─────────────────┐
│ Codegen (生成)  │  ← 357 行
│ ARM64 汇编      │
└──────┬──────────┘
       │ .s 文件
       ▼
┌─────────────────┐
│  as + ld        │
│  (系统工具)     │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│   Executable    │
└─────────────────┘
```

### 核心组件

| 组件 | 文件 | 行数 | 功能 |
|------|------|------|------|
| **词法分析器** | `lexer.py` | 206 | Token 流生成 |
| **语法分析器** | `parser.py` | 419 | AST 构建 |
| **语义分析器** | `semantic.py` | 481 | 类型检查、符号表 |
| **代码生成器** | `codegen_arm64.py` | 357 | ARM64 汇编 |
| **命令行工具** | `__main__.py` | 194 | CLI 接口 |
| **AST 定义** | `ast_nodes.py` | 174 | 节点结构 |
| **Token 定义** | `tokens.py` | 89 | 词法单元 |

**总计**：1,961 行源代码 + 1,204 行测试代码 = **3,165 行**

## 🧪 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_lexer.py -v       # 词法分析器
pytest tests/test_parser.py -v      # 语法分析器
pytest tests/test_semantic.py -v    # 语义分析器
pytest tests/test_codegen.py -v     # 代码生成器

# 测试覆盖率
pytest --cov=src/aicc --cov-report=html tests/
```

### 测试统计

| 模块 | 测试数 | 状态 |
|------|--------|------|
| 词法分析 | 11 | ✅ 100% |
| 语法分析 | 19 | ✅ 100% |
| 语义分析 | 26 | ✅ 100% |
| 代码生成 | 15 | ✅ 100% |
| 集成测试 | 7 | ✅ 100% |
| **总计** | **78** | **✅ 100%** |

## 📚 项目结构

```
aicc/
├── src/aicc/               # 编译器源代码
│   ├── __init__.py
│   ├── __main__.py         # CLI 入口
│   ├── tokens.py           # Token 定义
│   ├── lexer.py            # 词法分析器
│   ├── ast_nodes.py        # AST 节点
│   ├── parser.py           # 语法分析器
│   ├── semantic.py         # 语义分析器
│   ├── codegen.py          # 代码生成基类
│   └── codegen_arm64.py    # ARM64 代码生成器
├── tests/                  # 测试套件
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_semantic.py
│   ├── test_codegen.py
│   └── test_integration.py
├── examples/               # 示例程序
│   ├── hello.c
│   ├── fib.c
│   └── arithmetic.c
├── docs/                   # 文档和 Logo
│   ├── logo.txt
│   ├── logo.svg
│   └── ...
├── scripts/                # 辅助脚本
│   ├── run_tests.sh
│   └── show_logo.py        # 显示彩色 Logo
├── README.md               # 本文件
├── FINAL_SUMMARY.md        # 完整项目总结
├── QUICK_REFERENCE.md      # 快速参考手册
├── PROJECT_STATUS.md       # 项目状态报告
├── LICENSE                 # MIT 许可证
├── pyproject.toml          # 项目配置
└── requirements.txt        # 依赖列表
```

## 🎯 技术亮点

### 词法分析
- 手写状态机
- 精确的行号/列号追踪
- 注释处理（`//` 和 `/* */`）

### 语法分析
- 递归下降解析
- Pratt 优先级爬升算法
- 清晰的 AST 结构

### 语义分析
- 嵌套作用域符号表
- 完整的类型检查
- 详细的错误检测

### 代码生成
- ARM64 AArch64 指令集
- System V ABI 调用约定
- 栈式表达式求值
- 高效的寄存器使用

## 🗺️ 开发历程

| 阶段 | 内容 | 状态 |
|------|------|------|
| **Sprint 1** | 词法分析器 + 语法分析器 | ✅ 已完成 |
| **Sprint 2** | 语义分析器 + 符号表 | ✅ 已完成 |
| **Sprint 3** | ARM64 代码生成器 + CLI | ✅ 已完成 |
| **Sprint 4** | 优化和扩展功能 | 🔮 未来计划 |

### Git 提交历史

```
29f4da0 Add ASCII logo to README
ee4fef0 Add AICC logos and branding
00d6909 Add quick reference guide
0cdd15e Add final project summary
e355da9 Update README: Sprint 3 completion
3b748c1 Implement Sprint 3: ARM64 code generator and CLI
99da53e Update README: Sprint 2 completion
8e4a54b Implement Sprint 2: Semantic analyzer
6625f5b Add comprehensive project status report
57b620f Add documentation, examples, and test scripts
8118638 Initial implementation: lexer and parser
```

## 🌟 未来扩展

### 短期计划
- [ ] 字符串字面量支持
- [ ] `char` 类型
- [ ] 数组基础支持
- [ ] 更好的错误信息

### 中期计划
- [ ] 指针和指针运算
- [ ] 结构体（`struct`）
- [ ] 预处理器（`#include`, `#define`）
- [ ] 更多数据类型（`long`, `float`）

### 长期计划
- [ ] x86-64 后端
- [ ] RISC-V 后端
- [ ] 代码优化（寄存器分配、常量折叠）
- [ ] Linux 支持

## 📖 学习资源

- **[Crafting Interpreters](https://craftinginterpreters.com/)** - 优秀的编译器入门教程
- **[chibicc](https://github.com/rui314/chibicc)** - Rui Ueyama 的教学型 C 编译器
- **[龙书](https://en.wikipedia.org/wiki/Compilers:_Principles,_Techniques,_and_Tools)** - 编译器原理经典教材
- **[虎书](https://www.cs.princeton.edu/~appel/modern/)** - Modern Compiler Implementation

## 🤝 贡献

欢迎贡献！如果你想：
- 报告 bug
- 提出新功能
- 提交代码
- 改进文档

请查看 [CONTRIBUTING.md](CONTRIBUTING.md)（待创建）或直接提交 Issue/PR。

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。

## 🙏 致谢

本项目受到以下优秀项目的启发：

- **[chibicc](https://github.com/rui314/chibicc)** by Rui Ueyama - 教学型 C 编译器
- **[8cc](https://github.com/rui314/8cc)** by Rui Ueyama - 另一个小型 C 编译器
- **[TCC](https://bellard.org/tcc/)** by Fabrice Bellard - Tiny C Compiler

特别感谢 **Claude Opus 4.8** 协助完成这个项目！

---

## 📮 联系方式

- 项目地址：`/Users/i/Code/Build_Your_Onw_X_With_AI/aicc`
- 完成日期：2026-06-30
- 版本：v0.1.0

---

**⚠️ 注意**：这是一个教学项目，专注于展示编译器的核心概念和实现技术。不适用于生产环境。

**💡 提示**：运行 `python scripts/show_logo.py` 查看彩色 Logo！

---

<div align="center">

**Made with ❤️ for learning and education**

*证明编译器并不神秘 —— 它是可以理解、可以实现、可以测试的工程项目*

</div>
