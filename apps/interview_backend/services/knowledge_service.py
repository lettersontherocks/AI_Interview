"""知识库服务 - 直接连接 ES"""
from typing import List, Dict, Optional
from elasticsearch import Elasticsearch
from config import settings


class KnowledgeService:
    """知识库服务 - 直接访问 Elasticsearch"""

    def __init__(self):
        # ES 服务地址（9200 端口）
        # Docker 容器间通信使用服务名：http://elasticsearch:9200
        # 或者使用服务器 IP：http://47.93.141.137:9200
        self.es_host = getattr(settings, 'es_host', 'http://47.93.141.137:9200')
        self.es_index = getattr(settings, 'es_index', 'interview_questions')

        # 创建 ES 客户端
        self.es = Elasticsearch([self.es_host])

    def search_questions(
        self,
        query: str,
        position: Optional[str] = None,
        round_name: Optional[str] = None,
        size: int = 10,
        search_type: str = "hybrid"
    ) -> List[Dict]:
        """
        搜索面试题（直接查询 ES）

        Args:
            query: 搜索关键词（如：Python 列表、HTTP 协议）
            position: 岗位（如：Python后端开发）
            round_name: 面试轮次（如：技术一面）
            size: 返回数量
            search_type: 搜索类型（keyword/vector/hybrid）

        Returns:
            问题列表
        """
        try:
            # 构建查询条件
            must_clauses = []

            # 关键词搜索
            if search_type in ["keyword", "hybrid"]:
                must_clauses.append({
                    "multi_match": {
                        "query": query,
                        "fields": ["question^2", "answer", "category"],
                        "type": "best_fields"
                    }
                })

            # 筛选条件
            filter_clauses = []
            if position:
                filter_clauses.append({"term": {"position.keyword": position}})
            if round_name:
                filter_clauses.append({"term": {"round_name.keyword": round_name}})

            # 构建查询
            body = {
                "query": {
                    "bool": {
                        "must": must_clauses,
                        "filter": filter_clauses
                    }
                },
                "size": size
            }

            # 执行搜索
            response = self.es.search(index=self.es_index, body=body)

            # 解析结果
            results = []
            for hit in response["hits"]["hits"]:
                results.append(hit["_source"])

            return results

        except Exception as e:
            print(f"[ERROR] ES 查询失败: {e}")
            return []

    def search_by_position(
        self,
        position: str,
        limit: int = 15
    ) -> List[Dict]:
        """
        根据岗位获取参考题目（用于面试开始时）

        Args:
            position: 岗位名称
            limit: 返回数量

        Returns:
            问题列表
        """
        return self.search_questions(
            query=position,
            position=position,
            size=limit,
            search_type="hybrid"
        )

    def search_related_questions(
        self,
        keywords: str,
        position: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        根据关键词搜索相关问题（用于追问）

        Args:
            keywords: 关键词（从候选人回答中提取）
            position: 岗位
            limit: 返回数量

        Returns:
            问题列表
        """
        return self.search_questions(
            query=keywords,
            position=position,
            size=limit,
            search_type="vector"  # 使用向量搜索，更智能
        )

    def health_check(self) -> bool:
        """
        检查 ES 是否可用

        Returns:
            True 如果可用
        """
        try:
            return self.es.ping()
        except:
            return False


# 全局单例
knowledge_service = KnowledgeService()
