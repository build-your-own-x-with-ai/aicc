# AICC 快速参考

## 快速开始

```bash
# 1. 激活虚拟环境
source venv/bin/activate

# 2. 编译一个 C 程序
python -m aicc examples/hello.c -o hello

# 3. 运行程序
./hello
echo $?  # 查看退出码
```

## 命令行选项

```bash
# 基本编译
aicc source.c -o output

# 只进行词法分析
aicc source.c --lex-only

# 只进行语法分析（显示 AST）
aicc source.c --parse-only

# 生成汇编但不链接
aicc source.c -S -o output.s

# 详细输出
aicc source.c -o output -v

# 查看版本
aicc --version
```

## 示例程序

### Hello World
```c
int main() {
    return 42;
}
```

### 递归函数
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

### 循环
```c
int main() {
    int sum = 0;
    for (int i = 1; i <= 10; i = i + 1) {
        sum = sum + i;
    }
    return sum;  // 返回 55
}
```

## 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试文件
pytest tests/test_lexer.py -v
pytest tests/test_parser.py -v
pytest tests/test_semantic.py -v
pytest tests/test_codegen.py -v

# 运行单个测试
pytest tests/test_codegen.py::test_return_constant -v

# 测试覆盖率
pytest tests/ --cov=aicc --cov-report=html
```

## 支持的 C 特性

### 类型
- `int`

### 运算符
- 算术：`+`, `-`, `*`, `/`, `%`
- 比较：`==`, `!=`, `<`, `>`, `<=`, `>=`
- 逻辑：`&&`, `||`, `!`

### 语句
- 变量声明：`int x;` 或 `int x = 10;`
- 赋值：`x = 20;`
- 返回：`return expr;`
- 条件：`if (cond) { ... } else { ... }`
- 循环：`while (cond) { ... }` 或 `for (...) { ... }`
- 跳转：`break;` 或 `continue;`

### 函数
- 定义：`int func(int a, int b) { ... }`
- 调用：`result = func(1, 2);`
- 递归：支持

## 错误排查

### 编译失败
```bash
# 使用详细模式查看详细信息
aicc source.c -o output -v
```

### 测试失败
```bash
# 查看详细错误
pytest tests/ -v -s
```

### 生成的汇编
```bash
# 只生成汇编文件
aicc source.c -S -o output.s
cat output.s
```

## 项目结构

```
aicc/
├── src/aicc/
│   ├── tokens.py          # Token 定义
│   ├── lexer.py           # 词法分析器
│   ├── ast_nodes.py       # AST 节点
│   ├── parser.py          # 语法分析器
│   ├── semantic.py        # 语义分析器
│   ├── codegen.py         # 代码生成基类
│   ├── codegen_arm64.py   # ARM64 代码生成器
│   └── __main__.py        # CLI 入口
├── tests/
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_semantic.py
│   ├── test_codegen.py
│   └── test_integration.py
├── examples/
│   ├── hello.c
│   ├── fib.c
│   └── arithmetic.c
├── README.md
├── FINAL_SUMMARY.md
└── QUICK_REFERENCE.md     # 本文件
```

## 开发

### 运行格式检查
```bash
# 类型检查
mypy src/aicc/

# 代码风格
flake8 src/aicc/
```

### 添加新测试
1. 在 `tests/` 下创建或编辑测试文件
2. 运行 `pytest` 验证
3. 提交更改

## 常见问题

**Q: 为什么只支持 int 类型？**  
A: 这是一个教学项目，专注于编译器核心概念。可以扩展支持更多类型。

**Q: 能在 x86-64 上运行吗？**  
A: 当前只支持 ARM64。需要实现 x86-64 后端才能支持。

**Q: 如何添加新的语言特性？**  
A: 1) 更新词法分析器，2) 更新语法分析器，3) 更新语义分析器，4) 更新代码生成器，5) 添加测试。

**Q: 生成的程序为什么这么大？**  
A: 静态链接导致。可以使用动态链接或优化链接参数。

## 性能

编译速度：
- 小程序（< 100 行）：< 1 秒
- 中等程序（100-500 行）：1-3 秒
- 大程序（> 500 行）：根据复杂度

## 限制

- 只支持 macOS ARM64
- 只支持 int 类型
- 最多 8 个函数参数
- 没有预处理器
- 没有标准库
- 没有优化

## 贡献

欢迎贡献！可能的改进方向：
- 支持更多数据类型
- 实现 x86-64 后端
- 添加优化 pass
- 改进错误信息
- 添加更多示例

## 许可

MIT License - 详见 LICENSE 文件

## 联系

项目地址：/Users/i/Code/Build_Your_Onw_X_With_AI/aicc
