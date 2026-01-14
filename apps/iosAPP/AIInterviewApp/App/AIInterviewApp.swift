// AIInterviewApp.swift
// AI面试练习 iOS应用入口
//
// 对应小程序: app.js

import SwiftUI

@main
struct AIInterviewApp: App {
    // 应用状态管理
    @StateObject private var authService = AuthService()

    init() {
        // 配置全局外观
        setupAppearance()
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(authService)
                .onAppear {
                    // 应用启动时初始化
                    initializeApp()
                }
        }
    }

    // MARK: - Private Methods

    /// 配置全局外观
    private func setupAppearance() {
        // 配置导航栏外观
        let appearance = UINavigationBarAppearance()
        appearance.configureWithOpaqueBackground()
        appearance.backgroundColor = .white
        appearance.titleTextAttributes = [.foregroundColor: UIColor.black]

        UINavigationBar.appearance().standardAppearance = appearance
        UINavigationBar.appearance().scrollEdgeAppearance = appearance

        // 配置TabBar外观
        let tabBarAppearance = UITabBarAppearance()
        tabBarAppearance.configureWithOpaqueBackground()
        tabBarAppearance.backgroundColor = .white

        UITabBar.appearance().standardAppearance = tabBarAppearance
        UITabBar.appearance().scrollEdgeAppearance = tabBarAppearance
    }

    /// 初始化应用
    private func initializeApp() {
        print("🚀 AI面试练习 iOS 应用启动")
        print("📱 版本: \(Constants.version)")
        print("🌐 后端地址: \(Constants.baseURL)")

        // 检查用户登录状态
        authService.checkLoginStatus()

        // 请求必要权限
        requestPermissions()
    }

    /// 请求必要权限
    private func requestPermissions() {
        // 请求麦克风权限
        AudioService.shared.requestMicrophonePermission { granted in
            if granted {
                print("✅ 麦克风权限已授予")
            } else {
                print("❌ 麦克风权限被拒绝")
            }
        }
    }
}
