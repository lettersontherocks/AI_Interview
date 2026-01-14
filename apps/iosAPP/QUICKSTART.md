# 🚀 iOS项目快速启动指南

5分钟内启动你的iOS项目!

---

## ⚡ 快速开始

### 步骤 1: 用Xcode创建新项目

1. 打开 Xcode
2. File → New → Project
3. 选择 "App" (iOS)
4. 填写项目信息:
   - Product Name: `AIInterviewApp`
   - Team: 选择你的开发Team
   - Organization Identifier: `com.yourcompany`
   - Interface: **SwiftUI**
   - Language: **Swift**
   - 取消勾选 Core Data 和 Tests

5. 保存到: `/Users/yifeihuang/Documents/ClaudeAPIServicePlat/ai_interview/apps/iosAPP/`

### 步骤 2: 复制代码文件

将本目录下的所有 `.swift` 文件复制到 Xcode 项目中:

```bash
# 在Xcode中右键项目 → Add Files to "AIInterviewApp"
# 选择 AIInterviewApp 文件夹 → 勾选 "Copy items if needed" → Add
```

### 步骤 3: 配置 Info.plist

在 Info.plist 中添加:

```xml
<key>NSMicrophoneUsageDescription</key>
<string>需要使用麦克风进行语音面试</string>

<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

### 步骤 4: 配置后端地址

编辑 `Constants.swift`:

```swift
static let baseURL = "http://your-server-ip:8003"
```

### 步骤 5: 运行项目

1. 选择模拟器 (iPhone 15 Pro)
2. 点击 Run (⌘R)
3. 等待编译完成

---

## 📁 文件结构对照

```
Xcode项目结构:
AIInterviewApp/
├── App/
│   ├── AIInterviewApp.swift ✅
│   └── ContentView.swift ✅
├── Utils/
│   ├── Constants.swift ✅
│   └── Extensions.swift ✅
├── Models/ (参考PROJECT_GUIDE.md创建)
├── ViewModels/ (参考PROJECT_GUIDE.md创建)
├── Views/ (参考PROJECT_GUIDE.md创建)
└── Services/ (参考PROJECT_GUIDE.md创建)
```

---

## 🐛 常见问题

### Q1: 编译错误 "Cannot find type 'AuthService'"
**A**: 需要先创建 `Services/AuthService.swift` 文件

### Q2: 网络请求失败
**A**: 检查 Info.plist 的 NSAppTransportSecurity 配置

### Q3: 模拟器无法录音
**A**: 音频功能需要真机测试

---

## 📚 下一步

1. 阅读 [PROJECT_GUIDE.md](./PROJECT_GUIDE.md) 了解完整实现
2. 阅读 [README.md](./README.md) 了解项目架构
3. 参考小程序源码 `../miniprogram/` 理解业务逻辑

---

**需要帮助?** 查看 PROJECT_GUIDE.md 中的完整代码示例!
