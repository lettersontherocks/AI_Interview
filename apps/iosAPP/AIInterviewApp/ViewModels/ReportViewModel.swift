// ReportViewModel.swift
// 报告页视图模型
//
// 对应小程序: pages/report/report.js

import Foundation
import Combine
import SwiftUI

class ReportViewModel: ObservableObject {
    @Published var report: InterviewReport?
    @Published var isLoading = false
    @Published var errorMessage: String?

    let sessionId: String

    init(sessionId: String) {
        self.sessionId = sessionId
        loadReport()
    }

    // MARK: - Data Loading

    func loadReport() {
        isLoading = true
        errorMessage = nil

        print("📊 [Report] 加载面试报告: \(sessionId)")

        APIService.shared.fetchReport(sessionId: sessionId) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                switch result {
                case .success(let report):
                    self?.report = report
                    print("✅ [Report] 报告加载成功")
                    print("   总分: \(report.totalScore)")
                    print("   技术: \(report.technicalSkill)")
                    print("   沟通: \(report.communication)")
                case .failure(let error):
                    self?.errorMessage = "加载报告失败: \(error.localizedDescription)"
                    print("❌ [Report] 报告加载失败: \(error)")
                }
            }
        }
    }

    // MARK: - Computed Properties

    var scoreLevel: String {
        guard let report = report else { return "" }
        return report.scoreLevel
    }

    var scoreColor: Color {
        guard let report = report else { return .gray }
        return Color(hex: report.scoreColor)
    }

    var hasTranscript: Bool {
        return report?.transcript.isEmpty == false
    }

    // MARK: - Actions

    func retry() {
        loadReport()
    }

    func shareReport() {
        // TODO: 实现分享功能
        print("📤 [Report] 分享报告")
    }
}
