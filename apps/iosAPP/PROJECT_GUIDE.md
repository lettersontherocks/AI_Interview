# iOS项目完整实现指南

本文档提供iOS项目的完整实现代码框架和说明。由于文件众多,这里提供核心代码结构,开发者可根据此指南完成完整项目。

---

## 📦 已创建的文件

### ✅ 核心文件(已完成)
- `README.md` - 项目完整说明文档
- `AIInterviewApp/App/AIInterviewApp.swift` - 应用入口
- `AIInterviewApp/App/ContentView.swift` - 主容器视图
- `AIInterviewApp/Utils/Constants.swift` - 全局常量
- `AIInterviewApp/Utils/Extensions.swift` - 扩展方法

---

## 📋 待完成文件清单

### 1. 数据模型层 (Models/)

所有模型都应实现 `Codable` 协议以支持JSON序列化。

#### Position.swift
```swift
struct Position: Codable, Identifiable {
    let id: String
    let name: String
    let description: String
    let keywords: [String]
    let categoryName: String?
    let isParent: Bool
    let hasChildren: Bool
    let parentId: String?
    let parentName: String?
}

struct PositionCategory: Codable, Identifiable {
    let id: String
    let name: String
    let icon: String
    let positions: [Position]
}
```

#### User.swift
```swift
struct User: Codable {
    let userId: String
    let openid: String?
    let nickname: String
    let avatar: String?
    let isVip: Bool
    let vipExpireDate: Date?
    let freeCountToday: Int
    let createdAt: Date
}
```

#### InterviewSession.swift
```swift
struct InterviewSession: Codable {
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
}

struct InterviewStartRequest: Codable {
    let userId: String
    let positionId: String
    let round: String
    let interviewerStyle: String?
    let resume: String?
}

struct InterviewStartResponse: Codable {
    let sessionId: String
    let question: String
    let questionType: String
    let audioUrl: String?
}

struct AnswerRequest: Codable {
    let sessionId: String
    let answer: String
    let finishInterview: Bool
}

struct AnswerResponse: Codable {
    let nextQuestion: String?
    let instantScore: Double?
    let hint: String?
    let isFinished: Bool
    let audioUrl: String?
}
```

#### InterviewReport.swift
```swift
struct InterviewReport: Codable, Identifiable {
    let id: String // sessionId
    let sessionId: String
    let totalScore: Double
    let technicalSkill: Double
    let communication: Double
    let logicThinking: Double
    let experience: Double
    let suggestions: [String]
    let transcript: [TranscriptItem]
    let createdAt: Date
}

struct TranscriptItem: Codable, Identifiable {
    let id = UUID()
    let role: String // "interviewer" or "candidate"
    let content: String
    let timestamp: String
    let questionNumber: Int?
    let score: Double?
    let hint: String?
}
```

#### InterviewerStyle.swift
```swift
struct InterviewerStyle: Codable, Identifiable {
    let id: String
    let name: String
    let description: String
    let icon: String
}
```

---

### 2. 服务层 (Services/)

#### APIService.swift
```swift
import Foundation
import Combine

class APIService {
    static let shared = APIService()

    private init() {}

    // MARK: - Generic Request Method

    func request<T: Decodable>(
        _ endpoint: String,
        method: String = "GET",
        parameters: [String: Any]? = nil,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        guard let url = URL(string: endpoint) else {
            completion(.failure(NSError(domain: "Invalid URL", code: -1)))
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if let parameters = parameters {
            request.httpBody = try? JSONSerialization.data(withJSONObject: parameters)
        }

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }

            guard let data = data else {
                completion(.failure(NSError(domain: "No data", code: -1)))
                return
            }

            do {
                let decoder = JSONDecoder()
                decoder.dateDecodingStrategy = .iso8601
                let result = try decoder.decode(T.self, from: data)
                completion(.success(result))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }

    // MARK: - API Endpoints

    func fetchPositions(completion: @escaping (Result<[PositionCategory], Error>) -> Void) {
        struct Response: Codable {
            let categories: [PositionCategory]
        }
        request(Constants.API.positions) { (result: Result<Response, Error>) in
            switch result {
            case .success(let response):
                completion(.success(response.categories))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }

    func fetchInterviewerStyles(round: String?, completion: @escaping (Result<[InterviewerStyle], Error>) -> Void) {
        var endpoint = Constants.API.interviewerStyles
        if let round = round {
            endpoint += "?round=\(round)"
        }
        struct Response: Codable {
            let styles: [InterviewerStyle]
            let recommended: String?
        }
        request(endpoint) { (result: Result<Response, Error>) in
            switch result {
            case .success(let response):
                completion(.success(response.styles))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }

    func startInterview(
        request: InterviewStartRequest,
        completion: @escaping (Result<InterviewStartResponse, Error>) -> Void
    ) {
        let parameters = try? JSONEncoder().encode(request)
        let dict = try? JSONSerialization.jsonObject(with: parameters!, options: []) as? [String: Any]

        self.request(Constants.API.startInterview, method: "POST", parameters: dict, completion: completion)
    }

    func submitAnswer(
        request: AnswerRequest,
        completion: @escaping (Result<AnswerResponse, Error>) -> Void
    ) {
        let parameters = try? JSONEncoder().encode(request)
        let dict = try? JSONSerialization.jsonObject(with: parameters!, options: []) as? [String: Any]

        self.request(Constants.API.answer, method: "POST", parameters: dict, completion: completion)
    }

    func fetchReport(sessionId: String, completion: @escaping (Result<InterviewReport, Error>) -> Void) {
        let endpoint = "\(Constants.API.report)/\(sessionId)"
        request(endpoint, completion: completion)
    }
}
```

#### AudioService.swift
```swift
import AVFoundation

class AudioService: NSObject {
    static let shared = AudioService()

    private var audioRecorder: AVAudioRecorder?
    private var audioPlayer: AVAudioPlayer?

    private override init() {
        super.init()
        setupAudioSession()
    }

    // MARK: - Setup

    private func setupAudioSession() {
        let session = AVAudioSession.sharedInstance()
        do {
            try session.setCategory(.playAndRecord, mode: .default, options: [.defaultToSpeaker, .allowBluetooth])
            try session.setActive(true)
        } catch {
            print("❌ 音频会话设置失败: \(error)")
        }
    }

    // MARK: - Microphone Permission

    func requestMicrophonePermission(completion: @escaping (Bool) -> Void) {
        AVAudioSession.sharedInstance().requestRecordPermission { granted in
            DispatchQueue.main.async {
                completion(granted)
            }
        }
    }

    // MARK: - Recording

    func startRecording(completion: @escaping (URL?) -> Void) {
        let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let audioFilename = documentsPath.appendingPathComponent("recording_\(Date().timeIntervalSince1970).m4a")

        let settings = [
            AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
            AVSampleRateKey: 44100,
            AVNumberOfChannelsKey: 1,
            AVEncoderAudioQualityKey: AVAudioQuality.high.rawValue
        ]

        do {
            audioRecorder = try AVAudioRecorder(url: audioFilename, settings: settings)
            audioRecorder?.record()
            completion(audioFilename)
        } catch {
            print("❌ 录音失败: \(error)")
            completion(nil)
        }
    }

    func stopRecording() -> URL? {
        audioRecorder?.stop()
        return audioRecorder?.url
    }

    // MARK: - Playback

    func play(url: URL, completion: @escaping () -> Void) {
        do {
            audioPlayer = try AVAudioPlayer(contentsOf: url)
            audioPlayer?.play()
            DispatchQueue.main.asyncAfter(deadline: .now() + (audioPlayer?.duration ?? 0)) {
                completion()
            }
        } catch {
            print("❌ 播放失败: \(error)")
            completion()
        }
    }

    func stopPlaying() {
        audioPlayer?.stop()
    }
}
```

#### AuthService.swift
```swift
import Foundation
import Combine

class AuthService: ObservableObject {
    @Published var currentUser: User?
    @Published var isLoggedIn = false

    func checkLoginStatus() {
        // 从本地读取用户信息
        if let userData = UserDefaults.standard.data(forKey: Constants.StorageKey.userInfo),
           let user = try? JSONDecoder().decode(User.self, from: userData) {
            self.currentUser = user
            self.isLoggedIn = true
        }
    }

    func login(userId: String, completion: @escaping (Result<User, Error>) -> Void) {
        // iOS版本可以使用Apple登录或其他方式
        // 这里简化为直接创建用户
        let user = User(
            userId: userId,
            openid: nil,
            nickname: "iOS用户",
            avatar: nil,
            isVip: false,
            vipExpireDate: nil,
            freeCountToday: Constants.Business.freeDailyLimit,
            createdAt: Date()
        )

        saveUser(user)
        self.currentUser = user
        self.isLoggedIn = true
        completion(.success(user))
    }

    func logout() {
        UserDefaults.standard.removeObject(forKey: Constants.StorageKey.userInfo)
        self.currentUser = nil
        self.isLoggedIn = false
    }

    private func saveUser(_ user: User) {
        if let data = try? JSONEncoder().encode(user) {
            UserDefaults.standard.set(data, forKey: Constants.StorageKey.userInfo)
        }
    }
}
```

---

### 3. 视图模型层 (ViewModels/)

所有ViewModel都应继承 `ObservableObject`,使用 `@Published` 属性以支持SwiftUI响应式更新。

#### IndexViewModel.swift
```swift
import Foundation
import Combine

class IndexViewModel: ObservableObject {
    @Published var categories: [PositionCategory] = []
    @Published var interviewerStyles: [InterviewerStyle] = []
    @Published var selectedPosition: Position?
    @Published var selectedRound: String = "技术一面"
    @Published var selectedStyle: InterviewerStyle?
    @Published var isLoading = false
    @Published var errorMessage: String?

    let rounds = ["HR面", "技术一面", "技术二面", "技术三面", "总监面", "终面"]

    func loadData() {
        isLoading = true
        fetchPositions()
        fetchInterviewerStyles()
    }

    private func fetchPositions() {
        APIService.shared.fetchPositions { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                switch result {
                case .success(let categories):
                    self?.categories = categories
                case .failure(let error):
                    self?.errorMessage = "加载岗位失败: \(error.localizedDescription)"
                }
            }
        }
    }

    private func fetchInterviewerStyles() {
        APIService.shared.fetchInterviewerStyles(round: selectedRound) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let styles):
                    self?.interviewerStyles = styles
                case .failure(let error):
                    print("加载面试官风格失败: \(error)")
                }
            }
        }
    }

    func canStartInterview() -> Bool {
        return selectedPosition != nil
    }
}
```

---

### 4. 视图层 (Views/)

#### IndexView.swift - 首页
```swift
import SwiftUI

struct IndexView: View {
    @StateObject private var viewModel = IndexViewModel()
    @State private var showPrepare = false

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // 顶部标题
                    headerView

                    // 岗位选择
                    positionSelectionView

                    // 面试轮次选择
                    roundSelectionView

                    // 面试官风格选择
                    styleSelectionView

                    // 开始按钮
                    startButtonView

                    Spacer()
                }
                .padding()
            }
            .navigationTitle("AI面试练习")
            .navigationBarTitleDisplayMode(.inline)
            .onAppear {
                viewModel.loadData()
            }
            .loadingOverlay(isLoading: viewModel.isLoading)
            .sheet(isPresented: $showPrepare) {
                PrepareView(
                    position: viewModel.selectedPosition!,
                    round: viewModel.selectedRound,
                    style: viewModel.selectedStyle
                )
            }
        }
    }

    // MARK: - Subviews

    private var headerView: some View {
        VStack(spacing: 10) {
            Text("🎯 开始你的面试之旅")
                .font(.title)
                .fontWeight(.bold)
            Text("选择岗位和面试轮次，开始模拟面试")
                .font(.subheadline)
                .foregroundColor(.gray)
        }
        .frame(maxWidth: .infinity)
        .padding()
    }

    private var positionSelectionView: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("选择岗位")
                .font(.headline)

            if viewModel.selectedPosition == nil {
                Button(action: {
                    // 显示岗位选择器
                }) {
                    HStack {
                        Text("点击选择岗位")
                            .foregroundColor(.gray)
                        Spacer()
                        Image(systemName: "chevron.right")
                            .foregroundColor(.gray)
                    }
                    .padding()
                    .cardStyle()
                }
            } else {
                HStack {
                    VStack(alignment: .leading) {
                        Text(viewModel.selectedPosition!.name)
                            .font(.body)
                            .fontWeight(.medium)
                        Text(viewModel.selectedPosition!.description)
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                    Spacer()
                    Button("更换") {
                        viewModel.selectedPosition = nil
                    }
                    .font(.caption)
                }
                .padding()
                .cardStyle()
            }
        }
    }

    private var roundSelectionView: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("面试轮次")
                .font(.headline)

            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    ForEach(viewModel.rounds, id: \.self) { round in
                        Button(action: {
                            viewModel.selectedRound = round
                        }) {
                            Text(round)
                                .padding(.horizontal, 16)
                                .padding(.vertical, 8)
                                .background(viewModel.selectedRound == round ? Color.primaryColor : Color.gray.opacity(0.1))
                                .foregroundColor(viewModel.selectedRound == round ? .white : .primary)
                                .cornerRadius(20)
                        }
                    }
                }
            }
        }
    }

    private var styleSelectionView: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("面试官风格(可选)")
                .font(.headline)

            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 12) {
                ForEach(viewModel.interviewerStyles) { style in
                    Button(action: {
                        viewModel.selectedStyle = style
                    }) {
                        VStack {
                            Text(style.icon)
                                .font(.largeTitle)
                            Text(style.name)
                                .font(.caption)
                                .fontWeight(.medium)
                            Text(style.description)
                                .font(.caption2)
                                .foregroundColor(.gray)
                                .multilineTextAlignment(.center)
                        }
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(viewModel.selectedStyle?.id == style.id ? Color.primaryColor.opacity(0.1) : Color.gray.opacity(0.05))
                        .cornerRadius(12)
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(viewModel.selectedStyle?.id == style.id ? Color.primaryColor : Color.clear, lineWidth: 2)
                        )
                    }
                    .buttonStyle(PlainButtonStyle())
                }
            }
        }
    }

    private var startButtonView: some View {
        Button(action: {
            if viewModel.canStartInterview() {
                showPrepare = true
            }
        }) {
            Text("开始面试")
                .font(.headline)
                .primaryButtonStyle()
        }
        .disabled(!viewModel.canStartInterview())
        .opacity(viewModel.canStartInterview() ? 1.0 : 0.5)
    }
}
```

---

### 5. 通用组件 (Views/Components/)

#### LoadingView.swift
```swift
import SwiftUI

struct LoadingView: View {
    var body: some View {
        ZStack {
            Color.black.opacity(0.3)
                .edgesIgnoringSafeArea(.all)

            VStack(spacing: 20) {
                ProgressView()
                    .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    .scaleEffect(1.5)

                Text("加载中...")
                    .font(.caption)
                    .foregroundColor(.white)
            }
            .padding(30)
            .background(Color.black.opacity(0.7))
            .cornerRadius(12)
        }
    }
}
```

---

## 🎯 实现步骤建议

### 第1阶段: 基础框架(1-2天)
1. ✅ 创建Xcode项目
2. ✅ 配置Info.plist权限
3. ✅ 实现Constants和Extensions
4. ✅ 实现所有Model层
5. ✅ 实现Service层(APIService, AudioService, AuthService)

### 第2阶段: 核心功能(3-4天)
6. 实现IndexView + IndexViewModel
7. 实现PrepareView + PrepareViewModel
8. 实现InterviewView + InterviewViewModel (最复杂)
9. 实现ReportView + ReportViewModel

### 第3阶段: 附加功能(2-3天)
10. 实现ProfileView + ProfileViewModel
11. 实现HistoryView + HistoryViewModel
12. 实现VIPView + VIPViewModel
13. 实现Apple In-App Purchase(可选)

### 第4阶段: 优化与测试(2-3天)
14. UI优化和动画
15. 错误处理和边界情况
16. 性能优化
17. 测试和修复Bug

**总计预估**: 8-12天完成基础版本

---

## 📝 开发注意事项

### 1. Xcode项目配置
- Bundle Identifier: `com.yourcompany.aiinterview`
- Deployment Target: iOS 15.0+
- 签名: 选择你的Team

### 2. Info.plist配置
```xml
<key>NSMicrophoneUsageDescription</key>
<string>需要使用麦克风进行语音面试</string>

<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

### 3. 关键技术点
- **SwiftUI**: 所有UI使用SwiftUI构建
- **Combine**: 响应式数据流
- **MVVM架构**: 视图和逻辑分离
- **URLSession**: 网络请求
- **AVFoundation**: 音频录制和播放
- **Codable**: JSON序列化

### 4. 与小程序的对应关系
| 小程序 | iOS | 说明 |
|-------|-----|------|
| pages/index/index.js | IndexViewModel.swift | 首页逻辑 |
| pages/index/index.wxml | IndexView.swift | 首页UI |
| app.json的tabBar | ContentView.swift | 底部导航 |
| wx.request() | APIService.request() | 网络请求 |
| wx.getRecorderManager() | AudioService | 录音功能 |

---

## 🔗 相关资源

- [完整README](./README.md)
- [SwiftUI官方教程](https://developer.apple.com/tutorials/swiftui)
- [小程序源码](../miniprogram/)

---

**创建日期**: 2025-01-13
**维护者**: AI面试系统开发团队
