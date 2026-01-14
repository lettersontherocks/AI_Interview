// IndexViewModel.swift
// 首页视图模型
//
// 对应小程序: pages/index/index.js

import Foundation
import Combine

class IndexViewModel: ObservableObject {
    @Published var categories: [PositionCategory] = []
    @Published var interviewerStyles: [InterviewerStyle] = []
    @Published var selectedPosition: Position?
    @Published var selectedRound: String = "技术一面"
    @Published var selectedStyle: InterviewerStyle?
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var searchText = ""

    let rounds = ["HR面", "技术一面", "技术二面", "技术三面", "总监面", "终面"]

    private var cancellables = Set<AnyCancellable>()

    init() {
        loadData()
    }

    // MARK: - Data Loading

    func loadData() {
        isLoading = true
        errorMessage = nil

        let group = DispatchGroup()

        // 加载岗位
        group.enter()
        fetchPositions {
            group.leave()
        }

        // 加载面试官风格
        group.enter()
        fetchInterviewerStyles {
            group.leave()
        }

        group.notify(queue: .main) {
            self.isLoading = false
        }
    }

    private func fetchPositions(completion: @escaping () -> Void) {
        APIService.shared.fetchPositions { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let categories):
                    self?.categories = categories
                    print("✅ [Index] 加载岗位成功: \(categories.count)个分类")
                case .failure(let error):
                    self?.errorMessage = "加载岗位失败: \(error.localizedDescription)"
                    print("❌ [Index] 加载岗位失败: \(error)")
                }
                completion()
            }
        }
    }

    private func fetchInterviewerStyles(completion: @escaping () -> Void) {
        APIService.shared.fetchInterviewerStyles(round: selectedRound) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let styles):
                    self?.interviewerStyles = styles
                    print("✅ [Index] 加载面试官风格成功: \(styles.count)个")
                case .failure(let error):
                    print("❌ [Index] 加载面试官风格失败: \(error)")
                }
                completion()
            }
        }
    }

    // MARK: - Actions

    func selectPosition(_ position: Position) {
        self.selectedPosition = position
        print("📍 [Index] 选择岗位: \(position.name)")
    }

    func selectRound(_ round: String) {
        self.selectedRound = round
        // 重新加载推荐的面试官风格
        fetchInterviewerStyles {}
        print("🎯 [Index] 选择轮次: \(round)")
    }

    func selectStyle(_ style: InterviewerStyle) {
        self.selectedStyle = style
        print("🎭 [Index] 选择风格: \(style.name)")
    }

    func canStartInterview() -> Bool {
        return selectedPosition != nil
    }

    func clearSelection() {
        selectedPosition = nil
        selectedStyle = nil
    }

    func retry() {
        loadData()
    }

    // MARK: - Search

    func searchPositions() {
        guard !searchText.isEmpty else {
            loadData()
            return
        }

        isLoading = true
        APIService.shared.searchPositions(keyword: searchText) { [weak self] result in
            DispatchQueue.main.async {
                self?.isLoading = false
                switch result {
                case .success(let positions):
                    // 将搜索结果转换为分类格式
                    let category = PositionCategory(
                        id: "search_results",
                        name: "搜索结果",
                        icon: "🔍",
                        positions: positions
                    )
                    self?.categories = [category]
                case .failure(let error):
                    self?.errorMessage = "搜索失败: \(error.localizedDescription)"
                }
            }
        }
    }
}

// PositionCategory扩展，添加初始化方法
extension PositionCategory {
    init(id: String, name: String, icon: String, positions: [Position]) {
        self.id = id
        self.name = name
        self.icon = icon
        self.positions = positions
    }
}
