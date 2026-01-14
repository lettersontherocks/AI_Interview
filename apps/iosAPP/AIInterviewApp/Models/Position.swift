// Position.swift
// 岗位相关数据模型
//
// 对应小程序: pages/index/index.js 中的岗位数据

import Foundation

/// 岗位信息
struct Position: Codable, Identifiable, Hashable {
    let id: String
    let name: String
    let description: String
    let keywords: [String]
    let categoryName: String?
    let isParent: Bool
    let hasChildren: Bool
    let parentId: String?
    let parentName: String?

    enum CodingKeys: String, CodingKey {
        case id, name, description, keywords
        case categoryName = "category_name"
        case isParent = "is_parent"
        case hasChildren = "has_children"
        case parentId = "parent_id"
        case parentName = "parent_name"
    }
}

/// 岗位分类
struct PositionCategory: Codable, Identifiable {
    let id: String
    let name: String
    let icon: String
    let positions: [Position]

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.id = try container.decodeIfPresent(String.self, forKey: .id) ?? UUID().uuidString
        self.name = try container.decode(String.self, forKey: .name)
        self.icon = try container.decode(String.self, forKey: .icon)
        self.positions = try container.decode([Position].self, forKey: .positions)
    }

    enum CodingKeys: String, CodingKey {
        case id, name, icon, positions
    }
}

/// 岗位列表响应
struct PositionsResponse: Codable {
    let categories: [PositionCategory]
}
