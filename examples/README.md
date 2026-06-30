# AICC 示例程序

本目录包含可以用 AICC 编译的示例 C 程序。

## ✅ 当前可编译的示例

### hello.c - 简单返回
最简单的程序，返回值 42。
```bash
aicc examples/hello.c -o hello
./hello; echo $?  # 输出: 42
```

### fib.c - 递归斐波那契
演示递归函数调用。
```bash
aicc examples/fib.c -o fib
./fib; echo $?  # 输出: 55 (第10个斐波那契数)
```

### arithmetic.c - 复杂表达式和控制流
演示算术运算、条件判断和控制流。
```bash
aicc examples/arithmetic.c -o arithmetic
./arithmetic; echo $?  # 输出: 1 (true)
```

## ❌ 暂不支持的特性

- `#include` - 预处理器指令
- `printf()` - 标准库函数
- 字符串字面量 `"hello"`
- `char` 类型

## 📝 编写兼容程序的提示

1. **只使用 int 类型**
2. **通过返回值传递结果**
3. **不使用预处理器指令**
4. **不调用标准库函数**

## 🎯 正确的写法

```c
// ✅ 正确 - 使用 int 和返回值
int main() {
    int x = 10;
    int y = 20;
    return x + y;  // 返回 30
}

// ❌ 错误 - 使用了不支持的特性
#include <stdio.h>
int main() {
    printf("Hello\n");
    return 0;
}
```

## 🔮 即将支持

我们正在开发中的功能：
- 字符串字面量
- `char` 类型
- 简化版 `putchar()`
- 简化版 `printf()`

敬请期待下一个版本！
