// PrepareViewModel.swift
// 准备页视图模型
//
// 对应小程序: pages/prepare/prepare.js

import Foundation
import Combine

class PrepareViewModel: ObservableObject {
    @Published var position: Position
    @Published var round: String
    @Published var style: InterviewerStyle?
    @Published var resume: String = ""
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var showingAlert = false

    var userId: String

    init(position: Position, round: String, style: InterviewerStyle?, userId: String) {
        self.position = position
        self.round = round
        self.style = style
        self.userId = userId
    }

    // MARK: - Actions

    func startInterview(completion: @escaping (Result<InterviewStartResponse, Error>) -> Void) {
        guard !userId.isEmpty else {
            errorMessage = "用户ID不能为空"
            completion(.failure(NSError(domain: "UserId Required", code: -1)))
            return
        }

        isLoading = true
        errorMessage = nil

        let request = InterviewStartRequest(
            userId: userId,
            positionId: position.id,
            round: round,
            interviewerStyle: style?.id,
            resume: resume.isEmpty ? nil : resume
        )

        print("🚀 [Prepare] 开始面试")
        print("   岗位: \(position.name)")
        print("   轮次: \(round)")
        print("   风格: \(style?.name ?? "默认")")

        APIService.shared.startInterview(request: request) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                switch result {
                case .success(let response):
                    print("✅ [Prepare] 面试开始成功")
                    print("   会话ID: \(response.sessionId)")
                    print("   第一个问题: \(response.question.prefix(50))...")
                    completion(.success(response))
                case .failure(let error):
                    self?.errorMessage = "开始面试失败: \(error.localizedDescription)"
                    self?.showingAlert = true
                    print("❌ [Prepare] 面试开始失败: \(error)")
                    completion(.failure(error))
                }
            }
        }
    }

    func updateResume(_ text: String) {
        self.resume = text
    }

    var canStart: Bool {
        return !userId.isEmpty
    }
}
