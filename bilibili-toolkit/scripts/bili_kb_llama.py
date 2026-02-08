"""
B站视频知识库构建工具
功能: 将数据库中的视频文稿转换为向量索引,支持语义搜索
"""

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "llama-index",
#     "llama-index-vector-stores-postgres",
#     "llama-index-llms-openai-like",
#     "llama-index-embeddings-openai",
#     "python-dotenv",
#     "SQLAlchemy",
#     "psycopg[binary]",
#     "httpx",
#     "nest_asyncio",
#     "rich",
# ]
# ///

import os
import sys
import asyncio
import httpx
import argparse
from datetime import datetime, timedelta
from typing import List, Optional, Set
from dotenv import load_dotenv
import nest_asyncio
import json
from sqlalchemy import bindparam, create_engine, text
from sqlalchemy.engine import URL
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel

console = Console()

# 修复 Windows 控制台编码问题
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

nest_asyncio.apply()
from llama_index.core import Document, StorageContext, VectorStoreIndex, Settings, load_index_from_storage
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.llms.openai_like import OpenAILike

load_dotenv()

# ================= 自定义 OpenAI 兼容 Embedding 类 =================
class SiliconFlowEmbedding(BaseEmbedding):
    """适配硅基流动等 OpenAI 兼容接口的通用 Embedding 类"""
    model_name: str
    api_key: str
    api_base: str

    def __init__(self, model_name: str, api_key: str, api_base: str, **kwargs):
        super().__init__(model_name=model_name, api_key=api_key, api_base=api_base, **kwargs)

    @classmethod
    def class_name(cls) -> str:
        return "SiliconFlowEmbedding"

    def _get_query_embedding(self, query: str) -> List[float]:
        return asyncio.run(self._aget_query_embedding(query))

    def _get_text_embedding(self, text: str) -> List[float]:
        return asyncio.run(self._aget_text_embedding(text))

    def _get_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        return asyncio.run(self._aget_text_embeddings(texts))

    async def _aget_query_embedding(self, query: str) -> List[float]:
        embeddings = await self._aget_text_embeddings([query])
        return embeddings[0]

    async def _aget_text_embedding(self, text: str) -> List[float]:
        embeddings = await self._aget_text_embeddings([text])
        return embeddings[0]

    async def _aget_text_embeddings(self, texts: List[str]) -> List[List[float]]:
        # 手动限制每批大小,防止 API 报 413 错误
        max_batch = 4
        all_embeddings = []

        url = f"{self.api_base}/embeddings"
        headers = {"Authorization": f"Bearer {self.api_key}"}

        async with httpx.AsyncClient() as client:
            for i in range(0, len(texts), max_batch):
                batch_text = texts[i:i+max_batch]
                payload = {"model": self.model_name, "input": batch_text}

                response = await client.post(url, json=payload, headers=headers, timeout=60)
                if response.status_code == 413:
                    print(f"⚠️ 批次仍过大 ({len(batch_text)}),尝试单条发送...")
                    # 进一步拆分到 1 条
                    for single_text in batch_text:
                        r = await client.post(url, json={"model": self.model_name, "input": [single_text]}, headers=headers)
                        r.raise_for_status()
                        all_embeddings.append(r.json()["data"][0]["embedding"])
                else:
                    response.raise_for_status()
                    data = response.json()
                    all_embeddings.extend([item["embedding"] for item in data["data"]])

        return all_embeddings

# ================= 配置区 =================
# ================= 环境变量增强加载 =================
def load_secrets():
    """递归向上查找 secrets.json"""
    import json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while True:
        secrets_path = os.path.join(current_dir, "secrets.json")
        if os.path.exists(secrets_path):
            try:
                with open(secrets_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:  # 到达根目录
            return {}
        current_dir = parent_dir

SECRETS = load_secrets()

def get_env_flexible(key_name, default=None):
    """优先从 os.getenv 获取，如果为空则 Windows 注册表读取，最后 secrets.json"""
    val = os.getenv(key_name)
    if val: return val
    
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
                val, _ = winreg.QueryValueEx(key, key_name)
                if val: return val
        except Exception:
            pass
            
    if SECRETS and key_name in SECRETS:
        return SECRETS[key_name]
    return default

SILICONFLOW_API_KEY = get_env_flexible("SILICONFLOW_API_KEY")
SILICONFLOW_BASE_URL = "https://api.siliconflow.cn/v1"
EMBED_MODEL_NAME = "BAAI/bge-m3"

LONGMAO_API_KEY = get_env_flexible("LONGMAO_API_KEY")
LONGMAO_BASE_URL = get_env_flexible("LONGMAO_BASE_URL")
LLM_MODEL_NAME = get_env_flexible("LONGMAO_MODEL", "LongCat-Flash-Chat")

# 设置全局 LlamaIndex 配置
Settings.embed_model = SiliconFlowEmbedding(
    model_name=EMBED_MODEL_NAME,
    api_key=SILICONFLOW_API_KEY,
    api_base=SILICONFLOW_BASE_URL,
)
Settings.embed_batch_size = 10  # 提高批处理大小以提升性能
Settings.llm = OpenAILike(
    model=LLM_MODEL_NAME,
    api_key=LONGMAO_API_KEY,
    api_base=LONGMAO_BASE_URL,
    is_chat_model=True,
)
# 配置文本分块器：将长文本切分为适当大小的块
Settings.node_parser = SentenceSplitter(
    chunk_size=512,  # 每块512字符
    chunk_overlap=50,  # 块之间50字符重叠，保持上下文连贯性
    paragraph_separator="\n\n",
)

# ================= 数据库操作函数 =================

_ENGINE = None

def get_db_config():
    """从环境变量或 secrets.json 获取数据库配置"""
    return {
        "dbname": get_env_flexible("DB_NAME", "media_knowledge_base"),
        "user": get_env_flexible("DB_USER", "root"),
        "password": get_env_flexible("DB_PASSWORD", "15671040800q"),
        "host": get_env_flexible("DB_HOST", "127.0.0.1"),
        "port": get_env_flexible("DB_PORT", "5433")
    }

def get_engine():
    global _ENGINE
    if _ENGINE is not None:
        return _ENGINE

    config = get_db_config()
    port = config.get("port")
    try:
        port = int(port) if port is not None else None
    except (TypeError, ValueError):
        port = None

    _ENGINE = create_engine(
        URL.create(
            "postgresql+psycopg",
            username=config.get("user"),
            password=config.get("password"),
            host=config.get("host"),
            port=port,
            database=config.get("dbname"),
        ),
        pool_pre_ping=True,
    )
    return _ENGINE

def get_indexed_bvids() -> Set[str]:
    """获取已索引的 BVID 集合"""
    try:
        with get_engine().connect() as conn:
            rows = conn.execute(
                text(
                    "SELECT DISTINCT metadata_->>'bvid' FROM data_llama_collection WHERE metadata_->>'bvid' IS NOT NULL"
                )
            ).fetchall()
        return {row[0] for row in rows if row[0]}
    except Exception as e:
        print(f"⚠️ 获取已索引列表失败: {e}")
        return set()

def get_videos_from_db(up_mid: Optional[int] = None, days: Optional[int] = None,
                      bvids: Optional[List[str]] = None) -> List[tuple]:
    """
    从数据库获取视频列表

    Args:
        up_mid: UP主ID,只获取该UP主的视频
        days: 天数,只获取最近N天的视频
        bvids: BVID列表,只获取指定的视频

    Returns:
        List of (bvid, title, content_text) tuples
    """
    # 构建查询条件
    conditions = ["content_text IS NOT NULL"]
    params: dict = {}

    if up_mid:
        conditions.append("up_mid = :up_mid")
        params["up_mid"] = up_mid

    if days:
        date_threshold = datetime.now() - timedelta(days=days)
        conditions.append("pub_time >= :date_threshold")
        params["date_threshold"] = date_threshold

    if bvids:
        conditions.append("bvid IN :bvids")
        params["bvids"] = bvids

    sql = f"""
        SELECT bvid, title, content_text, up_mid
        FROM bili_video_contents
        WHERE {' AND '.join(conditions)}
        ORDER BY pub_time DESC
    """

    stmt = text(sql)
    if bvids:
        stmt = stmt.bindparams(bindparam("bvids", expanding=True))

    with get_engine().connect() as conn:
        return conn.execute(stmt, params).fetchall()

def get_index_stats() -> dict:
    """获取索引统计信息"""
    stats = {
        "total_videos": 0,
        "indexed_videos": 0,
        "total_docs": 0,
        "index_size_mb": 0,
    }

    try:
        with get_engine().connect() as conn:
            # 获取数据库中有文稿的视频总数
            stats["total_videos"] = conn.execute(
                text("SELECT COUNT(*) FROM bili_video_contents WHERE content_text IS NOT NULL")
            ).scalar_one()

            # 获取已索引的视频数（通过 metadata 中的 bvid 统计）
            stats["indexed_videos"] = conn.execute(
                text(
                    "SELECT COUNT(DISTINCT metadata_->>'bvid') FROM data_llama_collection WHERE metadata_->>'bvid' IS NOT NULL"
                )
            ).scalar_one()

            # 获取总文档数(可能一个视频被拆分)
            stats["total_docs"] = conn.execute(text("SELECT COUNT(*) FROM data_llama_collection")).scalar_one()

            # 获取表大小(MB)
            size_str = conn.execute(
                text("SELECT pg_size_pretty(pg_total_relation_size('data_llama_collection')) as size")
            ).scalar_one_or_none()
        # 解析 size 字符串 (如 "1234 MB")
        try:
            if size_str:
                stats["index_size_mb"] = float(size_str.split()[0])
        except:
            pass
    except Exception as e:
        print(f"⚠️ 获取统计信息失败: {e}")

    return stats

def clear_index():
    """清空向量索引"""
    try:
        with get_engine().begin() as conn:
            result = conn.execute(text("DELETE FROM data_llama_collection"))
            deleted = result.rowcount or 0
        print(f"✅ 已清空索引,删除 {deleted} 条记录")
        return True
    except Exception as e:
        print(f"❌ 清空索引失败: {e}")
        return False

def delete_from_index(bvids: List[str]):
    """从索引中删除指定视频"""
    try:
        stmt = text("DELETE FROM data_llama_collection WHERE metadata_->>'bvid' IN :bvids").bindparams(
            bindparam("bvids", expanding=True)
        )
        with get_engine().begin() as conn:
            result = conn.execute(stmt, {"bvids": bvids})
            deleted = result.rowcount or 0
        print(f"✅ 已从索引中删除 {deleted} 条记录")
        return True
    except Exception as e:
        print(f"❌ 删除索引失败: {e}")
        return False

# ================= 索引构建函数 =================

async def build_index(up_mid: Optional[int] = None, days: Optional[int] = None,
                    bvids: Optional[List[str]] = None, force_rebuild: bool = False):
    """构建向量索引
    """
    config = get_db_config()

    # 1. 获取要索引的视频列表
    print("📥 正在从数据库读取视频列表...")
    rows = get_videos_from_db(up_mid, days, bvids)

    if not rows:
        print("❌ 没有找到符合条件的视频")
        return

    print(f"📊 找到 {len(rows)} 个视频")

    # 2. 获取已索引的 BVID (增量更新)
    indexed_bvids = set()
    if not force_rebuild:
        indexed_bvids = get_indexed_bvids()
        print(f"✅ 已存在 {len(indexed_bvids)} 个视频的索引")

    # 3. 过滤出需要索引的视频
    videos_to_index = []
    skipped = 0

    for bvid, title, content, up_mid in rows:
        if not force_rebuild and bvid in indexed_bvids:
            skipped += 1
        else:
            videos_to_index.append((bvid, title, content, up_mid))

    if not videos_to_index:
        print(f"✅ 所有视频已索引,跳过 {skipped} 个")
        return

    print(f"🔧 准备索引 {len(videos_to_index)} 个新视频 (跳过 {skipped} 个已存在)")

    # 4. 初始化 PGVectorStore
    vector_store = PGVectorStore.from_params(
        host=config["host"],
        port=config["port"],
        database=config["dbname"],
        user=config["user"],
        password=config["password"],
        table_name="llama_collection",
        embed_dim=1024,
        perform_setup=False,
        hybrid_search=True,
    )

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # 5. 批量构建文档
    console.print("📝 准备文档...")
    documents = []
    for bvid, title, content, up_mid in videos_to_index:
        doc = Document(
            text=content,
            id_=bvid,
            metadata={
                "bvid": bvid,
                "title": title,
                "up_mid": up_mid or 0,
                "source": "bilibili"
            }
        )
        documents.append(doc)

    # 6. 批量索引（自动分块）
    success_count = 0
    fail_count = 0
    start_time = datetime.now()

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]正在构建索引...", total=len(documents))
            
            index = VectorStoreIndex.from_documents(
                documents, 
                storage_context=storage_context, 
                show_progress=False
            )
            progress.update(task, advance=len(documents))
            
        success_count = len(documents)
        console.print("[bold green]✅ 批量索引完成[/bold green]")
    except Exception as e:
        print(f"❌ 批量索引失败: {e}")
        print("⚠️ 尝试逐个索引...")
        # 如果批量失败，降级为逐个索引
        for i, doc in enumerate(documents, 1):
            try:
                title = doc.metadata.get('title', 'Unknown')
                print(f"[{i}/{len(documents)}] 索引: {title}")
                temp_index = VectorStoreIndex.from_documents(
                    [doc],
                    storage_context=storage_context,
                    show_progress=False
                )
                success_count += 1
            except Exception as e:
                print(f"❌ 索引失败 {doc.id_}: {e}")
                fail_count += 1

    # 7. 显示统计信息
    elapsed = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 60)
    print("📈 索引构建完成!")
    print(f"  ✅ 成功: {success_count}")
    print(f"  ❌ 失败: {fail_count}")
    print(f"  ⏭️  跳过: {skipped}")
    print(f"  ⏱️  耗时: {elapsed:.1f}秒")
    if success_count > 0:
        print(f"  📊 平均: {elapsed/success_count:.1f}秒/视频")
    print("=" * 60)

    # 8. 显示更新后的索引状态
    print("\n📊 当前索引状态:")
    show_stats()

def show_stats():
    """显示索引统计信息"""
    stats = get_index_stats()

    print(f"  📹 数据库视频总数: {stats['total_videos']}")
    print(f"  ✅ 已索引视频数: {stats['indexed_videos']}")
    print(f"  📄 总文档数: {stats['total_docs']}")
    if stats['index_size_mb'] > 0:
        print(f"  💾 索引大小: {stats['index_size_mb']:.1f} MB")

    # 计算覆盖率
    if stats['total_videos'] > 0:
        coverage = (stats['indexed_videos'] / stats['total_videos']) * 100
        print(f"  📊 覆盖率: {coverage:.1f}%")

def validate_index():
    """验证索引是否正常工作"""
    try:
        print("\n🔍 验证索引...")
        config = get_db_config()

        # 初始化向量存储
        vector_store = PGVectorStore.from_params(
            host=config["host"],
            port=config["port"],
            database=config["dbname"],
            user=config["user"],
            password=config["password"],
            table_name="data_llama_collection",
            embed_dim=1024,
        )

        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

        # 测试查询
        query_engine = index.as_query_engine(similarity_top_k=1)
        response = query_engine.query("测试")
        print(f"✅ 索引验证成功")

        return True
    except Exception as e:
        print(f"❌ 索引验证失败: {e}")
        return False

# ================= 命令行接口 =================

def main():
    parser = argparse.ArgumentParser(
        description="B站视频知识库构建工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 全量构建(增量模式)
  %(prog)s

  # 查看索引状态
  %(prog)s --stats

  # 强制重建所有索引
  %(prog)s --rebuild

  # 只索引指定UP主的视频
  %(prog)s --up 3546830417693175

  # 只索引最近30天的视频
  %(prog)s --days 30

  # 只索引指定的视频
  %(prog)s --bvids BV1xx411c7mD BV1yy411c7mE

  # 组合条件
  %(prog)s --up 3546830417693175 --days 7

  # 删除指定视频的索引
  %(prog)s --delete BV1xx411c7mD
        """
    )

    parser.add_argument("--stats", action="store_true", help="显示索引统计信息")
    parser.add_argument("--rebuild", action="store_true", help="清空并重建索引")
    parser.add_argument("--up", type=int, metavar="UID", help="只索引指定UP主的视频")
    parser.add_argument("--days", type=int, metavar="N", help="只索引最近N天的视频")
    parser.add_argument("--bvids", nargs="+", metavar="BVID", help="只索引指定的视频列表")
    parser.add_argument("--delete", nargs="+", metavar="BVID", help="从索引中删除指定视频")
    parser.add_argument("--validate", action="store_true", help="验证索引是否正常")
    parser.add_argument("--force", action="store_true", help="强制重建(忽略已存在的索引)")

    args = parser.parse_args()

    # 显示帮助信息
    if len(sys.argv) == 1:
        parser.print_help()
        return

    # 处理删除操作
    if args.delete:
        print(f"🗑️  删除索引: {', '.join(args.delete)}")
        delete_from_index(args.delete)
        return

    # 处理统计信息
    if args.stats:
        print("📊 索引统计信息:")
        show_stats()
        return

    # 处理验证
    if args.validate:
        show_stats()
        validate_index()
        return

    # 处理重建
    if args.rebuild:
        print("🔄 清空并重建索引...")
        if clear_index():
            asyncio.run(build_index(force_rebuild=True))
        return

    # 构建索引(增量或指定范围)
    asyncio.run(build_index(
        up_mid=args.up,
        days=args.days,
        bvids=args.bvids,
        force_rebuild=args.force
    ))

if __name__ == "__main__":
    main()
