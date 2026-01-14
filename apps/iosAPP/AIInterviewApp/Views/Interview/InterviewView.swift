// InterviewView.swift
// 面试页视图
//
// 对应小程序: pages/interview/interview.wxml

import SwiftUI

struct InterviewView: View {
    @StateObject private var viewModel: InterviewViewModel
    @Environment(\.dismiss) var dismiss
    @State private var showingFinishAlert = false
    @State private var showingReportView = false

    init(sessionId: String, firstQuestion: String, position: Position) {
        _viewModel = StateObject(wrappedValue: InterviewViewModel(
            sessionId: sessionId,
            firstQuestion: firstQuestion,
            position: position
        ))
    }

    var body: some View {
        NavigationView {
            ZStack {
                // 背景渐变
                LinearGradient(
                    gradient: Gradient(colors: [
                        Color.primaryColor.opacity(0.05),
                        Color.white
                    ]),
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()

                VStack(spacing: 0) {
                    // 顶部进度指示
                    progressHeader

                    // 对话区域
                    ScrollViewReader { proxy in
                        ScrollView {
                            LazyVStack(spacing: 16) {
                                ForEach(Array(viewModel.transcript.enumerated()), id: \.offset) { index, item in
                                    messageCard(item: item, index: index)
                                        .id(index)
                                }
                            }
                            .padding()
                        }
                        .onChange(of: viewModel.transcript.count) { _ in
                            withAnimation {
                                proxy.scrollTo(viewModel.transcript.count - 1, anchor: .bottom)
                            }
                        }
                    }

                    // 底部录音区域
                    recordingArea
                }

                // 加载遮罩
                if viewModel.isLoading {
                    LoadingView()
                }
            }
            .navigationTitle("\(viewModel.position.name)面试")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        showingFinishAlert = true
                    }) {
                        Text("结束")
                            .foregroundColor(.red)
                    }
                }
            }
            .alert("确认结束面试?", isPresented: $showingFinishAlert) {
                Button("取消", role: .cancel) {}
                Button("结束面试", role: .destructive) {
                    finishInterview()
                }
            } message: {
                Text("结束后将生成面试报告")
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
            .fullScreenCover(isPresented: $showingReportView) {
                ReportView(sessionId: viewModel.sessionId)
            }
        }
        .interactiveDismissDisabled()
    }

    // MARK: - Progress Header

    private var progressHeader: some View {
        VStack(spacing: 8) {
            HStack {
                Image(systemName: "clock")
                    .foregroundColor(.secondary)
                Text("已进行 \(viewModel.formattedElapsedTime)")
                    .font(.caption)
                    .foregroundColor(.secondary)

                Spacer()

                Text("第\(viewModel.currentQuestionNumber)题")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding(.horizontal)

            // 进度条
            ProgressView(value: Double(viewModel.currentQuestionNumber), total: 10)
                .tint(.primaryColor)
                .padding(.horizontal)
        }
        .padding(.vertical, 12)
        .background(Color.white)
    }

    // MARK: - Message Card

    private func messageCard(item: InterviewViewModel.TranscriptItem, index: Int) -> some View {
        HStack(alignment: .top, spacing: 12) {
            if item.role == "interviewer" {
                // 面试官消息(左侧)
                avatarView(isInterviewer: true)

                VStack(alignment: .leading, spacing: 8) {
                    // 问题文本
                    Text(item.content)
                        .font(.body)
                        .padding()
                        .background(Color.white)
                        .cornerRadius(12)
                        .shadow(color: Color.black.opacity(0.05), radius: 4, x: 0, y: 2)

                    // 音频播放按钮
                    if let audioUrl = item.audioUrl, !audioUrl.isEmpty {
                        Button(action: {
                            viewModel.playAudio(url: audioUrl)
                        }) {
                            HStack {
                                Image(systemName: viewModel.isPlayingAudio && viewModel.playingAudioUrl == audioUrl ? "pause.circle.fill" : "play.circle.fill")
                                Text(viewModel.isPlayingAudio && viewModel.playingAudioUrl == audioUrl ? "播放中..." : "播放语音")
                                    .font(.caption)
                            }
                            .foregroundColor(.primaryColor)
                            .padding(.horizontal, 12)
                            .padding(.vertical, 6)
                            .background(Color.primaryColor.opacity(0.1))
                            .cornerRadius(16)
                        }
                    }
                }

                Spacer(minLength: 40)

            } else {
                // 用户回答(右侧)
                Spacer(minLength: 40)

                VStack(alignment: .trailing, spacing: 8) {
                    // 回答文本
                    Text(item.content)
                        .font(.body)
                        .padding()
                        .background(
                            LinearGradient(
                                gradient: Gradient(colors: [
                                    Color.primaryColor,
                                    Color.primaryColor.opacity(0.8)
                                ]),
                                startPoint: .topLeading,
                                endPoint: .bottomTrailing
                            )
                        )
                        .foregroundColor(.white)
                        .cornerRadius(12)
                        .shadow(color: Color.primaryColor.opacity(0.3), radius: 4, x: 0, y: 2)

                    // 即时分数
                    if let score = item.score {
                        HStack(spacing: 4) {
                            Image(systemName: "star.fill")
                                .font(.caption2)
                            Text(String(format: "%.1f分", score))
                                .font(.caption)
                        }
                        .foregroundColor(.orange)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 4)
                        .background(Color.orange.opacity(0.1))
                        .cornerRadius(12)
                    }

                    // 提示信息
                    if let hint = item.hint, !hint.isEmpty {
                        HStack(spacing: 6) {
                            Image(systemName: "lightbulb.fill")
                                .font(.caption2)
                            Text(hint)
                                .font(.caption)
                                .lineLimit(2)
                        }
                        .foregroundColor(.orange)
                        .padding(.horizontal, 10)
                        .padding(.vertical, 6)
                        .background(Color.orange.opacity(0.1))
                        .cornerRadius(8)
                    }
                }

                avatarView(isInterviewer: false)
            }
        }
    }

    private func avatarView(isInterviewer: Bool) -> some View {
        Image(systemName: isInterviewer ? "person.crop.circle.fill" : "person.circle.fill")
            .resizable()
            .frame(width: 36, height: 36)
            .foregroundColor(isInterviewer ? .primaryColor : .blue)
            .padding(.top, 4) // 稍微向下偏移，让头像与文本顶部对齐更自然
    }

    // MARK: - Recording Area

    private var recordingArea: some View {
        VStack(spacing: 12) {
            Divider()

            // 当前问题显示
            if !viewModel.currentQuestion.isEmpty {
                Text("当前问题: \(viewModel.currentQuestion)")
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .lineLimit(2)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal)
            }

            // 录音按钮
            RecordingButton(
                isRecording: viewModel.isRecording,
                onTap: {
                    if viewModel.isRecording {
                        viewModel.stopRecording()
                    } else {
                        viewModel.startRecording()
                    }
                }
            )

            // 提示文本
            Text(viewModel.isRecording ? "松开发送" : "按住说话")
                .font(.caption)
                .foregroundColor(.secondary)

            // 跳过按钮
            if !viewModel.isRecording {
                Button(action: {
                    viewModel.skipQuestion()
                }) {
                    Text("跳过这题")
                        .font(.caption)
                        .foregroundColor(.orange)
                        .padding(.horizontal, 16)
                        .padding(.vertical, 6)
                        .background(Color.orange.opacity(0.1))
                        .cornerRadius(16)
                }
            }
        }
        .padding()
        .background(Color.white)
    }

    // MARK: - Actions

    private func finishInterview() {
        print("🏁 [Interview] 结束面试")
        viewModel.finishInterview { success in
            if success {
                showingReportView = true
            }
        }
    }
}

// MARK: - Preview

struct InterviewView_Previews: PreviewProvider {
    static var previews: some View {
        InterviewView(
            sessionId: "test-session-id",
            firstQuestion: "请简单介绍一下你的项目经验?",
            position: Position(
                id: "1",
                name: "iOS开发工程师",
                description: "负责iOS应用开发",
                keywords: ["Swift", "SwiftUI"],
                categoryName: "技术岗",
                isParent: false,
                hasChildren: false,
                parentId: nil,
                parentName: nil
            )
        )
    }
}
