# Custom Skill Development Guidelines

为了确保项目中的自定义技能（Skills）具有一致性、可维护性和易用性，请遵循以下开发规范。

## 1. 依赖管理 (Dependency Management)

所有 Python 脚本必须使用 `uv` 的内联元数据（Inline Metadata，遵循 PEP 723）来管理依赖。这使得脚本可以作为独立文件分发和运行，而无需手动管理虚拟环境。

### 示例
```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests",
#     "beautifulsoup4",
#     "rich",
# ]
# ///
```

## 2. 运行脚本 (Running Scripts)

推荐使用 `uv run` 来执行脚本：
```bash
uv run scripts/your_script.py
```

## 3. 目录结构 (Directory Structure)

每个技能集应组织在一个独立的目录下，包含以下内容：
- `scripts/`: 存放 Python 脚本。
- `SKILL.md`: 技能的元数据描述文件（用于网站展示）。
- `data/` (可选): 存放静态数据。
- `references/` (可选): 存放参考文档。

## 4. 统一配置加载 (Unified Configuration)

为了处理不同环境（环境变量、注册表、`secrets.json`）下的配置加载，请使用以下标准模式：

### 获取环境变量
使用 `get_env_flexible` 函数，它会按以下顺序查找配置：
1. 进程环境变量
2. Windows 注册表 (仅限 Windows)
3. 根目录或脚本同级的 `secrets.json`

### 数据库配置
使用统一的 `get_db_config()` 函数：
```python
def get_db_config():
    """从环境变量、注册表或 secrets.json 获取数据库配置"""
    return {
        "user": get_env_flexible("DB_USER", "root"),
        "password": get_env_flexible("DB_PASSWORD", ""),
        "host": get_env_flexible("DB_HOST", "127.0.0.1"),
        "port": get_env_flexible("DB_PORT", "5432"),
        "dbname": get_env_flexible("DB_NAME", "your_db")
    }
```

## 5. 日志与输出 (Logging & Output)

推荐使用 `rich` 库来提供美观的控制台输出，特别是在需要进度条或格式化表格时。

## 6. 代码规范 (Coding Standards)

- **异步优先**: 对于 I/O 密集型任务（如 API 调用、数据库操作），优先使用 `asyncio`。
- **类型提示**: 尽可能为函数参数和返回值提供类型提示。
- **错误处理**: 使用清晰的 try-except 块，并提供有意义的错误信息。

## 7. 技能元数据 (SKILL.md)

每个技能目录下必须包含 `SKILL.md`，格式如下：
```markdown
# 技能名称

- **Version**: 1.0.0
- **Author**: Your Name
- **Description**: 技能的详细描述。

## Usage
如何使用该技能的说明。
```
