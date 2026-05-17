#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "psycopg2-binary",
#     "python-dotenv",
#     "requests",
# ]
# ///
"""
为 showcase / recipe 提供更厚实的演示知识条目。
"""

import argparse
import json

from knowledge_save import save_knowledge


DEMO_ITEMS = [
    {
        "source_type": "test",
        "source_id": "eval_auto",
        "title": "AutoResearch评测条目",
        "content": """
AutoResearch 的核心价值不是“自动搜索”，而是把研究过程拆成可以反复迭代的闭环。

第一步是先定义清楚目标：到底想回答什么问题，最终希望输出成什么样。没有明确目标时，AI 会不断扩散搜索范围，最后产出一份看起来很丰富、但对决策没有帮助的资料堆。

第二步是设计评判标准。评判标准至少要覆盖三个维度：信息是否相关、信息是否可信、输出是否能真正帮助后续行动。Karpathy 提到的关键点就是，很多时候真正难的不是“让 AI 再搜一轮”，而是你要先想明白什么才算“搜得更好”。

第三步是让 AI 在“搜索 -> 提炼 -> 自评 -> 再搜索”之间循环。每一轮都不是简单追加资料，而是根据上一轮的不足修正方向，比如补反方观点、补数据来源、补案例细节，或者主动放弃噪音主题。

这个模式最适合拿来处理“高信息密度但方向不够稳定”的任务，例如：
1. 研究一个新工具链到底值不值得上手
2. 梳理某个 Agent workflow 的真实优缺点
3. 为专题分享或 deck 准备高质量的素材池

如果把它放到知识到 deck 的流水线里，它最大的帮助是：先把主题研究做扎实，再把真正值得展示的结论压缩成卡片，而不是直接从一堆零散素材里硬拼 PPT。
""".strip(),
        "ai_summary": "AutoResearch 的核心是先定义目标和评判标准，再让 AI 在搜索、提炼、自评之间迭代收敛。",
        "metadata": {
            "author": "demo-seed",
            "topic": "autoresearch",
            "format": "framework",
            "showcase": True,
        },
    },
    {
        "source_type": "test",
        "source_id": "eval_ai_summary",
        "title": "向量数据库选型对比",
        "content": """
在个人知识库和中小型 AI 应用里，向量数据库的选型重点不是“谁性能最强”，而是“谁最符合当前复杂度”。

pgvector 的优势是轻量。它直接跑在 PostgreSQL 里，部署和维护成本最低，适合已经用 Postgres 存主数据的团队。对于知识条目规模不大、查询量中等、而且你更在意工程一致性的场景，pgvector 往往是性价比最高的选择。

Milvus 的优势是性能和扩展性。它更适合向量规模大、检索请求高并发、需要分片和更专业索引能力的场景。但它会引入额外的部署复杂度，也意味着需要更强的运维意愿。

Weaviate 的优势是自带更多 AI 管道能力，例如对象模型、向量化流程、内建 API 体验更强。如果团队更想快速拼一个 AI 原型，并接受更重的系统体积，它会比自己手工拼装更省时间。

一个简单的决策框架可以这样看：
1. 如果你已经有 Postgres，而且知识规模还不大，优先 pgvector
2. 如果你确认会走到大规模检索和高并发，优先评估 Milvus
3. 如果你更在意 AI 原型搭建速度，而不是底层轻量，优先看 Weaviate

对于当前这个项目，用 pgvector 最合理，因为它让知识库、metadata、搜索和展示链路都保持在一个熟悉的栈里，整体维护成本最低。
""".strip(),
        "ai_summary": "向量数据库选型应优先看复杂度匹配：个人知识库首选 pgvector，大规模生产再考虑 Milvus 或 Weaviate。",
        "metadata": {
            "author": "demo-seed",
            "topic": "vector-database",
            "format": "comparison",
            "showcase": True,
        },
    },
]


def seed_demo_items() -> dict:
    results = []
    for item in DEMO_ITEMS:
        result = save_knowledge(
            source_type=item["source_type"],
            source_id=item["source_id"],
            title=item["title"],
            content=item["content"],
            metadata=item["metadata"],
            ai_summary=item["ai_summary"],
        )
        results.append(
            {
                "source_type": item["source_type"],
                "source_id": item["source_id"],
                "title": item["title"],
                "success": result.get("success", False),
                "id": result.get("id"),
                "ai_summary": result.get("ai_summary"),
            }
        )

    return {"seeded": len(results), "results": results}


def main():
    parser = argparse.ArgumentParser(description="写入更厚实的 showcase 演示知识")
    parser.parse_args()
    print(json.dumps(seed_demo_items(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
