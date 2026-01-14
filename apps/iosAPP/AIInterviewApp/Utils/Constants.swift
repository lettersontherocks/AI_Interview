// Constants.swift
// 全局常量配置
//
// 对应小程序: config.js

import Foundation

struct Constants {
    // MARK: - 后端配置
    /// 后端服务器地址
    static let baseURL = "http://47.93.141.137:8003"

    // MARK: - API端点
    struct API {
        static let positions = "\(baseURL)/positions"
        static let positionsSearch = "\(baseURL)/positions/search"
        static let interviewerStyles = "\(baseURL)/interviewer-styles"
        static let startInterview = "\(baseURL)/interview/start"
        static let answer = "\(baseURL)/interview/answer"
        static let report = "\(baseURL)/interview/report"
        static let userProfile = "\(baseURL)/user/profile"
        static let interviewHistory = "\(baseURL)/user/history"
        static let tts = "\(baseURL)/tts/synthesize"
    }

    // MARK: - 应用信息
    static let appName = "AI面试练习"
    static let version = "1.0.0"
    static let buildNumber = "1"

    // MARK: - 业务配置
    struct Business {
        /// 免费用户每日面试次数
        static let freeDailyLimit = 2
        /// VIP月度价格
        static let vipMonthlyPrice = 9.98
        /// 单次面试价格
        static let singleInterviewPrice = 0.99
    }

    // MARK: - UI配置
    struct UI {
        /// 主色调
        static let primaryColorHex = "667eea"
        /// 辅助色
        static let secondaryColorHex = "764ba2"
        /// 成功色
        static let successColorHex = "4CAF50"
        /// 警告色
        static let warningColorHex = "FFA726"
        /// 错误色
        static let errorColorHex = "EF5350"

        /// 默认圆角
        static let cornerRadius: CGFloat = 12
        /// 卡片阴影
        static let shadowRadius: CGFloat = 4
    }

    // MARK: - 存储Key
    struct StorageKey {
        static let userToken = "user_token"
        static let userId = "user_id"
        static let userInfo = "user_info"
        static let lastInterviewSession = "last_interview_session"
    }
}
