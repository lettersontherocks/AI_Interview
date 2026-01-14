// ContentView.swift
// 主容器视图 - 管理TabBar导航
//
// 对应小程序: app.json 的 tabBar 配置

import SwiftUI

struct ContentView: View {
    @EnvironmentObject var authService: AuthService
    @State private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            // 首页
            IndexView()
                .tabItem {
                    Label("首页", systemImage: selectedTab == 0 ? "house.fill" : "house")
                }
                .tag(0)

            // 个人中心
            ProfileView()
                .tabItem {
                    Label("我的", systemImage: selectedTab == 1 ? "person.fill" : "person")
                }
                .tag(1)
        }
        .accentColor(Color.primaryColor)
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
            .environmentObject(AuthService())
    }
}
