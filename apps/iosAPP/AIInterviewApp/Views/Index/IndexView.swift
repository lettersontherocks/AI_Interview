// IndexView.swift
// 首页视图
//
// 对应小程序: pages/index/index.wxml

import SwiftUI

struct IndexView: View {
    @StateObject private var viewModel = IndexViewModel()
    @EnvironmentObject var authService: AuthService
    @State private var showingPrepareView = false

    var body: some View {
        NavigationView {
            ZStack {
                if viewModel.isLoading {
                    LoadingView()
                } else if let error = viewModel.errorMessage {
                    ErrorView(message: error) {
                        viewModel.retry()
                    }
                } else {
                    ScrollView {
                        VStack(spacing: 20) {
                            // 顶部用户信息卡片
                            userInfoCard

                            // 岗位选择区域
                            positionSection

                            // 面试轮次选择
                            roundSection

                            // 面试官风格选择
                            styleSection

                            // 开始面试按钮
                            startButton
                        }
                        .padding()
                    }
                }
            }
            .navigationTitle("AI模拟面试")
            .navigationBarTitleDisplayMode(.large)
            .onAppear {
                viewModel.loadData()
            }
            .sheet(isPresented: $showingPrepareView) {
                if let position = viewModel.selectedPosition {
                    PrepareView(
                        position: position,
                        round: viewModel.selectedRound,
                        style: viewModel.selectedStyle
                    )
                }
            }
        }
    }

    // MARK: - User Info Card

    private var userInfoCard: some View {
        HStack {
            // 用户头像
            if let user = authService.currentUser {
                AsyncImage(url: URL(string: user.avatar ?? "")) { image in
                    image
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                } placeholder: {
                    Image(systemName: "person.circle.fill")
                        .resizable()
                        .foregroundColor(.gray)
                }
                .frame(width: 50, height: 50)
                .clipShape(Circle())

                VStack(alignment: .leading, spacing: 4) {
                    Text(user.nickname ?? "用户")
                        .font(.headline)

                    HStack {
                        if user.isVip {
                            Text("VIP会员")
                                .font(.caption)
                                .foregroundColor(.orange)
                                .padding(.horizontal, 8)
                                .padding(.vertical, 2)
                                .background(Color.orange.opacity(0.2))
                                .cornerRadius(4)
                        } else {
                            Text("今日剩余: \(user.freeCountToday)次")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                }

                Spacer()
            }
        }
        .padding()
        .cardStyle()
    }

    // MARK: - Position Section

    private var positionSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("选择岗位")
                .font(.headline)

            if viewModel.categories.isEmpty {
                Text("暂无岗位数据")
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .center)
                    .padding()
            } else {
                ForEach(viewModel.categories) { category in
                    VStack(alignment: .leading, spacing: 8) {
                        // 分类标题
                        HStack {
                            Image(systemName: category.icon)
                                .foregroundColor(.primaryColor)
                            Text(category.name)
                                .font(.subheadline)
                                .fontWeight(.medium)
                        }
                        .padding(.bottom, 4)

                        // 岗位列表
                        LazyVGrid(columns: [
                            GridItem(.flexible()),
                            GridItem(.flexible())
                        ], spacing: 10) {
                            ForEach(category.positions) { position in
                                positionCard(position)
                            }
                        }
                    }
                    .padding()
                    .cardStyle()
                }
            }
        }
    }

    private func positionCard(_ position: Position) -> some View {
        Button(action: {
            viewModel.selectPosition(position)
        }) {
            VStack(alignment: .leading, spacing: 6) {
                Text(position.name)
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.primary)
                    .lineLimit(1)

                if !position.keywords.isEmpty {
                    Text(position.keywords.prefix(2).joined(separator: " · "))
                        .font(.caption2)
                        .foregroundColor(.secondary)
                        .lineLimit(1)
                }
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(.horizontal, 12)
            .padding(.vertical, 10)
            .background(
                viewModel.selectedPosition?.id == position.id ?
                Color.primaryColor.opacity(0.1) : Color.gray.opacity(0.05)
            )
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(
                        viewModel.selectedPosition?.id == position.id ?
                        Color.primaryColor : Color.clear,
                        lineWidth: 2
                    )
            )
            .cornerRadius(8)
        }
    }

    // MARK: - Round Section

    private var roundSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("面试轮次")
                .font(.headline)

            LazyVGrid(columns: [
                GridItem(.flexible()),
                GridItem(.flexible())
            ], spacing: 10) {
                ForEach(viewModel.rounds, id: \.self) { round in
                    roundButton(round)
                }
            }
        }
        .padding()
        .cardStyle()
    }

    private func roundButton(_ round: String) -> some View {
        Button(action: {
            viewModel.selectRound(round)
        }) {
            Text(round)
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(
                    viewModel.selectedRound == round ? .white : .primary
                )
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
                .background(
                    viewModel.selectedRound == round ?
                    Color.primaryColor : Color.gray.opacity(0.1)
                )
                .cornerRadius(8)
        }
    }

    // MARK: - Style Section

    private var styleSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("面试官风格")
                    .font(.headline)
                Text("(可选)")
                    .font(.caption)
                    .foregroundColor(.secondary)
                Spacer()
            }

            if viewModel.interviewerStyles.isEmpty {
                Text("暂无风格数据")
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, alignment: .center)
                    .padding()
            } else {
                LazyVGrid(columns: [
                    GridItem(.flexible()),
                    GridItem(.flexible())
                ], spacing: 10) {
                    ForEach(viewModel.interviewerStyles) { style in
                        styleCard(style)
                    }
                }
            }
        }
        .padding()
        .cardStyle()
    }

    private func styleCard(_ style: InterviewerStyle) -> some View {
        Button(action: {
            viewModel.selectStyle(style)
        }) {
            VStack(spacing: 8) {
                Text(style.icon)
                    .font(.system(size: 32))

                Text(style.name)
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(.primary)
                    .lineLimit(1)

                Text(style.description)
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .lineLimit(2)
                    .multilineTextAlignment(.center)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 12)
            .padding(.horizontal, 8)
            .background(
                viewModel.selectedStyle?.id == style.id ?
                Color.primaryColor.opacity(0.1) : Color.gray.opacity(0.05)
            )
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(
                        viewModel.selectedStyle?.id == style.id ?
                        Color.primaryColor : Color.clear,
                        lineWidth: 2
                    )
            )
            .cornerRadius(12)
        }
    }

    // MARK: - Start Button

    private var startButton: some View {
        Button(action: {
            if viewModel.canStartInterview() {
                showingPrepareView = true
                print("🎯 [Index] 开始面试准备")
            }
        }) {
            HStack {
                Image(systemName: "play.circle.fill")
                    .font(.system(size: 20))
                Text("开始面试")
                    .font(.headline)
            }
            .foregroundColor(.white)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 16)
            .background(
                viewModel.canStartInterview() ?
                Color.primaryColor : Color.gray
            )
            .cornerRadius(12)
            .shadow(
                color: viewModel.canStartInterview() ?
                Color.primaryColor.opacity(0.3) : Color.clear,
                radius: 8, x: 0, y: 4
            )
        }
        .disabled(!viewModel.canStartInterview())
        .padding(.horizontal)
    }
}

// MARK: - Preview

struct IndexView_Previews: PreviewProvider {
    static var previews: some View {
        IndexView()
            .environmentObject(AuthService())
    }
}
