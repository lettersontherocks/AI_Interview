// ReportView.swift
// 报告页视图
//
// 对应小程序: pages/report/report.wxml

import SwiftUI

struct ReportView: View {
    @StateObject private var viewModel: ReportViewModel
    @Environment(\.dismiss) var dismiss
    @State private var showingShareSheet = false

    init(sessionId: String) {
        _viewModel = StateObject(wrappedValue: ReportViewModel(sessionId: sessionId))
    }

    var body: some View {
        NavigationView {
            ZStack {
                if viewModel.isLoading {
                    LoadingView()
                } else if let error = viewModel.errorMessage {
                    ErrorView(message: error) {
                        viewModel.retry()
                    }
                } else if let report = viewModel.report {
                    ScrollView {
                        VStack(spacing: 24) {
                            // 总分卡片
                            totalScoreCard(report: report)

                            // 雷达图
                            radarChartCard(report: report)

                            // 各项得分
                            scoresCard(report: report)

                            // 改进建议
                            suggestionsCard(report: report)

                            // 面试记录
                            if viewModel.hasTranscript {
                                transcriptCard(report: report)
                            }

                            // 底部按钮
                            actionButtons
                        }
                        .padding()
                    }
                }
            }
            .navigationTitle("面试报告")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("完成") {
                        dismiss()
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        viewModel.shareReport()
                    }) {
                        Image(systemName: "square.and.arrow.up")
                    }
                }
            }
        }
    }

    // MARK: - Total Score Card

    private func totalScoreCard(report: InterviewReport) -> some View {
        VStack(spacing: 16) {
            // 分数
            Text(String(format: "%.1f", report.totalScore))
                .font(.system(size: 64, weight: .bold))
                .foregroundColor(viewModel.scoreColor)

            // 等级
            Text(viewModel.scoreLevel)
                .font(.title2)
                .fontWeight(.semibold)
                .foregroundColor(viewModel.scoreColor)

            // 进度条
            ZStack(alignment: .leading) {
                RoundedRectangle(cornerRadius: 10)
                    .fill(Color.gray.opacity(0.2))
                    .frame(height: 8)

                RoundedRectangle(cornerRadius: 10)
                    .fill(
                        LinearGradient(
                            gradient: Gradient(colors: [
                                viewModel.scoreColor,
                                viewModel.scoreColor.opacity(0.7)
                            ]),
                            startPoint: .leading,
                            endPoint: .trailing
                        )
                    )
                    .frame(width: CGFloat(report.totalScore) / 100 * UIScreen.main.bounds.width * 0.85, height: 8)
            }
            .frame(maxWidth: .infinity)

            // 时间信息
            HStack {
                Image(systemName: "clock")
                    .foregroundColor(.secondary)
                Text(report.formattedCreatedAt)
                    .font(.caption)
                    .foregroundColor(.secondary)

                Spacer()

                Image(systemName: "timer")
                    .foregroundColor(.secondary)
                Text("用时\(report.duration)分钟")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .cardStyle()
    }

    // MARK: - Radar Chart Card

    private func radarChartCard(report: InterviewReport) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("能力雷达图")
                .font(.headline)

            ScoreRadarChart(
                technicalSkill: report.technicalSkill,
                communication: report.communication,
                logicThinking: report.logicThinking,
                problemSolving: report.problemSolving,
                projectExperience: report.projectExperience
            )
            .frame(height: 250)
        }
        .padding()
        .cardStyle()
    }

    // MARK: - Scores Card

    private func scoresCard(report: InterviewReport) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("详细评分")
                .font(.headline)

            VStack(spacing: 12) {
                scoreItem(title: "技术能力", score: report.technicalSkill, icon: "gearshape.fill")
                scoreItem(title: "沟通表达", score: report.communication, icon: "bubble.left.and.bubble.right.fill")
                scoreItem(title: "逻辑思维", score: report.logicThinking, icon: "brain.head.profile")
                scoreItem(title: "问题解决", score: report.problemSolving, icon: "lightbulb.fill")
                scoreItem(title: "项目经验", score: report.projectExperience, icon: "folder.fill")
            }
        }
        .padding()
        .cardStyle()
    }

    private func scoreItem(title: String, score: Double, icon: String) -> some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(.primaryColor)
                .frame(width: 24)

            Text(title)
                .font(.body)
                .frame(width: 80, alignment: .leading)

            ZStack(alignment: .leading) {
                RoundedRectangle(cornerRadius: 4)
                    .fill(Color.gray.opacity(0.2))
                    .frame(height: 8)

                RoundedRectangle(cornerRadius: 4)
                    .fill(Color.primaryColor)
                    .frame(width: CGFloat(score) / 100 * 150, height: 8)
            }
            .frame(width: 150)

            Spacer()

            Text(String(format: "%.1f", score))
                .font(.body)
                .fontWeight(.semibold)
                .foregroundColor(.primaryColor)
        }
    }

    // MARK: - Suggestions Card

    private func suggestionsCard(report: InterviewReport) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Image(systemName: "lightbulb.fill")
                    .foregroundColor(.orange)
                Text("改进建议")
                    .font(.headline)
                Spacer()
            }

            if report.suggestions.isEmpty {
                Text("暂无改进建议")
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .center)
                    .padding()
            } else {
                VStack(alignment: .leading, spacing: 12) {
                    ForEach(Array(report.suggestions.enumerated()), id: \.offset) { index, suggestion in
                        HStack(alignment: .top, spacing: 12) {
                            Text("\(index + 1).")
                                .font(.body)
                                .foregroundColor(.orange)
                                .fontWeight(.semibold)

                            Text(suggestion)
                                .font(.body)
                                .foregroundColor(.primary)
                                .fixedSize(horizontal: false, vertical: true)

                            Spacer()
                        }
                    }
                }
            }
        }
        .padding()
        .background(Color.orange.opacity(0.05))
        .cornerRadius(12)
    }

    // MARK: - Transcript Card

    private func transcriptCard(report: InterviewReport) -> some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("面试记录")
                .font(.headline)

            VStack(spacing: 12) {
                ForEach(Array(report.transcript.enumerated()), id: \.offset) { index, item in
                    VStack(alignment: .leading, spacing: 8) {
                        // 角色和时间
                        HStack {
                            Text(item.role == "interviewer" ? "面试官" : "你")
                                .font(.caption)
                                .fontWeight(.semibold)
                                .foregroundColor(item.role == "interviewer" ? .primaryColor : .blue)

                            Spacer()

                            if let score = item.score {
                                HStack(spacing: 2) {
                                    Image(systemName: "star.fill")
                                        .font(.caption2)
                                    Text(String(format: "%.1f", score))
                                        .font(.caption)
                                }
                                .foregroundColor(.orange)
                            }
                        }

                        // 内容
                        Text(item.content)
                            .font(.body)
                            .foregroundColor(.primary)
                            .padding()
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .background(
                                item.role == "interviewer" ?
                                Color.gray.opacity(0.1) :
                                Color.primaryColor.opacity(0.1)
                            )
                            .cornerRadius(8)
                    }

                    if index < report.transcript.count - 1 {
                        Divider()
                    }
                }
            }
        }
        .padding()
        .cardStyle()
    }

    // MARK: - Action Buttons

    private var actionButtons: some View {
        VStack(spacing: 12) {
            Button(action: {
                // 重新面试
                dismiss()
            }) {
                HStack {
                    Image(systemName: "arrow.clockwise")
                    Text("再来一次")
                }
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 14)
                .background(Color.primaryColor)
                .cornerRadius(10)
            }

            Button(action: {
                dismiss()
            }) {
                Text("返回首页")
                    .foregroundColor(.primaryColor)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 14)
                    .background(Color.primaryColor.opacity(0.1))
                    .cornerRadius(10)
            }
        }
    }
}

// MARK: - Preview

struct ReportView_Previews: PreviewProvider {
    static var previews: some View {
        ReportView(sessionId: "test-session-id")
    }
}
