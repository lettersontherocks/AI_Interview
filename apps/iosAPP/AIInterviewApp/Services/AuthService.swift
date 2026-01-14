// AuthService.swift
// 认证服务
//
// 对应小程序: wx.login() 和用户信息管理

import Foundation
import Combine

class AuthService: ObservableObject {
    @Published var currentUser: User?
    @Published var isLoggedIn = false

    private let userDefaults = UserDefaults.standard

    init() {
        loadUser()
    }

    // MARK: - User Management

    func checkLoginStatus() {
        loadUser()
    }

    private func loadUser() {
        if let userData = userDefaults.data(forKey: Constants.StorageKey.userInfo),
           let user = try? JSONDecoder().decode(User.self, from: userData) {
            self.currentUser = user
            self.isLoggedIn = true
            print("✅ [Auth] 用户已登录: \(user.nickname)")
        } else {
            self.isLoggedIn = false
            print("ℹ️ [Auth] 用户未登录")
        }
    }

    func login(userId: String, nickname: String, completion: @escaping (Result<User, Error>) -> Void) {
        // iOS版本使用本地用户ID
        // 可以替换为Sign in with Apple等认证方式

        let user = User(
            userId: userId,
            openid: nil,
            nickname: nickname,
            avatar: nil,
            isVip: false,
            vipExpireDate: nil,
            freeCountToday: Constants.Business.freeDailyLimit,
            createdAt: Date()
        )

        saveUser(user)
        self.currentUser = user
        self.isLoggedIn = true
        print("✅ [Auth] 登录成功: \(nickname)")
        completion(.success(user))
    }

    /// 使用Apple登录(可选实现)
    func loginWithApple(completion: @escaping (Result<User, Error>) -> Void) {
        // TODO: 实现Sign in with Apple
        // 这里使用临时用户
        let userId = "user_\(UUID().uuidString.prefix(16))"
        login(userId: userId, nickname: "iOS用户", completion: completion)
    }

    func logout() {
        userDefaults.removeObject(forKey: Constants.StorageKey.userInfo)
        userDefaults.removeObject(forKey: Constants.StorageKey.userToken)
        self.currentUser = nil
        self.isLoggedIn = false
        print("👋 [Auth] 用户已登出")
    }

    private func saveUser(_ user: User) {
        if let data = try? JSONEncoder().encode(user) {
            userDefaults.set(data, forKey: Constants.StorageKey.userInfo)
            userDefaults.set(user.userId, forKey: Constants.StorageKey.userId)
        }
    }

    // MARK: - User Info Update

    func updateUser(_ user: User) {
        saveUser(user)
        self.currentUser = user
        print("✅ [Auth] 用户信息已更新")
    }

    func updateVIPStatus(isVip: Bool, expireDate: Date?) {
        guard var user = currentUser else { return }

        let updatedUser = User(
            userId: user.userId,
            openid: user.openid,
            nickname: user.nickname,
            avatar: user.avatar,
            isVip: isVip,
            vipExpireDate: expireDate,
            freeCountToday: user.freeCountToday,
            createdAt: user.createdAt
        )

        updateUser(updatedUser)
    }

    func decreaseFreeCount() {
        guard var user = currentUser else { return }

        let newCount = max(0, user.freeCountToday - 1)
        let updatedUser = User(
            userId: user.userId,
            openid: user.openid,
            nickname: user.nickname,
            avatar: user.avatar,
            isVip: user.isVip,
            vipExpireDate: user.vipExpireDate,
            freeCountToday: newCount,
            createdAt: user.createdAt
        )

        updateUser(updatedUser)
    }

    // MARK: - Helpers

    func getUserId() -> String? {
        return currentUser?.userId
    }

    func canStartInterview() -> Bool {
        return currentUser?.canStartFreeInterview ?? false
    }
}
