// InterviewReport.swift
// 面试报告数据模型
//
// 对应小程序: pages/report/report.js 中的报告数据

import Foundation

/// 面试报告
struct InterviewReport: Codable, Identifiable {
    let id: String // sessionId
    let sessionId: String
    let totalScore: Double
    let technicalSkill: Double
    let communication: Double
    let logicThinking: Double
    let problemSolving: Double
    let projectExperience: Double
    let experience: Double
    let suggestions: [String]
    let transcript: [TranscriptItem]
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case sessionId = "session_id"
        case totalScore = "total_score"
        case technicalSkill = "technical_skill"
        case communication
        case logicThinking = "logic_thinking"
        case problemSolving = "problem_solving"
        case projectExperience = "project_experience"
        case experience
        case suggestions
        case transcript
        case createdAt = "created_at"
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.sessionId = try container.decode(String.self, forKey: .sessionId)
        self.id = sessionId
        self.totalScore = try container.decode(Double.self, forKey: .totalScore)
        self.technicalSkill = try container.decode(Double.self, forKey: .technicalSkill)
        self.communication = try container.decode(Double.self, forKey: .communication)
        self.logicThinking = try container.decode(Double.self, forKey: .logicThinking)
        self.problemSolving = try container.decode(Double.self, forKey: .problemSolving)
        self.projectExperience = try container.decode(Double.self, forKey: .projectExperience)
        self.experience = try container.decode(Double.self, forKey: .experience)
        self.suggestions = try container.decode([String].self, forKey: .suggestions)
        self.transcript = try container.decode([TranscriptItem].self, forKey: .transcript)

        let dateString = try container.decode(String.self, forKey: .createdAt)
        let formatter = ISO8601DateFormatter()
        self.createdAt = formatter.date(from: dateString) ?? Date()
    }

    /// 格式化的创建时间（对应小程序的 formatDate）
    var formattedCreatedAt: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "M月d日 HH:mm"
        formatter.locale = Locale(identifier: "zh_CN")
        return formatter.string(from: createdAt)
    }

    /// 面试时长（分钟）
    var duration: Int {
        // 根据对话数量估算时长，每个问答约2-3分钟
        let estimatedMinutes = transcript.count / 2 * 2
        return max(estimatedMinutes, 5) // 最少5分钟
    }

    /// 评分等级
    var scoreLevel: String {
        switch totalScore {
        case 90...100: return "优秀"
        case 80..<90: return "良好"
        case 70..<80: return "中等"
        case 60..<70: return "及格"
        default: return "待提升"
        }
    }

    /// 评分颜色
    var scoreColor: String {
        switch totalScore {
        case 90...100: return Constants.UI.successColorHex
        case 80..<90: return Constants.UI.primaryColorHex
        case 70..<80: return Constants.UI.warningColorHex
        default: return Constants.UI.errorColorHex
        }
    }
}

/// 对话记录项
struct TranscriptItem: Codable, Identifiable {
    let id: String
    let role: String // "interviewer" or "candidate"
    let content: String
    let timestamp: String
    let questionNumber: Int?
    let score: Double?
    let hint: String?
    let feedback: String?

    enum CodingKeys: String, CodingKey {
        case role, content, timestamp
        case questionNumber = "question_number"
        case score, hint, feedback
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.id = UUID().uuidString
        self.role = try container.decode(String.self, forKey: .role)
        self.content = try container.decode(String.self, forKey: .content)
        self.timestamp = try container.decode(String.self, forKey: .timestamp)
        self.questionNumber = try container.decodeIfPresent(Int.self, forKey: .questionNumber)
        self.score = try container.decodeIfPresent(Double.self, forKey: .score)
        self.hint = try container.decodeIfPresent(String.self, forKey: .hint)
        self.feedback = try container.decodeIfPresent(String.self, forKey: .feedback)
    }

    /// 是否是面试官
    var isInterviewer: Bool {
        return role == "interviewer"
    }
}

/// 面试历史记录项
struct InterviewHistoryItem: Codable, Identifiable {
    let id: String // sessionId
    let sessionId: String
    let position: String
    let round: String
    let totalScore: Double?
    let createdAt: Date
    let isFinished: Bool

    enum CodingKeys: String, CodingKey {
        case sessionId = "session_id"
        case position, round
        case totalScore = "total_score"
        case createdAt = "created_at"
        case isFinished = "is_finished"
    }

    // 普通初始化器（用于测试和预览）
    init(sessionId: String, position: String, round: String, createdAt: Date, totalScore: Double? = nil, isFinished: Bool) {
        self.id = sessionId
        self.sessionId = sessionId
        self.position = position
        self.round = round
        self.totalScore = totalScore
        self.createdAt = createdAt
        self.isFinished = isFinished
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.sessionId = try container.decode(String.self, forKey: .sessionId)
        self.id = sessionId
        self.position = try container.decode(String.self, forKey: .position)
        self.round = try container.decode(String.self, forKey: .round)
        self.totalScore = try container.decodeIfPresent(Double.self, forKey: .totalScore)
        self.isFinished = try container.decode(Bool.self, forKey: .isFinished)

        let dateString = try container.decode(String.self, forKey: .createdAt)
        let formatter = ISO8601DateFormatter()
        self.createdAt = formatter.date(from: dateString) ?? Date()
    }

    /// 格式化的创建时间（对应小程序的 formatDate）
    var formattedCreatedAt: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "M月d日 HH:mm"
        formatter.locale = Locale(identifier: "zh_CN")
        return formatter.string(from: createdAt)
    }
}
