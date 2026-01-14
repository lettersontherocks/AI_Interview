// InterviewSession.swift
// 面试会话相关数据模型
//
// 对应小程序: pages/interview/interview.js 中的面试数据

import Foundation

/// 面试会话
struct InterviewSession: Codable, Identifiable {
    let id: String // sessionId
    let sessionId: String
    let userId: String
    let position: String
    let round: String
    let interviewerStyle: String?
    let resume: String?
    let currentQuestion: String
    let questionCount: Int
    let isFinished: Bool
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case sessionId = "session_id"
        case userId = "user_id"
        case position, round
        case interviewerStyle = "interviewer_style"
        case resume
        case currentQuestion = "current_question"
        case questionCount = "question_count"
        case isFinished = "is_finished"
        case createdAt = "created_at"
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.sessionId = try container.decode(String.self, forKey: .sessionId)
        self.id = sessionId
        self.userId = try container.decode(String.self, forKey: .userId)
        self.position = try container.decode(String.self, forKey: .position)
        self.round = try container.decode(String.self, forKey: .round)
        self.interviewerStyle = try container.decodeIfPresent(String.self, forKey: .interviewerStyle)
        self.resume = try container.decodeIfPresent(String.self, forKey: .resume)
        self.currentQuestion = try container.decode(String.self, forKey: .currentQuestion)
        self.questionCount = try container.decode(Int.self, forKey: .questionCount)
        self.isFinished = try container.decode(Bool.self, forKey: .isFinished)

        let dateString = try container.decode(String.self, forKey: .createdAt)
        let formatter = ISO8601DateFormatter()
        self.createdAt = formatter.date(from: dateString) ?? Date()
    }
}

/// 开始面试请求
struct InterviewStartRequest: Codable {
    let userId: String
    let positionId: String
    let round: String
    let interviewerStyle: String?
    let resume: String?

    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case positionId = "position_id"
        case round
        case interviewerStyle = "interviewer_style"
        case resume
    }
}

/// 开始面试响应
struct InterviewStartResponse: Codable {
    let sessionId: String
    let question: String
    let questionType: String
    let audioUrl: String?

    enum CodingKeys: String, CodingKey {
        case sessionId = "session_id"
        case question
        case questionType = "question_type"
        case audioUrl = "audio_url"
    }
}

/// 提交回答请求
struct AnswerRequest: Codable {
    let sessionId: String
    let answer: String
    let finishInterview: Bool

    enum CodingKeys: String, CodingKey {
        case sessionId = "session_id"
        case answer
        case finishInterview = "finish_interview"
    }
}

/// 提交回答响应
struct AnswerResponse: Codable {
    let nextQuestion: String?
    let instantScore: Double?
    let hint: String?
    let isFinished: Bool
    let audioUrl: String?

    enum CodingKeys: String, CodingKey {
        case nextQuestion = "next_question"
        case instantScore = "instant_score"
        case hint
        case isFinished = "is_finished"
        case audioUrl = "audio_url"
    }
}
