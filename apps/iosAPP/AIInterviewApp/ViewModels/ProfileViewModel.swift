// ProfileViewModel.swift
// 个人中心视图模型
//
// 对应小程序: pages/profile/profile.js

import Foundation
import Combine

class ProfileViewModel: ObservableObject {
    @Published var user: User?
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var showingLogoutAlert = false

    private var authService: AuthService
    private var cancellables = Set<AnyCancellable>()

    init(authService: AuthService) {
        self.authService = authService

        // 监听用户变化
        authService.$currentUser
            .assign(to: &$user)
    }

    // MARK: - Computed Properties

    var isVip: Bool {
        return user?.isVip ?? false
    }

    var vipStatusText: String {
        if isVip {
            if let days = user?.vipRemainingDays {
                return "VIP会员 (剩余\(days)天)"
            }
            return "VIP会员"
        } else {
            return "普通用户"
        }
    }

    var freeCountText: String {
        let count = user?.freeCountToday ?? 0
        return "今日剩余: \(count)次"
    }

    var canStartInterview: Bool {
        return user?.canStartFreeInterview ?? false
    }

    // MARK: - Actions

    func refreshUserInfo() {
        guard let userId = user?.userId else { return }

        isLoading = true

        APIService.shared.fetchUserProfile(userId: userId) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                switch result {
                case .success(let userInfo):
                    let user = User(
                        userId: userInfo.userId,
                        openid: userInfo.openid,
                        nickname: userInfo.nickname,
                        avatar: userInfo.avatar,
                        isVip: userInfo.isVip,
                        vipExpireDate: userInfo.vipExpireDate,
                        freeCountToday: userInfo.freeCountToday,
                        createdAt: userInfo.createdAt
                    )
                    self?.authService.updateUser(user)
                    print("✅ [Profile] 用户信息刷新成功")
                case .failure(let error):
                    self?.errorMessage = "刷新失败: \(error.localizedDescription)"
                    print("❌ [Profile] 刷新用户信息失败: \(error)")
                }
            }
        }
    }

    func logout() {
        authService.logout()
        print("👋 [Profile] 用户登出")
    }

    // MARK: - Navigation

    func navigateToVIP() {
        // 导航到VIP页面
        print("💎 [Profile] 导航到VIP页面")
    }

    func navigateToHistory() {
        // 导航到历史记录
        print("📚 [Profile] 导航到历史记录")
    }

    func navigateToSettings() {
        // 导航到设置页面
        print("⚙️ [Profile] 导航到设置")
    }
}
