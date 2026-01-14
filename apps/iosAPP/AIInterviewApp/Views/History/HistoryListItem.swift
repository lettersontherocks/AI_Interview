// HistoryListItem.swift
// 历史记录列表项组件
//
// 可重用的历史记录卡片

import SwiftUI

struct HistoryListItem: View {
    let item: InterviewHistoryItem

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // 头部: 岗位和状态
            HStack {
                Text(item.position)
                    .font(.headline)
                    .foregroundColor(.primary)

                Spacer()

                statusBadge
            }

            // 轮次和时间
            HStack(spacing: 16) {
                Label(item.round, systemImage: "number")
                    .font(.caption)
                    .foregroundColor(.secondary)

                Label(item.formattedCreatedAt, systemImage: "clock")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            Divider()

            // 底部: 分数或状态
            HStack {
                if item.isFinished {
                    // 已完成 - 显示分数
                    if let score = item.totalScore {
                        HStack(spacing: 8) {
                            // 总分
                            HStack(spacing: 4) {
                                Text("总分:")
                                    .font(.caption)
                                    .foregroundColor(.secondary)

                                Text(String(format: "%.1f", score))
                                    .font(.title3)
                                    .fontWeight(.bold)
                                    .foregroundColor(scoreColor(score))
                            }

                            Divider()
                                .frame(height: 20)

                            // 等级
                            Text(scoreLevel(score))
                                .font(.caption)
                                .fontWeight(.medium)
                                .foregroundColor(scoreColor(score))
                                .padding(.horizontal, 10)
                                .padding(.vertical, 4)
                                .background(scoreColor(score).opacity(0.2))
                                .cornerRadius(8)
                        }
                    }

                    Spacer()

                    // 查看报告按钮
                    HStack(spacing: 4) {
                        Text("查看报告")
                            .font(.caption)
                            .foregroundColor(.primaryColor)

                        Image(systemName: "chevron.right")
                            .font(.caption2)
                            .foregroundColor(.primaryColor)
                    }

                } else {
                    // 未完成
                    Text("未完成")
                        .font(.caption)
                        .foregroundColor(.orange)

                    Spacer()

                    // 继续面试按钮
                    HStack(spacing: 4) {
                        Text("继续面试")
                            .font(.caption)
                            .foregroundColor(.orange)

                        Image(systemName: "chevron.right")
                            .font(.caption2)
                            .foregroundColor(.orange)
                    }
                }
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.05), radius: 4, x: 0, y: 2)
    }

    // MARK: - Status Badge

    private var statusBadge: some View {
        Group {
            if item.isFinished {
                HStack(spacing: 4) {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.caption2)
                    Text("已完成")
                        .font(.caption)
                }
                .foregroundColor(.green)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color.green.opacity(0.1))
                .cornerRadius(12)
            } else {
                HStack(spacing: 4) {
                    Image(systemName: "clock.fill")
                        .font(.caption2)
                    Text("进行中")
                        .font(.caption)
                }
                .foregroundColor(.orange)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(Color.orange.opacity(0.1))
                .cornerRadius(12)
            }
        }
    }

    // MARK: - Helpers

    private func scoreColor(_ score: Double) -> Color {
        switch score {
        case 90...100:
            return .green
        case 80..<90:
            return .blue
        case 70..<80:
            return .orange
        default:
            return .red
        }
    }

    private func scoreLevel(_ score: Double) -> String {
        switch score {
        case 90...100:
            return "优秀"
        case 80..<90:
            return "良好"
        case 70..<80:
            return "中等"
        case 60..<70:
            return "及格"
        default:
            return "不及格"
        }
    }
}

// MARK: - Preview

struct HistoryListItem_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: 12) {
            // 已完成
            HistoryListItem(item: InterviewHistoryItem(
                sessionId: "1",
                position: "iOS开发工程师",
                round: "技术一面",
                createdAt: Date(),
                totalScore: 85.5,
                isFinished: true
            ))

            // 未完成
            HistoryListItem(item: InterviewHistoryItem(
                sessionId: "2",
                position: "前端开发工程师",
                round: "技术二面",
                createdAt: Date(),
                totalScore: nil,
                isFinished: false
            ))
        }
        .padding()
        .background(Color.gray.opacity(0.1))
    }
}
