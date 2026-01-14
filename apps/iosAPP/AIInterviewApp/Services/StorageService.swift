// StorageService.swift
// 本地存储服务
//
// 对应小程序: wx.setStorageSync() 和 wx.getStorageSync()

import Foundation

class StorageService {
    static let shared = StorageService()

    private let userDefaults = UserDefaults.standard

    private init() {}

    // MARK: - Generic Storage

    func save<T: Codable>(_ value: T, forKey key: String) {
        if let data = try? JSONEncoder().encode(value) {
            userDefaults.set(data, forKey: key)
            print("💾 [Storage] 保存数据: \(key)")
        }
    }

    func load<T: Codable>(_ type: T.Type, forKey key: String) -> T? {
        guard let data = userDefaults.data(forKey: key) else {
            return nil
        }
        return try? JSONDecoder().decode(type, from: data)
    }

    func remove(forKey key: String) {
        userDefaults.removeObject(forKey: key)
        print("🗑️ [Storage] 删除数据: \(key)")
    }

    func exists(forKey key: String) -> Bool {
        return userDefaults.object(forKey: key) != nil
    }

    // MARK: - Interview Session

    func saveLastSession(_ session: InterviewSession) {
        save(session, forKey: Constants.StorageKey.lastInterviewSession)
    }

    func loadLastSession() -> InterviewSession? {
        return load(InterviewSession.self, forKey: Constants.StorageKey.lastInterviewSession)
    }

    func clearLastSession() {
        remove(forKey: Constants.StorageKey.lastInterviewSession)
    }

    // MARK: - Simple Values

    func saveString(_ value: String, forKey key: String) {
        userDefaults.set(value, forKey: key)
    }

    func loadString(forKey key: String) -> String? {
        return userDefaults.string(forKey: key)
    }

    func saveInt(_ value: Int, forKey key: String) {
        userDefaults.set(value, forKey: key)
    }

    func loadInt(forKey key: String) -> Int? {
        return userDefaults.integer(forKey: key)
    }

    func saveBool(_ value: Bool, forKey key: String) {
        userDefaults.set(value, forKey: key)
    }

    func loadBool(forKey key: String) -> Bool {
        return userDefaults.bool(forKey: key)
    }

    // MARK: - Clear All

    func clearAll() {
        if let bundleID = Bundle.main.bundleIdentifier {
            userDefaults.removePersistentDomain(forName: bundleID)
            print("🗑️ [Storage] 清空所有数据")
        }
    }
}
