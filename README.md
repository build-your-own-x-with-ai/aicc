# AICC - ASCII C Compiler

一个从零实现的 C 语言编译器，用于教学和学习编译器原理。

## 特性

- ✅ **词法分析器**：支持整数、关键字、标识符、运算符
- ✅ **语法分析器**：递归下降 + 优先级爬升算法
- ✅ **语义分析器**：符号表、类型检查、作用域管理
- ✅ **完整测试覆盖**：63 个单元测试和集成测试
- 🚧 **代码生成**：x86-64/ARM64 汇编（开发中）

## 当前支持的 C 特性

### 第一阶段（已完成）+ 第二阶段（已完成）

- **数据类型**：`int`
- **运算符**：算术 (`+`, `-`, `*`, `/`, `%`)、关系 (`==`, `!=`, `<`, `>`, `<=`, `>=`)、逻辑 (`&&`, `||`, `!`)
- **语句**：变量声明、赋值、`return`、`if-else`、`while`、`for`
- **函数**：函数定义、函数调用、参数传递、递归
- **作用域**：块级作用域、函数作用域、变量遮蔽
- **类型检查**：变量类型、函数签名、返回值类型
- **错误检测**：未定义变量、重复定义、类型不匹配、无效的 break/continue

### 示例程序

```c
int fib(int n) {
    if (n <= 1) {
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}

int main() {
    return fib(10);
}
```

## 安装

```bash
# 克隆仓库
git clone <repository-url>
cd aicc

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -e .
pip install -r requirements-dev.txt
```

## 使用

```bash
# 编译 C 源文件（开发中）
aicc source.c -o output

# 只进行词法分析
aicc source.c --lex-only

# 只进行语法分析（打印 AST）
aicc source.c --parse-only
```

## 开发

```bash
# 运行测试
pytest tests/ -v

# 测试覆盖率
pytest --cov=src/aicc --cov-report=html tests/

# 代码格式化
black src/ tests/

# 类型检查
mypy src/
```

## 项目结构

```
aicc/
├── src/aicc/           # 编译器源代码
│   ├── lexer.py        # 词法分析器
│   ├── parser.py       # 语法分析器
│   ├── tokens.py       # Token 定义
│   ├── ast_nodes.py    # AST 节点定义
│   └── ...
├── tests/              # 测试套件
│   ├── test_lexer.py
│   ├── test_parser.py
│   └── fixtures/       # 测试用例
├── examples/           # 示例程序
├── docs/               # 文档
└── README.md
```

## 架构

AICC 采用经典的编译器架构：

```
源代码 → [词法分析] → Token 流 → [语法分析] → AST
      → [语义分析] → 带类型的 AST → [代码生成] → 汇编代码（开发中）
```

### 词法分析器（Lexer）

- 手写状态机实现
- 支持整数字面量、关键字、标识符、运算符
- 行号和列号追踪，便于错误报告
- 处理注释（`//` 和 `/* */`）

### 语法分析器（Parser）

- 递归下降解析
- 优先级爬升法（Pratt Parsing）处理表达式
- 构建抽象语法树（AST）
- 详细的错误信息

### 语义分析器（已完成）

- 符号表管理（作用域、变量绑定）
- 类型检查
- 语义错误检测：
  - 未定义变量/函数
  - 重复定义
  - 类型不匹配
  - 函数签名验证
  - break/continue 位置检查

### 代码生成器（开发中）

- 目标架构：x86-64、ARM64
- AT&T 风格汇编
- 调用系统汇编器和链接器

## 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_lexer.py -v

# 查看测试覆盖率
pytest --cov=src/aicc tests/
```

当前测试覆盖：
- ✅ 词法分析器：11 个测试
- ✅ 语法分析器：19 个测试
- ✅ 语义分析器：26 个测试
- ✅ 集成测试：7 个测试
- **总计**：63 个测试（100% 通过）

## 路线图

- [x] **阶段 1**：词法分析和语法分析（已完成）
- [x] **阶段 2**：语义分析和符号表（已完成）
- [ ] **阶段 3**：代码生成（x86-64/ARM64）
- [ ] **阶段 4**：优化和完善

## 学习资源

- [Crafting Interpreters](https://craftinginterpreters.com/) - 优秀的编译器教程
- [chibicc](https://github.com/rui314/chibicc) - 小型 C 编译器参考实现
- [龙书](https://en.wikipedia.org/wiki/Compilers:_Principles,_Techniques,_and_Tools) - 经典编译器教材

## 贡献

欢迎贡献！请阅读 CONTRIBUTING.md 了解详情。

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 致谢

本项目受到以下项目的启发：
- [chibicc](https://github.com/rui314/chibicc) by Rui Ueyama
- [8cc](https://github.com/rui314/8cc) by Rui Ueyama
- [TCC](https://bellard.org/tcc/) by Fabrice Bellard

---

**注意**：这是一个教学项目，不适用于生产环境。
