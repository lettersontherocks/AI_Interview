// HistoryView.swift
// 历史记录视图
//
// 对应小程序: pages/history/history.wxml

import SwiftUI

struct HistoryView: View {
    @StateObject private var viewModel: HistoryViewModel
    @Environment(\.dismiss) var dismiss
    @State private var showingFilterMenu = false
    @State private var selectedItem: InterviewHistoryItem?
    @State private var showingReportView = false

    init(userId: String) {
        _viewModel = StateObject(wrappedValue: HistoryViewModel(userId: userId))
    }

    var body: some View {
        NavigationView {
            ZStack {
                if viewModel.isLoading {
                    LoadingView()
                } else if let error = viewModel.errorMessage {
                    ErrorView(message: error) {
                        viewModel.retry()
                    }
                } else if viewModel.filteredItems.isEmpty {
                    emptyView
                } else {
                    ScrollView {
                        VStack(spacing: 0) {
                            // 筛选和排序栏
                            filterBar

                            // 历史列表
                            LazyVStack(spacing: 12) {
                                ForEach(viewModel.filteredItems) { item in
                                    HistoryListItem(item: item)
                                        .onTapGesture {
                                            selectedItem = item
                                            showingReportView = true
                                        }
                                        .contextMenu {
                                            Button(role: .destructive) {
                                                viewModel.deleteItem(item)
                                            } label: {
                                                Label("删除", systemImage: "trash")
                                            }
                                        }
                                }
                            }
                            .padding()
                        }
                    }
                }
            }
            .navigationTitle("面试历史")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("关闭") {
                        dismiss()
                    }
                }
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        showingFilterMenu.toggle()
                    }) {
                        Image(systemName: "line.3.horizontal.decrease.circle")
                    }
                }
            }
            .refreshable {
                viewModel.loadHistory()
            }
            .sheet(isPresented: $showingReportView) {
                if let item = selectedItem {
                    ReportView(sessionId: item.sessionId)
                }
            }
            .sheet(isPresented: $showingFilterMenu) {
                filterMenuView
                    .presentationDetents([.medium])
            }
        }
    }

    // MARK: - Filter Bar

    private var filterBar: some View {
        VStack(spacing: 12) {
            // 筛选选项
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 10) {
                    ForEach(HistoryViewModel.FilterOption.allCases, id: \.self) { option in
                        filterChip(option: option)
                    }
                }
                .padding(.horizontal)
            }

            // 排序选项
            HStack {
                Image(systemName: "arrow.up.arrow.down")
                    .foregroundColor(.secondary)
                    .font(.caption)

                Text("排序:")
                    .font(.caption)
                    .foregroundColor(.secondary)

                Text(viewModel.sortOption.rawValue)
                    .font(.caption)
                    .fontWeight(.medium)
                    .foregroundColor(.primaryColor)

                Spacer()

                Text("共\(viewModel.filteredItems.count)条记录")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding(.horizontal)

            Divider()
        }
        .padding(.vertical, 8)
        .background(Color.white)
    }

    private func filterChip(option: HistoryViewModel.FilterOption) -> some View {
        Button(action: {
            viewModel.setFilter(option)
        }) {
            Text(option.rawValue)
                .font(.caption)
                .fontWeight(.medium)
                .foregroundColor(
                    viewModel.filterOption == option ? .white : .primary
                )
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(
                    viewModel.filterOption == option ?
                    Color.primaryColor : Color.gray.opacity(0.1)
                )
                .cornerRadius(16)
        }
    }

    // MARK: - Filter Menu

    private var filterMenuView: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: 24) {
                // 筛选选项
                VStack(alignment: .leading, spacing: 12) {
                    Text("筛选")
                        .font(.headline)

                    VStack(spacing: 8) {
                        ForEach(HistoryViewModel.FilterOption.allCases, id: \.self) { option in
                            Button(action: {
                                viewModel.setFilter(option)
                            }) {
                                HStack {
                                    Text(option.rawValue)
                                        .foregroundColor(.primary)

                                    Spacer()

                                    if viewModel.filterOption == option {
                                        Image(systemName: "checkmark")
                                            .foregroundColor(.primaryColor)
                                    }
                                }
                                .padding()
                                .background(
                                    viewModel.filterOption == option ?
                                    Color.primaryColor.opacity(0.1) : Color.clear
                                )
                                .cornerRadius(8)
                            }
                        }
                    }
                }

                // 排序选项
                VStack(alignment: .leading, spacing: 12) {
                    Text("排序")
                        .font(.headline)

                    VStack(spacing: 8) {
                        ForEach(HistoryViewModel.SortOption.allCases, id: \.self) { option in
                            Button(action: {
                                viewModel.setSort(option)
                                showingFilterMenu = false
                            }) {
                                HStack {
                                    Text(option.rawValue)
                                        .foregroundColor(.primary)

                                    Spacer()

                                    if viewModel.sortOption == option {
                                        Image(systemName: "checkmark")
                                            .foregroundColor(.primaryColor)
                                    }
                                }
                                .padding()
                                .background(
                                    viewModel.sortOption == option ?
                                    Color.primaryColor.opacity(0.1) : Color.clear
                                )
                                .cornerRadius(8)
                            }
                        }
                    }
                }

                Spacer()
            }
            .padding()
            .navigationTitle("筛选与排序")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("完成") {
                        showingFilterMenu = false
                    }
                }
            }
        }
    }

    // MARK: - Empty View

    private var emptyView: some View {
        VStack(spacing: 16) {
            Image(systemName: "clock.arrow.circlepath")
                .font(.system(size: 64))
                .foregroundColor(.gray)

            Text("暂无面试记录")
                .font(.headline)
                .foregroundColor(.secondary)

            Text("开始你的第一次AI面试吧")
                .font(.caption)
                .foregroundColor(.secondary)

            Button(action: {
                dismiss()
            }) {
                Text("去面试")
                    .foregroundColor(.white)
                    .padding(.horizontal, 32)
                    .padding(.vertical, 12)
                    .background(Color.primaryColor)
                    .cornerRadius(20)
            }
            .padding(.top)
        }
    }
}

// MARK: - Preview

struct HistoryView_Previews: PreviewProvider {
    static var previews: some View {
        HistoryView(userId: "test-user-id")
    }
}
