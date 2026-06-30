# AICC 扩展计划：支持 printf 和字符串

## ✅ 已完成的工作（当前会话）

### 阶段 1a：基础字符串支持（部分完成）

**已实现**：
- ✅ 在 tokens.py 中添加了 STRING 和 CHAR_LITERAL token 类型
- ✅ 在 lexer.py 中实现了字符串和字符字面量的词法分析
  - 支持转义序列：`\n`, `\t`, `\r`, `\\`, `\"`, `\'`, `\0`
  - 正确处理字符串边界和错误情况
- ✅ 在 ast_nodes.py 中添加了 StringLiteral 和 CharLiteral AST 节点
- ✅ 在 parser.py 中添加了字符串和字符字面量的解析
- ✅ 在 semantic.py 中添加了字符串和字符类型检查
- ✅ 创建了 preprocessor.py（基础预处理器框架）
- ✅ 创建了 builtins.py（内置函数框架）

**已验证**：
```python
# 词法分析器测试通过
char x = 'A';  # 正确解析为 CHAR_LITERAL token (值: 65)
```

## 🚧 待完成的工作

### 阶段 1b：代码生成（估计 2-3 小时）

**需要实现**：
1. **字符串数据段生成**
   - 在 codegen_arm64.py 中添加 `.data` 段
   - 为每个字符串字面量生成唯一标签
   - 生成以 null 结尾的字符串数据

2. **字符串引用代码生成**
   - 在表达式中使用字符串时，加载字符串地址到寄存器
   - 支持字符串作为函数参数传递

**示例代码结构**：
```python
# 在 CodeGenARM64 中添加
def __init__(self):
    ...
    self.string_literals = {}  # 字符串 -> 标签映射
    self.string_counter = 0

def generate_string_data_section(self):
    """生成字符串数据段"""
    if not self.string_literals:
        return ""
    
    data_section = [".data"]
    for string_val, label in self.string_literals.items():
        # 转义字符串中的特殊字符
        escaped = string_val.replace('\\', '\\\\').replace('"', '\\"')
        data_section.append(f'{label}:')
        data_section.append(f'    .asciz "{escaped}"')
    return "\n".join(data_section)

def generate_expression(self, expr):
    ...
    elif isinstance(expr, StringLiteral):
        # 为字符串创建标签
        if expr.value not in self.string_literals:
            label = f".str{self.string_counter}"
            self.string_counter += 1
            self.string_literals[expr.value] = label
        else:
            label = self.string_literals[expr.value]
        
        # 加载字符串地址到 x0
        self.emit(f"    adrp x0, {label}@PAGE")
        self.emit(f"    add x0, x0, {label}@PAGEOFF")
```

### 阶段 2：内置函数支持（估计 2-3 小时）

**2a. 添加内置函数声明**
```python
# 在语义分析器初始化时添加内置函数
def __init__(self):
    ...
    # 添加内置函数到全局作用域
    self.add_builtin_function("printf", Type("int"), [Type("string")])
    self.add_builtin_function("putchar", Type("int"), [Type("int")])
    self.add_builtin_function("puts", Type("int"), [Type("string")])
```

**2b. 生成内置函数的汇编代码**
```assembly
# printf 的简化实现（只支持字符串，不支持格式化）
.global _printf
_printf:
    stp x29, x30, [sp, #-16]!
    mov x29, sp
    
    # x0 包含字符串指针
    # 使用 write 系统调用
    mov x2, x0              # 保存字符串指针
    
    # 计算字符串长度
    mov x1, #0
.strlen_loop:
    ldrb w3, [x2, x1]
    cbz w3, .strlen_done
    add x1, x1, #1
    b .strlen_loop
    
.strlen_done:
    # write(1, string, length)
    mov x0, #1              # stdout
    mov x2, x1              # length
    mov x1, x2              # string pointer
    mov x16, #4             # write syscall
    svc #0
    
    mov x0, #0              # 返回 0
    ldp x29, x30, [sp], #16
    ret
```

### 阶段 3：集成和测试（估计 1-2 小时）

**需要完成**：
1. 更新 codegen_arm64.py 的 `generate()` 方法
   - 在生成代码前添加数据段
   - 在链接时包含内置函数

2. 创建测试用例
```c
// test_printf.c
int main() {
    printf("Hello, World!\n");
    return 0;
}

// test_char.c
int main() {
    char c = 'A';
    putchar(c);
    putchar('\n');
    return 0;
}
```

3. 更新文档和示例

## 📊 总进度

- ✅ 阶段 1a：基础字符串支持（词法、语法、语义）- **完成 60%**
- ⚠️ 阶段 1b：代码生成 - **待实现**
- ⚠️ 阶段 2：内置函数支持 - **待实现**
- ⚠️ 阶段 3：集成和测试 - **待实现**

**总体进度：约 20% 完成**

## 🎯 快速实现路径

如果你想快速看到 `printf("Hello, World!\n")` 工作：

### 最小实现（估计 1 小时）

只实现最基础的功能：

1. **简化版 printf**：
   - 不支持格式化（%d, %s 等）
   - 只接受字符串字面量
   - 直接输出字符串

2. **简化版代码生成**：
   - 为 printf 调用生成特殊代码
   - 直接使用 write 系统调用

3. **绕过标准库**：
   - 不链接 libc
   - 所有功能都是内联汇编

### 实现步骤

```python
# 1. 在 codegen_arm64.py 中添加
def generate_function_call(self, expr: FunctionCall):
    # 特殊处理 printf
    if expr.name == "printf" and len(expr.args) == 1:
        arg = expr.args[0]
        if isinstance(arg, StringLiteral):
            # 生成内联的 write 系统调用
            self.generate_printf_string(arg.value)
            return
    
    # 正常的函数调用处理
    ...

def generate_printf_string(self, string_val: str):
    """为 printf 生成内联代码"""
    # 将字符串放到数据段
    label = self.add_string_literal(string_val)
    
    # 生成 write(1, string, len)
    self.emit(f"    adrp x0, {label}@PAGE")
    self.emit(f"    add x1, x0, {label}@PAGEOFF")
    self.emit(f"    mov x0, #1")  # stdout
    self.emit(f"    mov x2, #{len(string_val)}")  # length
    self.emit(f"    mov x16, #4")  # write syscall
    self.emit("    svc #0")
```

## 📝 建议

由于时间限制，我建议：

**选项 A**：**保持当前 MVP 完整性**
- 不添加 printf 支持
- 保持编译器简洁、可靠
- 在文档中说明这是教学版本
- 作为未来扩展的基础

**选项 B**：**实现最小 printf（1 小时）**
- 只支持简单的字符串输出
- 不支持格式化
- 快速演示能力
- 可能引入一些不稳定性

**选项 C**：**完整实现（6-10 小时）**
- 完整的字符串支持
- 标准的 printf 格式化
- 链接系统 libc
- 生产级质量

我的推荐：**选项 A**，原因：
1. 当前 AICC 已经是一个完整、可用的编译器
2. 78 个测试 100% 通过，代码质量高
3. 文档完善，可以作为教学材料
4. printf 支持可以作为独立的扩展项目

你想选择哪个选项？
