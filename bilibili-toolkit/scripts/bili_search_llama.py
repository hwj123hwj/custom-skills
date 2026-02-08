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
import nest_asyncio
import logging
import io
from typing import List, Optional, Any
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

# 1. 彻底屏蔽噪音：禁止库日志和警告
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3" # 屏蔽 TensorFlow 警告
logging.getLogger("llama_index").setLevel(logging.ERROR)

console = Console()

# 2. 基础配置
nest_asyncio.apply()
logging.getLogger("llama_index").setLevel(logging.ERROR)

from llama_index.core import StorageContext, VectorStoreIndex, Settings
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core.postprocessor.types import BaseNodePostprocessor
from llama_index.core.schema import NodeWithScore, QueryBundle
from llama_index.core.vector_stores.types import VectorStoreQueryMode
from llama_index.core.vector_stores import MetadataFilters, ExactMatchFilter
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.llms.openai_like import OpenAILike

load_dotenv()

# ================= 自定义 OpenAI 兼容 Embedding 类 =================
class SiliconFlowEmbedding(BaseEmbedding):
    api_key: str = ""
    api_base: str = ""

    def __init__(
        self, 
        model_name: str = "BAAI/bge-m3", 
        api_key: str = "", 
        api_base: str = "", 
        **kwargs
    ):
        super().__init__(
            model_name=model_name, 
            api_key=api_key, 
            api_base=api_base, 
            **kwargs
        )

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
        # 手动限制每批大小，防止 API 报 413 错误
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
                    # 进一步拆分
                    for single_text in batch_text:
                        r = await client.post(url, json={"model": self.model_name, "input": [single_text]}, headers=headers)
                        r.raise_for_status()
                        all_embeddings.append(r.json()["data"][0]["embedding"])
                else:
                    response.raise_for_status()
                    data = response.json()
                    all_embeddings.extend([item["embedding"] for item in data["data"]])
                    
        return all_embeddings

# ================= 自定义 SiliconFlow Reranker 类 =================
class SiliconFlowRerank(BaseNodePostprocessor):
    """使用硅基流动 API 进逻辑重排"""
    model: str
    api_key: str
    top_n: int = 3

    def __init__(self, model: str, api_key: str, top_n: int = 3):
        super().__init__(model=model, api_key=api_key, top_n=top_n)

    @classmethod
    def class_name(cls) -> str:
        return "SiliconFlowRerank"

    def _postprocess_nodes(
        self,
        nodes: List[NodeWithScore],
        query_bundle: Optional[QueryBundle] = None,
    ) -> List[NodeWithScore]:
        if query_bundle is None or not nodes:
            return nodes

        url = "https://api.siliconflow.cn/v1/rerank"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        texts = [node.node.get_content() for node in nodes]
        payload = {
            "model": self.model,
            "query": query_bundle.query_str,
            "documents": texts,
            "top_n": self.top_n
        }

        with httpx.Client() as client:
            response = client.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            results = response.json()

        new_nodes = []
        # SiliconFlow 返回的 results['results'] 包含了 index 和 relevance_score
        for res in results.get("results", []):
            idx = res["index"]
            original_node = nodes[idx]
            original_node.score = res["relevance_score"] # 更新为重排后的分数
            new_nodes.append(original_node)

        return new_nodes

# ================= 配置区 =================
# ================= 配置加载 =================
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

# ================= 环境变量增强加载 =================
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

# AI 配置从环境变量加载，secrets.json 作为备用
SILICONFLOW_API_KEY = get_env_flexible("SILICONFLOW_API_KEY")
SILICONFLOW_BASE_URL = "https://api.siliconflow.cn/v1"
EMBED_MODEL_NAME = "BAAI/bge-m3"
RERANK_MODEL_NAME = "BAAI/bge-reranker-v2-m3"

LONGMAO_API_KEY = get_env_flexible("LONGMAO_API_KEY")
LONGMAO_BASE_URL = get_env_flexible("LONGMAO_BASE_URL")
LONGMAO_MODEL = get_env_flexible("LONGMAO_MODEL", "LongCat-Flash-Chat")

# 设置全局 LlamaIndex 配置
Settings.embed_model = SiliconFlowEmbedding(
    model_name=EMBED_MODEL_NAME,
    api_key=SILICONFLOW_API_KEY,
    api_base=SILICONFLOW_BASE_URL,
)
Settings.embed_batch_size = 20
Settings.llm = OpenAILike(
    model=LONGMAO_MODEL,
    api_key=LONGMAO_API_KEY,
    api_base=LONGMAO_BASE_URL,
    temperature=0.1,
    is_chat_model=True,
)

# ================= 数据库操作 =================
def get_db_config():
    """从环境变量、注册表或 secrets.json 获取数据库配置"""
    return {
        "dbname": get_env_flexible("DB_NAME", "media_knowledge_base"),
        "user": get_env_flexible("DB_USER", "root"),
        "password": get_env_flexible("DB_PASSWORD", "15671040800q"),
        "host": get_env_flexible("DB_HOST", "127.0.0.1"),
        "port": get_env_flexible("DB_PORT", "5433")
    }

async def search_kb(query_str: str, up_mid: Optional[int] = None, 
                   use_query_engine: bool = True, top_k: int = 5):
    """
    在 B 站知识库中进行语义检索
    """
    config = get_db_config()
    
    # 1. 初始化向量存储连接
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
    
    # 2. 加载索引
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
    
    # 3. 创建重排器
    reranker = SiliconFlowRerank(
        model=RERANK_MODEL_NAME,
        api_key=SILICONFLOW_API_KEY,
        top_n=top_k
    )
    
    # 4. 配置元数据过滤
    filters = None
    if up_mid:
        filters = MetadataFilters(
            filters=[ExactMatchFilter(key="up_mid", value=up_mid)]
        )
        console.print(f"[cyan]🔍 只搜索 UP 主 {up_mid} 的视频[/cyan]")
    
    if use_query_engine:
        query_engine = index.as_query_engine(
            similarity_top_k=20,
            node_postprocessors=[reranker],
            response_mode=ResponseMode.COMPACT,
            filters=filters,
            vector_store_query_mode=VectorStoreQueryMode.HYBRID,
        )
        
        console.print(f"[bold green]🔍 正在查询:[/bold green] {query_str}")
        response = await query_engine.aquery(query_str)
        
        # 使用 rich 输出结果
        console.print(Panel(Markdown(response.response), title="🤖 AI 生成的答案", border_style="green"))
        
        table = Table(title=f"📄 相关源文档 ({len(response.source_nodes)} 条)")
        table.add_column("Index", style="dim")
        table.add_column("Title", style="cyan")
        table.add_column("BVID", style="magenta")
        table.add_column("Score", style="yellow")
        
        for i, node in enumerate(response.source_nodes, 1):
            metadata = node.metadata
            table.add_row(
                str(i),
                metadata.get('title', 'Unknown'),
                metadata.get('bvid', 'N/A'),
                f"{node.score:.4f}"
            )
        
        console.print(table)
        
        # 写入临时文件
        try:
            with open("search_context.tmp", "w", encoding="utf-8") as f:
                f.write("<KNOWLEDGE_BASE_START>\n")
                f.write(f"QUERY: {query_str}\n")
                f.write(f"ANSWER: {response.response}\n\n")
                f.write("SOURCES:\n")
                for node in response.source_nodes:
                    metadata = node.metadata
                    f.write(f"TITLE: {metadata.get('title')}\n")
                    f.write(f"BVID: {metadata.get('bvid')}\n")
                    f.write(f"SCORE: {node.score:.4f}\n")
                    f.write(f"CONTENT: {node.get_content()}\n")
                    f.write("---CHUNK_END---\n")
                f.write("<KNOWLEDGE_BASE_END>\n")
        except Exception as e:
            console.print(f"[red]⚠️ 写入临时文件失败: {e}[/red]")
            
    else:
        retriever = index.as_retriever(
            similarity_top_k=20,
            vector_store_query_mode=VectorStoreQueryMode.HYBRID,
            alpha=0.3,
            filters=filters,
        )
        
        console.print(f"[bold green]🔍 正在检索:[/bold green] {query_str}")
        nodes = await retriever.aretrieve(query_str)
        reranked_nodes = reranker.postprocess_nodes(nodes, query_bundle=QueryBundle(query_str))
        
        table = Table(title=f"📄 检索结果 ({len(reranked_nodes)} 条)")
        table.add_column("Index", style="dim")
        table.add_column("Title", style="cyan")
        table.add_column("BVID", style="magenta")
        table.add_column("Score", style="yellow")
        
        for i, node in enumerate(reranked_nodes, 1):
            metadata = node.node.metadata
            table.add_row(
                str(i),
                metadata.get('title', 'Unknown'),
                metadata.get('bvid', 'N/A'),
                f"{node.score:.4f}"
            )
        
        console.print(table)
        
        # 写入临时文件
        try:
            with open("search_context.tmp", "w", encoding="utf-8") as f:
                f.write("<KNOWLEDGE_BASE_START>\n")
                for node in reranked_nodes:
                    metadata = node.node.metadata
                    f.write(f"TITLE: {metadata.get('title')}\n")
                    f.write(f"BVID: {metadata.get('bvid')}\n")
                    f.write(f"SCORE: {node.score:.4f}\n")
                    f.write(f"CONTENT: {node.node.get_content()}\n")
                    f.write("---CHUNK_END---\n")
                f.write("<KNOWLEDGE_BASE_END>\n")
        except Exception as e:
            print(f"⚠️ 写入临时文件失败: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="B站视频知识库语义检索工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 基本搜索（生成答案）
  python bili_search_llama.py "DeepSeek如何使用"
  
  # 只返回原始分片（不生成答案）
  python bili_search_llama.py "本地部署RAG" --raw
  
  # 指定 UP 主搜索
  python bili_search_llama.py "AI应用" --up 3546830417693175
  
  # 调整返回数量
  python bili_search_llama.py "Python RAG" --top-k 10
        """
    )
    
    parser.add_argument("query", nargs="+", help="搜索查询")
    parser.add_argument("--up", type=int, metavar="UID", help="只搜索指定 UP 主的视频")
    parser.add_argument("--raw", action="store_true", help="只返回原始分片，不生成答案")
    parser.add_argument("--top-k", type=int, default=5, help="返回结果数量（默认 5）")
    
    args = parser.parse_args()
    query = " ".join(args.query)
    
    asyncio.run(search_kb(
        query_str=query,
        up_mid=args.up,
        use_query_engine=not args.raw,
        top_k=args.top_k
    ))
