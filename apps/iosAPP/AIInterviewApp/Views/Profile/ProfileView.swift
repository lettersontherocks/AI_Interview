// ProfileView.swift
// 个人中心视图
//
// 对应小程序: pages/profile/profile.wxml

import SwiftUI

struct ProfileView: View {
    @EnvironmentObject var authService: AuthService
    @StateObject private var viewModel: ProfileViewModel
    @State private var showingVIPView = false
    @State private var showingHistoryView = false
    @State private var showingSettingsView = false

    init() {
        // 会在onAppear中初始化authService
        _viewModel = StateObject(wrappedValue: ProfileViewModel(authService: AuthService()))
    }

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // 用户信息卡片
                    userInfoCard

                    // VIP卡片
                    vipCard

                    // 功能列表
                    menuList

                    // 登出按钮
                    if authService.isLoggedIn {
                        logoutButton
                    }
                }
                .padding()
            }
            .navigationTitle("我的")
            .navigationBarTitleDisplayMode(.large)
            .refreshable {
                viewModel.refreshUserInfo()
            }
            .sheet(isPresented: $showingVIPView) {
                VIPView()
            }
            .sheet(isPresented: $showingHistoryView) {
                if let userId = viewModel.user?.userId {
                    HistoryView(userId: userId)
                }
            }
            .alert("提示", isPresented: $viewModel.showingLogoutAlert) {
                Button("取消", role: .cancel) {}
                Button("确认登出", role: .destructive) {
                    viewModel.logout()
                }
            } message: {
                Text("确定要登出吗?")
            }
        }
        .onAppear {
            // 传递正确的authService
            viewModel.authService = authService
        }
    }

    // MARK: - User Info Card

    private var userInfoCard: some View {
        HStack(spacing: 16) {
            // 头像
            if let user = viewModel.user {
                AsyncImage(url: URL(string: user.avatar ?? "")) { image in
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                } placeholder: {
                    Image(systemName: "person.circle.fill")
                        .resizable()
                        .foregroundColor(.gray)
                }
                .frame(width: 70, height: 70)
                .clipShape(Circle())
                .overlay(
                    Circle()
                        .stroke(Color.primaryColor, lineWidth: 2)
                )

                VStack(alignment: .leading, spacing: 8) {
                    // 昵称
                    Text(user.nickname ?? "用户")
                        .font(.title3)
                        .fontWeight(.semibold)

                    // VIP状态
                    HStack {
                        if viewModel.isVip {
                            HStack(spacing: 4) {
                                Image(systemName: "crown.fill")
                                    .foregroundColor(.orange)
                                    .font(.caption)
                                Text(viewModel.vipStatusText)
                                    .font(.caption)
                                    .foregroundColor(.orange)
                            }
                            .padding(.horizontal, 10)
                            .padding(.vertical, 4)
                            .background(Color.orange.opacity(0.2))
                            .cornerRadius(12)
                        } else {
                            Text(viewModel.vipStatusText)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }

                    // 免费次数
                    if !viewModel.isVip {
                        Text(viewModel.freeCountText)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }

                Spacer()

                // 刷新按钮
                Button(action: {
                    viewModel.refreshUserInfo()
                }) {
                    Image(systemName: "arrow.clockwise")
                        .foregroundColor(.primaryColor)
                        .font(.title3)
                }
            } else {
                // 未登录状态
                Image(systemName: "person.circle.fill")
                    .resizable()
                    .foregroundColor(.gray)
                    .frame(width: 70, height: 70)

                VStack(alignment: .leading, spacing: 8) {
                    Text("未登录")
                        .font(.title3)
                        .fontWeight(.semibold)
                    Text("点击登录")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Spacer()
            }
        }
        .padding()
        .cardStyle()
    }

    // MARK: - VIP Card

    private var vipCard: some View {
        Button(action: {
            showingVIPView = true
        }) {
            HStack {
                VStack(alignment: .leading, spacing: 8) {
                    HStack(spacing: 6) {
                        Image(systemName: "crown.fill")
                            .foregroundColor(.orange)
                        Text("开通VIP会员")
                            .font(.headline)
                            .foregroundColor(.primary)
                    }

                    Text("无限面试次数 · 专属报告 · 优先客服")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Spacer()

                Image(systemName: "chevron.right")
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(
                LinearGradient(
                    gradient: Gradient(colors: [
                        Color.orange.opacity(0.15),
                        Color.orange.opacity(0.05)
                    ]),
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .cornerRadius(12)
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(Color.orange.opacity(0.3), lineWidth: 1)
            )
        }
    }

    // MARK: - Menu List

    private var menuList: some View {
        VStack(spacing: 0) {
            menuItem(
                icon: "clock.arrow.circlepath",
                title: "面试历史",
                color: .blue,
                action: {
                    showingHistoryView = true
                }
            )

            Divider()
                .padding(.leading, 56)

            menuItem(
                icon: "chart.bar.fill",
                title: "学习报告",
                color: .green,
                action: {
                    print("📊 [Profile] 学习报告")
                }
            )

            Divider()
                .padding(.leading, 56)

            menuItem(
                icon: "bookmark.fill",
                title: "收藏夹",
                color: .orange,
                action: {
                    print("⭐️ [Profile] 收藏夹")
                }
            )

            Divider()
                .padding(.leading, 56)

            menuItem(
                icon: "gearshape.fill",
                title: "设置",
                color: .gray,
                action: {
                    showingSettingsView = true
                }
            )
        }
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.05), radius: 4, x: 0, y: 2)
    }

    private func menuItem(icon: String, title: String, color: Color, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            HStack(spacing: 16) {
                Image(systemName: icon)
                    .foregroundColor(color)
                    .font(.title3)
                    .frame(width: 24)

                Text(title)
                    .font(.body)
                    .foregroundColor(.primary)

                Spacer()

                Image(systemName: "chevron.right")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding()
        }
    }

    // MARK: - Logout Button

    private var logoutButton: some View {
        Button(action: {
            viewModel.showingLogoutAlert = true
        }) {
            Text("退出登录")
                .font(.body)
                .foregroundColor(.red)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 14)
                .background(Color.white)
                .cornerRadius(12)
                .shadow(color: Color.black.opacity(0.05), radius: 4, x: 0, y: 2)
        }
    }
}

// MARK: - Preview

struct ProfileView_Previews: PreviewProvider {
    static var previews: some View {
        ProfileView()
            .environmentObject(AuthService())
    }
}
