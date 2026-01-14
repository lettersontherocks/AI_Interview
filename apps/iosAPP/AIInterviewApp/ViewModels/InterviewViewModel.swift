// InterviewViewModel.swift
// 面试页视图模型
//
// 对应小程序: pages/interview/interview.js

import Foundation
import Combine
import AVFoundation

class InterviewViewModel: ObservableObject {
    @Published var sessionId: String
    @Published var currentQuestion: String
    @Published var questionNumber: Int = 1
    @Published var userAnswer: String = ""
    @Published var transcript: [(role: String, content: String, score: Double?)] = []
    @Published var isRecording = false
    @Published var isPlaying = false
    @Published var isLoading = false
    @Published var instantScore: Double?
    @Published var hint: String?
    @Published var isFinished = false
    @Published var errorMessage: String?

    private var audioService = AudioService.shared
    private var recordingURL: URL?
    private var cancellables = Set<AnyCancellable>()

    init(sessionId: String, firstQuestion: String, audioUrl: String? = nil) {
        self.sessionId = sessionId
        self.currentQuestion = firstQuestion

        // 添加第一个问题到对话记录
        transcript.append((role: "interviewer", content: firstQuestion, score: nil))

        // 自动播放第一个问题的音频
        if let audioUrl = audioUrl {
            playAudio(url: audioUrl)
        }

        print("🎙️ [Interview] 面试会话初始化")
        print("   会话ID: \(sessionId)")
    }

    // MARK: - Recording

    func startRecording() {
        guard !isRecording else { return }

        audioService.startRecording { [weak self] url in
            if let url = url {
                self?.recordingURL = url
                self?.isRecording = true
                print("🎙️ [Interview] 开始录音")
            } else {
                self?.errorMessage = "录音失败，请检查麦克风权限"
            }
        }
    }

    func stopRecording() {
        guard isRecording else { return }

        if let url = audioService.stopRecording() {
            isRecording = false
            print("⏹️ [Interview] 停止录音")

            // TODO: 调用语音识别API
            // 这里暂时使用用户输入的文本
            if !userAnswer.isEmpty {
                submitAnswer(userAnswer)
            }
        }
    }

    // MARK: - Answer Submission

    func submitAnswer(_ answer: String, finish: Bool = false) {
        guard !answer.isEmpty || finish else {
            errorMessage = "请先回答问题"
            return
        }

        isLoading = true

        let request = AnswerRequest(
            sessionId: sessionId,
            answer: answer,
            finishInterview: finish
        )

        print("📤 [Interview] 提交回答")
        print("   回答: \(answer.prefix(50))...")

        // 添加用户回答到对话记录
        transcript.append((role: "candidate", content: answer, score: nil))

        APIService.shared.submitAnswer(request: request) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                switch result {
                case .success(let response):
                    self?.handleAnswerResponse(response)
                case .failure(let error):
                    self?.errorMessage = "提交失败: \(error.localizedDescription)"
                    print("❌ [Interview] 提交回答失败: \(error)")
                }
            }
        }

        // 清空输入
        userAnswer = ""
    }

    private func handleAnswerResponse(_ response: AnswerResponse) {
        // 更新即时评分
        self.instantScore = response.instantScore
        self.hint = response.hint

        // 更新上一条回答的评分
        if let score = response.instantScore, transcript.count > 0 {
            let lastIndex = transcript.count - 1
            transcript[lastIndex].score = score
        }

        print("📊 [Interview] 即时评分: \(response.instantScore ?? 0)")

        if response.isFinished {
            self.isFinished = true
            print("🏁 [Interview] 面试结束")
        } else if let nextQuestion = response.nextQuestion {
            self.currentQuestion = nextQuestion
            self.questionNumber += 1
            transcript.append((role: "interviewer", content: nextQuestion, score: nil))

            print("❓ [Interview] 下一个问题: \(nextQuestion.prefix(50))...")

            // 播放音频
            if let audioUrl = response.audioUrl {
                playAudio(url: audioUrl)
            }
        }
    }

    // MARK: - Audio Playback

    func playAudio(url: String) {
        isPlaying = true
        audioService.playFromURL(urlString: url) { [weak self] in
            self?.isPlaying = false
        }
    }

    func stopAudio() {
        audioService.stopPlaying()
        isPlaying = false
    }

    // MARK: - Interview Control

    func finishInterview() {
        submitAnswer("", finish: true)
    }

    func cleanup() {
        audioService.cleanup()
    }
}
