// User.swift
// 用户数据模型
//
// 对应小程序: pages/profile/profile.js 中的用户信息

import Foundation

/// 用户信息
struct User: Codable {
    let userId: String
    let openid: String?
    let nickname: String
    let avatar: String?
    let isVip: Bool
    let vipExpireDate: Date?
    let freeCountToday: Int
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case openid
        case nickname
        case avatar
        case isVip = "is_vip"
        case vipExpireDate = "vip_expire_date"
        case freeCountToday = "free_count_today"
        case createdAt = "created_at"
    }

    /// 是否可以进行免费面试
    var canStartFreeInterview: Bool {
        return isVip || freeCountToday > 0
    }

    /// VIP剩余天数
    var vipRemainingDays: Int? {
        guard let expireDate = vipExpireDate else { return nil }
        let days = Calendar.current.dateComponents([.day], from: Date(), to: expireDate).day
        return max(0, days ?? 0)
    }
}

/// 用户信息响应
struct UserInfo: Codable {
    let userId: String
    let openid: String?
    let nickname: String
    let avatar: String?
    let isVip: Bool
    let vipExpireDate: Date?
    let freeCountToday: Int
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case openid, nickname, avatar
        case isVip = "is_vip"
        case vipExpireDate = "vip_expire_date"
        case freeCountToday = "free_count_today"
        case createdAt = "created_at"
    }
}
