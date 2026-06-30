# ASCII C 语言编译器实现计划

## Context（背景）

本项目旨在从零实现一个功能完整的 C 语言编译器 (AICC - ASCII C Compiler)，用于教学和学习编译器原理。当前项目是一个空的 Git 仓库，需要完整搭建：

- **目标**：实现一个能够将 C 源代码编译为可执行文件的编译器
- **用途**：教学项目，重点在于代码清晰度和可理解性
- **要求**：包括完整的测试套件、README 文档、Git 版本管理
- **目标平台**：x86-64 Linux 和 ARM64 macOS

## 技术栈选择

### 实现语言：Python

**理由**：
- 代码清晰度高，更易理解编译器核心概念
- 快速原型开发，专注编译器逻辑而非底层细节
- 丰富的测试生态（pytest）和类型提示支持
- 调试友好，适合迭代学习

**权衡**：性能较 C/Rust 慢，但对教学项目不是瓶颈

### 目标代码：x86-64/ARM64 汇编

- 生成 AT&T 风格汇编代码
- 调用系统汇编器（`as`）和链接器（`gcc`/`ld`）完成最终可执行文件生成
- 支持 macOS (ARM64) 和 Linux (x86-64) 双平台

---

## 项目架构

### 目录结构

```
aicc/
├── README.md                # 项目文档
├── LICENSE                  # MIT License
├── pyproject.toml           # Python 项目配置
├── requirements.txt         # 依赖列表
├── requirements-dev.txt     # 开发依赖
│
├── src/aicc/               # 编译器源代码
│   ├── __init__.py
│   ├── __main__.py         # CLI 入口
│   ├── tokens.py           # Token 定义
│   ├── lexer.py            # 词法分析器
│   ├── ast_nodes.py        # AST 节点定义
│   ├── parser.py           # 语法分析器
│   ├── semantic.py         # 语义分析器
│   ├── codegen.py          # 代码生成基类
│   ├── codegen_x64.py      # x86-64 代码生成
│   ├── codegen_arm64.py    # ARM64 代码生成
│   └── utils.py            # 工具函数（错误报告）
│
├── tests/                   # 测试套件
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_semantic.py
│   ├── test_codegen.py
│   ├── test_integration.py
│   └── fixtures/           # 测试用例 C 源文件
│       ├── phase1/         # 第一阶段测试
│       ├── phase2/         # 第二阶段测试
│       └── phase3/         # 第三阶段测试
│
├── examples/               # 示例 C 程序
│   ├── hello.c
│   ├── fib.c
│   └── array_sum.c
│
├── docs/                   # 详细文档
│   ├── architecture.md     # 架构设计
│   ├── grammar.md          # 支持的语法（BNF）
│   └── codegen.md          # 代码生成策略
│
└── scripts/                # 辅助脚本
    └── run_tests.sh
```

### 模块职责

| 模块 | 职责 |
|------|------|
| `tokens.py` | Token 类型定义（枚举） |
| `lexer.py` | 词法分析：源代码 → Token 流 |
| `ast_nodes.py` | AST 节点数据类定义 |
| `parser.py` | 语法分析：Token 流 → AST |
| `semantic.py` | 语义分析：类型检查、符号表、作用域 |
| `codegen.py` | 代码生成抽象层 |
| `codegen_x64.py` | x86-64 汇编生成 |
| `codegen_arm64.py` | ARM64 汇编生成 |
| `utils.py` | 错误报告、位置追踪 |

---

## 支持的 C 特性（分阶段）

### 第一阶段（MVP - 基础表达式和控制流）

**目标**：能编译简单的算术和条件判断程序

- **数据类型**：`int`（32 位有符号整数）
- **字面量**：整数常量（十进制）
- **运算符**：
  - 算术：`+`, `-`, `*`, `/`, `%`
  - 一元：`-`, `+`
  - 关系：`==`, `!=`, `<`, `>`, `<=`, `>=`
  - 逻辑：`&&`, `||`, `!`
- **语句**：
  - 变量声明：`int x;`, `int y = 5;`
  - 赋值：`x = expr;`
  - `return` 语句
  - `if-else` 语句
- **函数**：单个 `int main()` 函数（无参数）

**里程碑示例**：
```c
int main() {
    int x = 10;
    int y = 20;
    int z = x + y * 2;
    if (z > 40) {
        return 1;
    } else {
        return 0;
    }
}
```

### 第二阶段（循环和函数调用）

**扩展特性**：
- **控制流**：`while`, `for`, `break`, `continue`
- **函数**：
  - 多个函数定义
  - 函数调用（参数传递、返回值）
  - 最多 6 个 int 参数（System V ABI）
- **作用域**：块级作用域 `{...}`

**里程碑示例**：
```c
int fib(int n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}

int main() {
    return fib(10);
}
```

### 第三阶段（指针和数组）

**扩展特性**：
- **指针**：声明、取地址 `&`、解引用 `*`、指针算术
- **数组**：一维数组、数组索引
- **字符串字面量**：`"hello"`（存储在 `.rodata`）
- **新类型**：`char`

**里程碑示例**：
```c
int strlen(char *s) {
    int len = 0;
    while (*s != 0) {
        len = len + 1;
        s = s + 1;
    }
    return len;
}

int main() {
    char *msg = "Hello";
    return strlen(msg);
}
```

### 第四阶段（结构体）（可选扩展）

- `struct` 定义和成员访问
- 类型扩展：`long`, `short`, `unsigned`
- 简单预处理器：`#define`, `#include`

---

## 实现计划（分 Sprint）

### Sprint 1：词法和语法分析（2 周）

**目标**：实现 Lexer 和 Parser，能够将 C 源代码解析为 AST

**关键文件**：
- `src/aicc/tokens.py` - Token 类型枚举和数据类
- `src/aicc/lexer.py` - 词法分析器（状态机实现）
- `src/aicc/ast_nodes.py` - AST 节点定义（dataclass）
- `src/aicc/parser.py` - 递归下降解析器
- `src/aicc/utils.py` - 错误报告工具
- `tests/test_lexer.py` - Lexer 单元测试
- `tests/test_parser.py` - Parser 单元测试

**实现细节**：
1. **Lexer**：手写状态机，支持整数、标识符、关键字、运算符、分隔符
2. **Parser**：递归下降 + 优先级爬升法（Pratt Parsing）处理表达式
3. **AST 节点**：表达式（`IntLiteral`, `BinaryOp`, `Variable`）、语句（`VarDecl`, `Assignment`, `ReturnStmt`, `IfStmt`）、函数（`Function`, `Program`）

**测试覆盖**：
- Lexer：每种 Token 类型的正确识别
- Parser：表达式优先级、语句解析、错误恢复

### Sprint 2：语义分析（1 周）

**目标**：实现符号表、类型检查和作用域管理

**关键文件**：
- `src/aicc/semantic.py` - 语义分析器、符号表
- `tests/test_semantic.py` - 语义分析测试

**实现细节**：
1. **符号表**：哈希表实现，支持嵌套作用域（链式符号表）
2. **类型检查**：简单的 int 类型检查（第一阶段只有 int）
3. **作用域管理**：函数作用域、块级作用域
4. **错误检测**：未定义变量、重复定义、类型不匹配

**测试覆盖**：
- 变量未声明检测
- 变量重复定义检测
- 作用域嵌套正确性

### Sprint 3：代码生成（1.5 周）

**目标**：生成 x86-64/ARM64 汇编代码，并调用系统工具链生成可执行文件

**关键文件**：
- `src/aicc/codegen.py` - 代码生成抽象基类
- `src/aicc/codegen_x64.py` - x86-64 汇编生成
- `src/aicc/codegen_arm64.py` - ARM64 汇编生成
- `src/aicc/__main__.py` - CLI 入口（编译流程）
- `tests/test_codegen.py` - 代码生成单元测试
- `tests/test_integration.py` - 端到端集成测试

**实现细节**：
1. **代码生成策略**：栈式表达式求值，结果存储在累加器寄存器（`rax`/`x0`）
2. **x86-64 寄存器分配**：
   - `rax`：累加器（表达式结果）
   - `rbx`：临时寄存器
   - `rsp`：栈指针
   - `rbp`：栈帧指针
3. **ARM64 寄存器分配**：
   - `x0`：累加器
   - `x1`：临时寄存器
   - `sp`：栈指针
   - `fp`：栈帧指针
4. **汇编生成流程**：
   - 生成 `.s` 汇编文件
   - 调用 `as` 生成 `.o` 目标文件
   - 调用 `ld` 或 `gcc` 链接生成可执行文件

**测试覆盖**：
- 表达式求值正确性
- 变量赋值和读取
- if-else 控制流跳转
- 端到端：编译并运行，检查 exit code

### Sprint 4：项目完善和文档（0.5 周）

**目标**：完善项目配置、文档和示例

**关键文件**：
- `README.md` - 项目说明、安装、使用指南
- `docs/architecture.md` - 架构设计文档
- `docs/grammar.md` - 支持的 C 语法（BNF 格式）
- `docs/codegen.md` - 代码生成策略和 ABI
- `LICENSE` - MIT License
- `pyproject.toml` - Python 项目配置
- `requirements.txt`, `requirements-dev.txt` - 依赖管理
- `.gitignore` - Git 忽略规则
- `examples/hello.c`, `examples/arithmetic.c` - 示例程序
- `scripts/run_tests.sh` - 自动化测试脚本

**文档内容**：
1. **README**：项目概述、特性列表、安装步骤、使用示例、测试运行
2. **架构文档**：编译流程图、模块交互、数据流
3. **语法文档**：支持的 C 语法 BNF 定义
4. **代码生成文档**：汇编生成策略、寄存器分配、调用约定

---

## 测试策略

### 单元测试（`tests/test_*.py`）

**Lexer 测试**：
- 整数字面量识别
- 关键字识别
- 运算符识别
- 注释和空白符跳过
- 错误位置追踪

**Parser 测试**：
- 表达式解析（算术、关系、逻辑）
- 运算符优先级和结合性
- 语句解析（声明、赋值、return、if-else）
- 语法错误检测

**Semantic 测试**：
- 符号表查找
- 未定义变量检测
- 重复定义检测
- 作用域隔离

**CodeGen 测试**：
- 汇编代码格式正确性
- 寄存器使用正确性
- 标签生成唯一性

### 集成测试（`tests/test_integration.py`）

端到端测试流程：
1. 编写测试 C 代码
2. 调用编译器生成可执行文件
3. 运行可执行文件
4. 检查 exit code 或输出

**测试用例集**（`tests/fixtures/`）：
- `phase1/return_constant.c`：`int main() { return 42; }`
- `phase1/arithmetic.c`：`return 2 + 3 * 4;`（测试优先级）
- `phase1/comparison.c`：`return 5 > 3;`（返回 1）
- `phase1/if_else.c`：条件分支测试
- `phase1/variables.c`：变量声明和赋值

### 测试运行

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_lexer.py -v

# 测试覆盖率
pytest --cov=src/aicc --cov-report=html tests/

# 第一阶段集成测试
pytest tests/test_integration.py -k phase1 -v
```

---

## CLI 设计

```bash
# 基本编译（生成可执行文件）
aicc source.c -o output

# 生成汇编代码（不链接）
aicc source.c -S -o output.s

# 只进行词法分析
aicc source.c --lex-only

# 只进行语法分析（打印 AST）
aicc source.c --parse-only

# 详细输出（调试模式）
aicc source.c -v -o output
```

---

## 验证方案

### 第一阶段验证（MVP）

**验证目标**：能编译简单的算术和条件判断程序，并生成可运行的可执行文件

**验证步骤**：

1. **词法分析验证**：
```bash
aicc examples/hello.c --lex-only
# 应输出正确的 Token 流
```

2. **语法分析验证**：
```bash
aicc examples/hello.c --parse-only
# 应输出 AST 树状结构
```

3. **端到端编译验证**：
```bash
aicc examples/hello.c -o hello
./hello
echo $?  # 应输出 42
```

4. **测试套件验证**：
```bash
pytest tests/ -v
# 所有测试应通过（至少 20+ 个测试用例）
```

**验证测试用例**：

```c
// examples/hello.c
int main() {
    return 42;
}
```

```c
// examples/arithmetic.c
int main() {
    int x = 10;
    int y = 20;
    return x + y;  // 应返回 30
}
```

```c
// examples/if_else.c
int main() {
    int x = 5;
    if (x > 3) {
        return 1;
    } else {
        return 0;
    }
    // 应返回 1
}
```

```c
// examples/precedence.c
int main() {
    return 2 + 3 * 4;  // 应返回 14，验证优先级
}
```

### 后续阶段验证

**第二阶段**：验证函数调用和循环（递归斐波那契、for 循环累加）

**第三阶段**：验证指针和数组（字符串长度、数组求和）

---

## 关键实现要点

### 1. Lexer 实现（`lexer.py`）

使用手写状态机：
```python
class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
    
    def tokenize(self) -> Iterator[Token]:
        while self.pos < len(self.source):
            if self.current_char().isspace():
                self.skip_whitespace()
            elif self.current_char().isdigit():
                yield self.read_integer()
            elif self.current_char().isalpha():
                yield self.read_identifier_or_keyword()
            elif self.current_char() == '+':
                yield self.make_token(TokenType.PLUS)
            # ...
```

### 2. Parser 实现（`parser.py`）

递归下降 + 优先级爬升：
```python
def parse_expression(self, min_prec=0):
    left = self.parse_primary()
    while self.current_is_binop():
        prec = self.get_precedence()
        if prec < min_prec:
            break
        op = self.current_token
        self.advance()
        right = self.parse_expression(prec + 1)
        left = BinaryOp(left, op, right)
    return left
```

### 3. 符号表实现（`semantic.py`）

链式符号表支持作用域：
```python
class SymbolTable:
    def __init__(self, parent=None):
        self.symbols = {}
        self.parent = parent
    
    def define(self, name, symbol):
        if name in self.symbols:
            raise SemanticError(f"Redefinition of '{name}'")
        self.symbols[name] = symbol
    
    def lookup(self, name):
        if name in self.symbols:
            return self.symbols[name]
        if self.parent:
            return self.parent.lookup(name)
        return None
```

### 4. 代码生成实现（`codegen_x64.py`）

栈式表达式求值：
```python
def visit_binary_op(self, node):
    # 左操作数 -> rax
    self.visit(node.left)
    self.emit("push %rax")
    
    # 右操作数 -> rax
    self.visit(node.right)
    self.emit("pop %rbx")
    
    # 执行运算
    if node.op == TokenType.PLUS:
        self.emit("add %rbx, %rax")
    elif node.op == TokenType.STAR:
        self.emit("imul %rbx, %rax")
```

---

## 总结

本计划将在约 **5 周时间** 内完成 ASCII C 编译器的第一阶段（MVP）实现，包括：

1. ✅ 完整的词法分析器、语法分析器、语义分析器和代码生成器
2. ✅ 支持基础 C 特性（int 类型、表达式、变量、if-else）
3. ✅ 生成 x86-64/ARM64 汇编并链接为可执行文件
4. ✅ 完善的测试套件（20+ 个测试用例）
5. ✅ 完整的项目文档（README、架构文档、语法文档）

后续可根据学习进度扩展至第二阶段（函数调用、循环）和第三阶段（指针、数组）。
