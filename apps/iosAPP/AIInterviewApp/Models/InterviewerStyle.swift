// InterviewerStyle.swift
// 面试官风格数据模型
//
// 对应小程序: pages/index/index.js 中的面试官风格数据

import Foundation

/// 面试官风格
struct InterviewerStyle: Codable, Identifiable, Hashable {
    let id: String
    let name: String
    let description: String
    let icon: String

    /// 风格类型枚举
    enum StyleType: String {
        case friendly = "friendly"      // 友好型
        case professional = "professional" // 专业型
        case challenging = "challenging"   // 挑战型
        case mentor = "mentor"            // 导师型

        var localizedName: String {
            switch self {
            case .friendly: return "友好型"
            case .professional: return "专业型"
            case .challenging: return "挑战型"
            case .mentor: return "导师型"
            }
        }

        var emoji: String {
            switch self {
            case .friendly: return "😊"
            case .professional: return "💼"
            case .challenging: return "🔥"
            case .mentor: return "🎓"
            }
        }
    }

    var styleType: StyleType? {
        return StyleType(rawValue: id)
    }
}

/// 面试官风格响应
struct InterviewerStylesResponse: Codable {
    let styles: [InterviewerStyle]
    let recommended: String?
}
