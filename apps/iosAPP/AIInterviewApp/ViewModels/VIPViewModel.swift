// VIPViewModel.swift
// VIP页面视图模型
//
// 对应小程序: pages/vip/vip.js

import Foundation
import Combine
import StoreKit

class VIPViewModel: ObservableObject {
    @Published var selectedPlan: VIPPlan?
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var showingPaymentSheet = false

    struct VIPPlan: Identifiable {
        let id: String
        let name: String
        let duration: String
        let price: Double
        let originalPrice: Double?
        let features: [String]
        let isRecommended: Bool

        var discount: Int? {
            guard let original = originalPrice else { return nil }
            return Int((1 - price / original) * 100)
        }
    }

    let plans: [VIPPlan] = [
        VIPPlan(
            id: "monthly",
            name: "月度会员",
            duration: "1个月",
            price: 9.98,
            originalPrice: nil,
            features: ["无限次面试", "所有岗位", "所有面试官风格"],
            isRecommended: false
        ),
        VIPPlan(
            id: "quarterly",
            name: "季度会员",
            duration: "3个月",
            price: 19.98,
            originalPrice: 29.94,
            features: ["无限次面试", "所有岗位", "所有面试官风格", "优先客服"],
            isRecommended: true
        ),
        VIPPlan(
            id: "yearly",
            name: "年度会员",
            duration: "12个月",
            price: 49.98,
            originalPrice: 119.76,
            features: ["无限次面试", "所有岗位", "所有面试官风格", "优先客服", "专属报告"],
            isRecommended: false
        )
    ]

    // MARK: - Actions

    func selectPlan(_ plan: VIPPlan) {
        self.selectedPlan = plan
        print("💎 [VIP] 选择套餐: \(plan.name) - ¥\(plan.price)")
    }

    func purchase() {
        guard let plan = selectedPlan else {
            errorMessage = "请先选择套餐"
            return
        }

        print("💳 [VIP] 开始购买: \(plan.name)")

        // TODO: 实现Apple In-App Purchase
        // 这里是简化实现
        isLoading = true

        DispatchQueue.main.asyncAfter(deadline: .now() + 2) { [weak self] in
            self?.isLoading = false
            // 模拟购买成功
            print("✅ [VIP] 购买成功")
            self?.showingPaymentSheet = false
        }
    }

    func restorePurchase() {
        print("🔄 [VIP] 恢复购买")

        isLoading = true

        // TODO: 实现恢复购买
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) { [weak self] in
            self?.isLoading = false
            print("✅ [VIP] 恢复购买完成")
        }
    }

    // MARK: - Helpers

    func getPlanById(_ id: String) -> VIPPlan? {
        return plans.first { $0.id == id }
    }
}
