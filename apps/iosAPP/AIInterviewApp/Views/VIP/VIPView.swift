// VIPView.swift
// VIP页面视图
//
// 对应小程序: pages/vip/vip.wxml

import SwiftUI

struct VIPView: View {
    @StateObject private var viewModel = VIPViewModel()
    @Environment(\.dismiss) var dismiss
    @State private var showingPaymentSheet = false

    var body: some View {
        NavigationView {
            ZStack {
                // 背景渐变
                LinearGradient(
                    gradient: Gradient(colors: [
                        Color.orange.opacity(0.15),
                        Color.white
                    ]),
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()

                ScrollView {
                    VStack(spacing: 24) {
                        // 顶部特权展示
                        privilegesSection

                        // 套餐选择
                        plansSection

                        // 支付按钮
                        purchaseButton

                        // 恢复购买按钮
                        restoreButton

                        // 说明文字
                        disclaimerText
                    }
                    .padding()
                }

                if viewModel.isLoading {
                    LoadingView()
                }
            }
            .navigationTitle("VIP会员")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("关闭") {
                        dismiss()
                    }
                }
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
        }
    }

    // MARK: - Privileges Section

    private var privilegesSection: some View {
        VStack(spacing: 20) {
            // 皇冠图标
            Image(systemName: "crown.fill")
                .font(.system(size: 60))
                .foregroundColor(.orange)
                .shadow(color: .orange.opacity(0.3), radius: 10, x: 0, y: 5)

            Text("解锁全部功能")
                .font(.title)
                .fontWeight(.bold)

            Text("成为VIP会员,享受专属特权")
                .font(.subheadline)
                .foregroundColor(.secondary)

            // 特权列表
            VStack(spacing: 16) {
                privilegeItem(
                    icon: "infinity",
                    title: "无限次面试",
                    description: "不限次数,随时练习"
                )

                privilegeItem(
                    icon: "star.fill",
                    title: "所有岗位开放",
                    description: "覆盖全行业岗位"
                )

                privilegeItem(
                    icon: "person.2.fill",
                    title: "所有面试官风格",
                    description: "体验不同面试场景"
                )

                privilegeItem(
                    icon: "chart.bar.fill",
                    title: "专属报告分析",
                    description: "深度解析你的表现"
                )

                privilegeItem(
                    icon: "headphones",
                    title: "优先客服支持",
                    description: "专属客服快速响应"
                )
            }
            .padding()
            .background(Color.white)
            .cornerRadius(16)
        }
    }

    private func privilegeItem(icon: String, title: String, description: String) -> some View {
        HStack(spacing: 16) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(.orange)
                .frame(width: 32)

            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.body)
                    .fontWeight(.semibold)

                Text(description)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            Spacer()

            Image(systemName: "checkmark.circle.fill")
                .foregroundColor(.green)
        }
    }

    // MARK: - Plans Section

    private var plansSection: some View {
        VStack(spacing: 16) {
            Text("选择套餐")
                .font(.headline)
                .frame(maxWidth: .infinity, alignment: .leading)

            VStack(spacing: 12) {
                ForEach(viewModel.plans) { plan in
                    planCard(plan: plan)
                }
            }
        }
    }

    private func planCard(plan: VIPViewModel.VIPPlan) -> some View {
        Button(action: {
            viewModel.selectPlan(plan)
        }) {
            VStack(alignment: .leading, spacing: 12) {
                // 头部
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        HStack {
                            Text(plan.name)
                                .font(.headline)
                                .foregroundColor(.primary)

                            if plan.isRecommended {
                                Text("推荐")
                                    .font(.caption2)
                                    .fontWeight(.bold)
                                    .foregroundColor(.white)
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 2)
                                    .background(Color.orange)
                                    .cornerRadius(8)
                            }
                        }

                        Text(plan.duration)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }

                    Spacer()

                    // 价格
                    VStack(alignment: .trailing, spacing: 2) {
                        if let originalPrice = plan.originalPrice {
                            Text("¥\(String(format: "%.2f", originalPrice))")
                                .font(.caption)
                                .foregroundColor(.secondary)
                                .strikethrough()
                        }

                        HStack(alignment: .firstTextBaseline, spacing: 2) {
                            Text("¥")
                                .font(.body)
                                .fontWeight(.bold)
                                .foregroundColor(.orange)

                            Text(String(format: "%.2f", plan.price))
                                .font(.title2)
                                .fontWeight(.bold)
                                .foregroundColor(.orange)
                        }
                    }
                }

                // 折扣标签
                if let discount = plan.discount {
                    Text("立省\(discount)%")
                        .font(.caption)
                        .fontWeight(.semibold)
                        .foregroundColor(.red)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.red.opacity(0.1))
                        .cornerRadius(8)
                }

                Divider()

                // 特权列表
                VStack(alignment: .leading, spacing: 6) {
                    ForEach(plan.features, id: \.self) { feature in
                        HStack(spacing: 8) {
                            Image(systemName: "checkmark.circle.fill")
                                .font(.caption)
                                .foregroundColor(.green)

                            Text(feature)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                }
            }
            .padding()
            .background(
                viewModel.selectedPlan?.id == plan.id ?
                Color.orange.opacity(0.1) : Color.white
            )
            .overlay(
                RoundedRectangle(cornerRadius: 16)
                    .stroke(
                        viewModel.selectedPlan?.id == plan.id ?
                        Color.orange : Color.gray.opacity(0.2),
                        lineWidth: viewModel.selectedPlan?.id == plan.id ? 2 : 1
                    )
            )
            .cornerRadius(16)
            .shadow(
                color: viewModel.selectedPlan?.id == plan.id ?
                Color.orange.opacity(0.2) : Color.clear,
                radius: 8, x: 0, y: 4
            )
        }
    }

    // MARK: - Purchase Button

    private var purchaseButton: some View {
        Button(action: {
            viewModel.purchase()
        }) {
            HStack {
                Image(systemName: "crown.fill")
                    .font(.system(size: 20))

                if let plan = viewModel.selectedPlan {
                    Text("立即开通 - ¥\(String(format: "%.2f", plan.price))")
                        .font(.headline)
                } else {
                    Text("请先选择套餐")
                        .font(.headline)
                }
            }
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 16)
            .background(
                viewModel.selectedPlan != nil ?
                LinearGradient(
                    gradient: Gradient(colors: [
                        Color.orange,
                        Color.orange.opacity(0.8)
                    ]),
                    startPoint: .leading,
                    endPoint: .trailing
                ) :
                LinearGradient(
                    gradient: Gradient(colors: [Color.gray, Color.gray]),
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .cornerRadius(12)
            .shadow(
                color: viewModel.selectedPlan != nil ?
                Color.orange.opacity(0.3) : Color.clear,
                radius: 8, x: 0, y: 4
            )
        }
        .disabled(viewModel.selectedPlan == nil)
    }

    // MARK: - Restore Button

    private var restoreButton: some View {
        Button(action: {
            viewModel.restorePurchase()
        }) {
            Text("恢复购买")
                .font(.body)
                .foregroundColor(.primaryColor)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 14)
                .background(Color.primaryColor.opacity(0.1))
                .cornerRadius(10)
        }
    }

    // MARK: - Disclaimer

    private var disclaimerText: some View {
        VStack(spacing: 8) {
            Text("购买说明")
                .font(.caption)
                .fontWeight(.semibold)
                .foregroundColor(.secondary)
                .frame(maxWidth: .infinity, alignment: .leading)

            VStack(alignment: .leading, spacing: 4) {
                Text("• 购买成功后立即生效")
                Text("• 可随时取消自动续订")
                Text("• 支持恢复之前的购买")
                Text("• 如有问题请联系客服")
            }
            .font(.caption2)
            .foregroundColor(.secondary)
            .frame(maxWidth: .infinity, alignment: .leading)
        }
        .padding()
        .background(Color.gray.opacity(0.05))
        .cornerRadius(8)
    }
}

// MARK: - Preview

struct VIPView_Previews: PreviewProvider {
    static var previews: some View {
        VIPView()
    }
}
