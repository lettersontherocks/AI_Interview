// PrepareView.swift
// 准备页视图
//
// 对应小程序: pages/prepare/prepare.wxml

import SwiftUI

struct PrepareView: View {
    @StateObject private var viewModel: PrepareViewModel
    @EnvironmentObject var authService: AuthService
    @Environment(\.dismiss) var dismiss
    @State private var showingInterviewView = false
    @State private var sessionId: String?
    @State private var firstQuestion: String?

    init(position: Position, round: String, style: InterviewerStyle?) {
        _viewModel = StateObject(wrappedValue: PrepareViewModel(
            position: position,
            round: round,
            style: style
        ))
    }

    var body: some View {
        NavigationView {
            ZStack {
                ScrollView {
                    VStack(spacing: 24) {
                        // 面试信息卡片
                        interviewInfoCard

                        // 简历输入区域
                        resumeSection

                        // 提示信息
                        tipsSection

                        // 开始按钮
                        startButton
                    }
                    .padding()
                }

                if viewModel.isLoading {
                    LoadingView()
                }
            }
            .navigationTitle("面试准备")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("返回") {
                        dismiss()
                    }
                }
            }
            .alert("提示", isPresented: .constant(viewModel.errorMessage != nil)) {
                Button("确定") {
                    viewModel.errorMessage = nil
                }
            } message: {
                if let error = viewModel.errorMessage {
                    Text(error)
                }
            }
            .fullScreenCover(isPresented: $showingInterviewView) {
                if let sessionId = sessionId, let question = firstQuestion {
                    InterviewView(
                        sessionId: sessionId,
                        firstQuestion: question,
                        position: viewModel.position
                    )
                }
            }
        }
    }

    // MARK: - Interview Info Card

    private var interviewInfoCard: some View {
        VStack(alignment: .leading, spacing: 16) {
            // 标题
            HStack {
                Image(systemName: "doc.text.fill")
                    .foregroundColor(.primaryColor)
                    .font(.title2)
                Text("面试信息")
                    .font(.headline)
                Spacer()
            }

            Divider()

            // 岗位
            HStack {
                Text("岗位:")
                    .foregroundColor(.secondary)
                    .frame(width: 80, alignment: .leading)
                Text(viewModel.position.name)
                    .fontWeight(.medium)
                Spacer()
            }

            // 轮次
            HStack {
                Text("轮次:")
                    .foregroundColor(.secondary)
                    .frame(width: 80, alignment: .leading)
                Text(viewModel.round)
                    .fontWeight(.medium)
                Spacer()
            }

            // 面试官风格
            if let style = viewModel.style {
                HStack {
                    Text("面试官:")
                        .foregroundColor(.secondary)
                        .frame(width: 80, alignment: .leading)
                    Text("\(style.icon) \(style.name)")
                        .fontWeight(.medium)
                    Spacer()
                }
            }

            // 关键词
            if !viewModel.position.keywords.isEmpty {
                VStack(alignment: .leading, spacing: 8) {
                    Text("考察重点:")
                        .foregroundColor(.secondary)

                    FlowLayout(spacing: 8) {
                        ForEach(viewModel.position.keywords, id: \.self) { keyword in
                            Text(keyword)
                                .font(.caption)
                                .padding(.horizontal, 10)
                                .padding(.vertical, 4)
                                .background(Color.primaryColor.opacity(0.1))
                                .foregroundColor(.primaryColor)
                                .cornerRadius(12)
                        }
                    }
                }
            }
        }
        .padding()
        .cardStyle()
    }

    // MARK: - Resume Section

    private var resumeSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "person.text.rectangle")
                    .foregroundColor(.primaryColor)
                Text("简历信息")
                    .font(.headline)
                Text("(可选)")
                    .font(.caption)
                    .foregroundColor(.secondary)
                Spacer()
            }

            Text("提供简历可以让面试更加个性化")
                .font(.caption)
                .foregroundColor(.secondary)

            TextEditor(text: $viewModel.resume)
                .frame(height: 150)
                .padding(8)
                .background(Color.gray.opacity(0.05))
                .cornerRadius(8)
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(Color.gray.opacity(0.2), lineWidth: 1)
                )

            if !viewModel.resume.isEmpty {
                HStack {
                    Spacer()
                    Text("\(viewModel.resume.count)字")
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding()
        .cardStyle()
    }

    // MARK: - Tips Section

    private var tipsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "lightbulb.fill")
                    .foregroundColor(.orange)
                Text("温馨提示")
                    .font(.headline)
                Spacer()
            }

            VStack(alignment: .leading, spacing: 10) {
                tipItem(icon: "checkmark.circle.fill", text: "请在安静的环境中进行面试")
                tipItem(icon: "checkmark.circle.fill", text: "建议使用耳机以获得更好的体验")
                tipItem(icon: "checkmark.circle.fill", text: "请允许麦克风权限以进行语音回答")
                tipItem(icon: "checkmark.circle.fill", text: "面试时长约15-30分钟")
            }
        }
        .padding()
        .background(Color.orange.opacity(0.05))
        .cornerRadius(12)
    }

    private func tipItem(icon: String, text: String) -> some View {
        HStack(alignment: .top, spacing: 10) {
            Image(systemName: icon)
                .foregroundColor(.orange)
                .font(.caption)
            Text(text)
                .font(.caption)
                .foregroundColor(.secondary)
            Spacer()
        }
    }

    // MARK: - Start Button

    private var startButton: some View {
        Button(action: {
            startInterview()
        }) {
            HStack {
                Image(systemName: "play.fill")
                    .font(.system(size: 18))
                Text("开始面试")
                    .font(.headline)
            }
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 16)
            .background(
                LinearGradient(
                    gradient: Gradient(colors: [Color.primaryColor, Color.primaryColor.opacity(0.8)]),
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .cornerRadius(12)
            .shadow(color: Color.primaryColor.opacity(0.3), radius: 8, x: 0, y: 4)
        }
        .disabled(viewModel.isLoading)
    }

    // MARK: - Actions

    private func startInterview() {
        guard let userId = authService.currentUser?.userId else {
            viewModel.errorMessage = "请先登录"
            return
        }

        print("🚀 [Prepare] 启动面试")
        print("   岗位: \(viewModel.position.name)")
        print("   轮次: \(viewModel.round)")
        print("   风格: \(viewModel.style?.name ?? "默认")")

        viewModel.startInterview(userId: userId) { result in
            switch result {
            case .success(let response):
                self.sessionId = response.sessionId
                self.firstQuestion = response.firstQuestion
                self.showingInterviewView = true
                print("✅ [Prepare] 面试开始成功")
                print("   SessionID: \(response.sessionId)")

            case .failure(let error):
                print("❌ [Prepare] 启动面试失败: \(error)")
            }
        }
    }
}

// MARK: - FlowLayout Helper

struct FlowLayout: Layout {
    var spacing: CGFloat = 8

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let result = FlowResult(
            in: proposal.replacingUnspecifiedDimensions().width,
            subviews: subviews,
            spacing: spacing
        )
        return result.size
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let result = FlowResult(
            in: bounds.width,
            subviews: subviews,
            spacing: spacing
        )
        for (index, subview) in subviews.enumerated() {
            subview.place(at: CGPoint(x: bounds.minX + result.positions[index].x, y: bounds.minY + result.positions[index].y), proposal: .unspecified)
        }
    }

    struct FlowResult {
        var size: CGSize
        var positions: [CGPoint]

        init(in maxWidth: CGFloat, subviews: Subviews, spacing: CGFloat) {
            var positions: [CGPoint] = []
            var currentX: CGFloat = 0
            var currentY: CGFloat = 0
            var lineHeight: CGFloat = 0

            for subview in subviews {
                let size = subview.sizeThatFits(.unspecified)

                if currentX + size.width > maxWidth && currentX > 0 {
                    currentX = 0
                    currentY += lineHeight + spacing
                    lineHeight = 0
                }

                positions.append(CGPoint(x: currentX, y: currentY))
                currentX += size.width + spacing
                lineHeight = max(lineHeight, size.height)
            }

            self.positions = positions
            self.size = CGSize(width: maxWidth, height: currentY + lineHeight)
        }
    }
}

// MARK: - Preview

struct PrepareView_Previews: PreviewProvider {
    static var previews: some View {
        PrepareView(
            position: Position(
                id: "1",
                name: "iOS开发工程师",
                description: "负责iOS应用开发",
                keywords: ["Swift", "SwiftUI", "UIKit"],
                categoryId: "1",
                categoryName: "技术岗"
            ),
            round: "技术一面",
            style: nil
        )
        .environmentObject(AuthService())
    }
}
