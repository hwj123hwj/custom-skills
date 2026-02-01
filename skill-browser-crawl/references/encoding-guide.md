# 编码问题解决指南

## 常见编码问题

### 1. Windows 终端编码错误

**症状**：
```
UnicodeEncodeError: 'gbk' codec can't encode character
```

**原因**：
- Windows CMD/PowerShell 默认使用 GBK 编码
- Python 输出包含 emoji (ℹ️ ✅ ❌) 或中文字符时触发错误

**解决方案**：

所有脚本已包含以下修复代码：

```python
import os
import sys

# 设置 Python IO 编码为 UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Windows 平台额外处理
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
```

**手动执行时的替代方案**：

```powershell
# PowerShell
$env:PYTHONIOENCODING='utf-8'; python script.py

# CMD
set PYTHONIOENCODING=utf-8 && python script.py
```

### 2. 文件写入编码问题

**症状**：
```
UnicodeEncodeError when writing to file
```

**解决方案**：

```python
# 总是显式指定 UTF-8 编码
with open('output.md', 'w', encoding='utf-8') as f:
    f.write(content)

# 读取时也要指定
with open('input.md', 'r', encoding='utf-8') as f:
    content = f.read()
```

### 3. 平台默认编码差异

**检测当前编码**：

```python
import locale
import sys

print(f"平台: {sys.platform}")
print(f"默认编码: {locale.getpreferredencoding()}")
print(f"文件系统编码: {sys.getfilesystemencoding()}")
```

**典型输出**：
- Windows: `cp936` (GBK)
- Linux/Mac: `UTF-8`

### 4. crawl4ai 特定问题

crawl4ai 使用 `rich` 库输出进度信息，包含 emoji 字符。在 Windows GBK 环境下会报错。

**已修复**：
所有脚本在导入 crawl4ai 之前设置了 UTF-8 编码。

**如果仍然遇到问题**：

```python
# 在脚本最开头添加
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
```

使用 `errors='replace'` 可以在无法编码时用替换字符代替，避免程序崩溃。

### 5. JSON 文件编码

```python
import json

# 写入 JSON（保持中文可读）
with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 读取 JSON
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
```

## 最佳实践

1. **统一使用 UTF-8**
   - 所有文件读写指定 `encoding='utf-8'`
   - 所有数据库连接指定 UTF-8
   - 所有网络请求/响应检查编码

2. **Windows 额外处理**
   ```python
   os.environ['PYTHONIOENCODING'] = 'utf-8'
   if sys.platform == 'win32':
       sys.stdout.reconfigure(encoding='utf-8')
   ```

3. **异常处理**
   ```python
   try:
       with open('file.txt', 'r', encoding='utf-8') as f:
           content = f.read()
   except UnicodeDecodeError:
       # 尝试其他编码
       with open('file.txt', 'r', encoding='gbk') as f:
           content = f.read()
   ```

4. **Python shebang 声明**
   ```python
   #!/usr/bin/env python3
   # -*- coding: utf-8 -*-
   ```

## 相关资源

- [Python Unicode HOWTO](https://docs.python.org/3/howto/unicode.html)
- [UnicodeEncodeError 常见原因](https://stackoverflow.com/questions/9942594/unicodeencodeerror-ascii-codec-cant-encode-character)
