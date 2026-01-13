"""岗位配置服务"""
import json
import os
from typing import List, Dict, Optional
from functools import lru_cache


class PositionService:
    """岗位配置管理服务

    ⚡ 优化：使用类变量缓存配置，避免重复加载 JSON 文件
    """

    # 类级别缓存（所有实例共享，应用启动时加载一次）
    _config_cache = None
    _position_map_cache = None

    def __init__(self):
        # 如果缓存不存在，则加载配置
        if PositionService._config_cache is None:
            print("[岗位配置] 首次加载 positions.json")
            config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'positions.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                PositionService._config_cache = json.load(f)
            print(f"[岗位配置] 已加载 {len(PositionService._config_cache.get('categories', []))} 个分类")
        else:
            print("[岗位配置] 使用缓存数据")

        # 使用缓存的配置
        self.config = PositionService._config_cache

        # 如果position_map缓存不存在，则构建
        if PositionService._position_map_cache is None:
            print("[岗位配置] 构建岗位映射表")
            PositionService._position_map_cache = {}
            self._build_position_map()
        else:
            print("[岗位配置] 使用缓存的映射表")

        # 使用缓存的映射
        self.position_map = PositionService._position_map_cache

    def _build_position_map(self):
        """构建岗位ID映射表"""
        for category in self.config['categories']:
            for position in category['positions']:
                # 添加父级岗位
                PositionService._position_map_cache[position['id']] = {
                    'id': position['id'],
                    'name': position['name'],
                    'description': position['description'],
                    'keywords': position['keywords'],
                    'category_name': category['name'],
                    'is_parent': True,
                    'has_children': len(position.get('sub_positions', [])) > 0
                }

                # 添加子级岗位
                for sub_position in position.get('sub_positions', []):
                    PositionService._position_map_cache[sub_position['id']] = {
                        'id': sub_position['id'],
                        'name': sub_position['name'],
                        'description': sub_position['description'],
                        'keywords': sub_position['keywords'],
                        'parent_id': position['id'],
                        'parent_name': position['name'],
                        'category_name': category['name'],
                        'is_parent': False,
                        'has_children': False
                    }
        print(f"[岗位配置] 映射表构建完成，共 {len(PositionService._position_map_cache)} 个岗位")

    def get_all_categories(self) -> List[Dict]:
        """获取所有岗位分类"""
        return self.config['categories']

    def get_position_by_id(self, position_id: str) -> Optional[Dict]:
        """根据ID获取岗位信息"""
        return self.position_map.get(position_id)

    def search_positions(self, keyword: str) -> List[Dict]:
        """根据关键词搜索岗位"""
        keyword = keyword.lower()
        results = []

        for position_id, position_info in self.position_map.items():
            # 搜索名称
            if keyword in position_info['name'].lower():
                results.append(position_info)
                continue

            # 搜索描述
            if keyword in position_info['description'].lower():
                results.append(position_info)
                continue

            # 搜索关键词
            for kw in position_info['keywords']:
                if keyword in kw.lower():
                    results.append(position_info)
                    break

        return results

    def get_position_full_name(self, position_id: str) -> str:
        """获取岗位完整名称（包括父级）"""
        position = self.get_position_by_id(position_id)
        if not position:
            return position_id

        if position['is_parent']:
            return position['name']
        else:
            # 子级岗位，返回 "父级 - 子级" 格式
            return f"{position['parent_name']} - {position['name']}"

    def get_position_keywords(self, position_id: str) -> List[str]:
        """获取岗位相关关键词（用于生成面试问题提示）"""
        position = self.get_position_by_id(position_id)
        if not position:
            return []

        keywords = position['keywords'].copy()

        # 如果是子级岗位，合并父级的关键词
        if not position['is_parent']:
            parent = self.get_position_by_id(position.get('parent_id', ''))
            if parent:
                keywords.extend(parent['keywords'])

        return keywords

    def validate_position_id(self, position_id: str) -> bool:
        """验证岗位ID是否有效"""
        return position_id in self.position_map

    @classmethod
    def clear_cache(cls):
        """
        清除缓存（在配置文件更新时调用）

        注意：清除后需要重新创建 position_service 实例
        """
        cls._config_cache = None
        cls._position_map_cache = None
        print("[岗位配置] 缓存已清除")


# 全局单例
position_service = PositionService()
