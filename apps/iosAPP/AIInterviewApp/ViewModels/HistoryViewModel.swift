// HistoryViewModel.swift
// 历史记录视图模型
//
// 对应小程序: pages/history/history.js

import Foundation
import Combine

class HistoryViewModel: ObservableObject {
    @Published var historyItems: [InterviewHistoryItem] = []
    @Published var filteredItems: [InterviewHistoryItem] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var filterOption: FilterOption = .all
    @Published var sortOption: SortOption = .dateDesc

    enum FilterOption: String, CaseIterable {
        case all = "全部"
        case finished = "已完成"
        case unfinished = "未完成"
    }

    enum SortOption: String, CaseIterable {
        case dateDesc = "最新优先"
        case dateAsc = "最早优先"
        case scoreDesc = "分数最高"
        case scoreAsc = "分数最低"
    }

    let userId: String

    init(userId: String) {
        self.userId = userId
        loadHistory()
    }

    // MARK: - Data Loading

    func loadHistory() {
        isLoading = true
        errorMessage = nil

        print("📚 [History] 加载面试历史: \(userId)")

        APIService.shared.fetchHistory(userId: userId) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                switch result {
                case .success(let items):
                    self?.historyItems = items
                    self?.applyFilter()
                    print("✅ [History] 历史记录加载成功: \(items.count)条")
                case .failure(let error):
                    self?.errorMessage = "加载失败: \(error.localizedDescription)"
                    print("❌ [History] 加载历史失败: \(error)")
                }
            }
        }
    }

    // MARK: - Filter & Sort

    func setFilter(_ option: FilterOption) {
        self.filterOption = option
        applyFilter()
    }

    func setSort(_ option: SortOption) {
        self.sortOption = option
        applyFilter()
    }

    private func applyFilter() {
        // 筛选
        var items = historyItems

        switch filterOption {
        case .all:
            break
        case .finished:
            items = items.filter { $0.isFinished }
        case .unfinished:
            items = items.filter { !$0.isFinished }
        }

        // 排序
        switch sortOption {
        case .dateDesc:
            items.sort { $0.createdAt > $1.createdAt }
        case .dateAsc:
            items.sort { $0.createdAt < $1.createdAt }
        case .scoreDesc:
            items.sort { ($0.totalScore ?? 0) > ($1.totalScore ?? 0) }
        case .scoreAsc:
            items.sort { ($0.totalScore ?? 0) < ($1.totalScore ?? 0) }
        }

        self.filteredItems = items
        print("🔍 [History] 筛选后: \(items.count)条")
    }

    // MARK: - Actions

    func retry() {
        loadHistory()
    }

    func deleteItem(_ item: InterviewHistoryItem) {
        // TODO: 实现删除功能
        print("🗑️ [History] 删除记录: \(item.sessionId)")
    }
}
