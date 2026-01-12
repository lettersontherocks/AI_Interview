"""知识库服务 - 直接连接 ES"""
from typing import List, Dict, Optional
from elasticsearch import Elasticsearch
from config import settings
import dashscope
from dashscope import TextEmbedding


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

        # 配置 DashScope（用于向量化查询）
        dashscope.api_key = settings.dashscope_api_key

    def _get_query_vector(self, text: str) -> Optional[List[float]]:
        """将文本转换为向量

        Args:
            text: 查询文本

        Returns:
            1536维向量，失败返回None
        """
        try:
            response = TextEmbedding.call(
                model=TextEmbedding.Models.text_embedding_v2,
                input=text
            )
            if response.status_code == 200:
                return response.output['embeddings'][0]['embedding']
            else:
                print(f"[ERROR] 向量化失败: {response.message}")
                return None
        except Exception as e:
            print(f"[ERROR] 向量化异常: {e}")
            return None

    def search_questions(
        self,
        query: str,
        position: Optional[str] = None,
        round_name: Optional[str] = None,
        size: int = 10,
        search_type: str = "hybrid"
    ) -> List[Dict]:
        """
        搜索面试题（支持关键词、向量、混合搜索）

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
            # 筛选条件
            filter_clauses = []
            if position:
                # 处理岗位匹配：支持模糊匹配（如"后端工程师 - Python后端"可以匹配"Python工程师"或"后端工程师"）
                # 提取岗位关键词
                position_keywords = position.replace(" - ", " ").split()
                if len(position_keywords) > 1:
                    # 有多个词时，使用should查询（任意一个匹配即可）
                    filter_clauses.append({
                        "bool": {
                            "should": [
                                {"match": {"position": kw}} for kw in position_keywords
                            ],
                            "minimum_should_match": 1
                        }
                    })
                else:
                    # 单个词时，使用match查询（支持模糊匹配）
                    filter_clauses.append({"match": {"position": position}})
            if round_name:
                filter_clauses.append({"term": {"round": round_name}})

            # 根据搜索类型构建查询
            if search_type == "keyword":
                # 纯关键词搜索
                body = {
                    "query": {
                        "bool": {
                            "must": {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["question^2", "answer"],
                                    "type": "best_fields"
                                }
                            },
                            "filter": filter_clauses
                        }
                    },
                    "size": size
                }

            elif search_type == "vector":
                # 纯向量搜索
                query_vector = self._get_query_vector(query)
                if not query_vector:
                    # 向量化失败，降级为关键词搜索
                    print(f"[WARNING] 向量化失败，降级为关键词搜索")
                    return self.search_questions(query, position, round_name, size, "keyword")

                body = {
                    "query": {
                        "script_score": {
                            "query": {
                                "bool": {
                                    "filter": filter_clauses
                                }
                            },
                            "script": {
                                "source": "cosineSimilarity(params.query_vector, 'question_vector') + 1.0",
                                "params": {"query_vector": query_vector}
                            }
                        }
                    },
                    "size": size
                }

            else:  # hybrid
                # 混合搜索：关键词 + 向量（RRF融合）
                query_vector = self._get_query_vector(query)
                if not query_vector:
                    # 向量化失败，降级为关键词搜索
                    print(f"[WARNING] 向量化失败，使用纯关键词搜索")
                    return self.search_questions(query, position, round_name, size, "keyword")

                # 使用 RRF (Reciprocal Rank Fusion) 混合搜索
                body = {
                    "query": {
                        "bool": {
                            "should": [
                                {
                                    "multi_match": {
                                        "query": query,
                                        "fields": ["question^2", "answer"],
                                        "type": "best_fields",
                                        "boost": 0.5  # 关键词权重0.5
                                    }
                                },
                                {
                                    "script_score": {
                                        "query": {"match_all": {}},
                                        "script": {
                                            "source": "cosineSimilarity(params.query_vector, 'question_vector') + 1.0",
                                            "params": {"query_vector": query_vector}
                                        },
                                        "boost": 0.5  # 向量权重0.5
                                    }
                                }
                            ],
                            "filter": filter_clauses,
                            "minimum_should_match": 1
                        }
                    },
                    "size": size
                }

            # 执行搜索
            response = self.es.search(index=self.es_index, body=body)

            # 解析结果
            results = []
            for hit in response["hits"]["hits"]:
                result = hit["_source"]
                result["_score"] = hit["_score"]  # 保存相似度分数
                results.append(result)

            print(f"[知识库] {search_type}搜索 '{query}' 返回 {len(results)} 条结果")
            return results

        except Exception as e:
            print(f"[ERROR] ES 查询失败: {e}")
            import traceback
            traceback.print_exc()
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
