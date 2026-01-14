// Extensions.swift
// Swift扩展方法

import SwiftUI

// MARK: - Color Extensions
extension Color {
    /// 主色调
    static let primaryColor = Color(hex: Constants.UI.primaryColorHex)
    /// 辅助色
    static let secondaryColor = Color(hex: Constants.UI.secondaryColorHex)
    /// 成功色
    static let successColor = Color(hex: Constants.UI.successColorHex)
    /// 警告色
    static let warningColor = Color(hex: Constants.UI.warningColorHex)
    /// 错误色
    static let errorColor = Color(hex: Constants.UI.errorColorHex)

    /// 从HEX字符串创建颜色
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (255, 0, 0, 0)
        }

        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue:  Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

// MARK: - View Extensions
extension View {
    /// 自定义圆角
    func cornerRadius(_ radius: CGFloat, corners: UIRectCorner) -> some View {
        clipShape(RoundedCorner(radius: radius, corners: corners))
    }

    /// 卡片样式
    func cardStyle() -> some View {
        self
            .background(Color.white)
            .cornerRadius(Constants.UI.cornerRadius)
            .shadow(color: Color.black.opacity(0.1), radius: Constants.UI.shadowRadius, x: 0, y: 2)
    }

    /// 主按钮样式
    func primaryButtonStyle() -> some View {
        self
            .padding()
            .frame(maxWidth: .infinity)
            .background(
                LinearGradient(
                    gradient: Gradient(colors: [Color.primaryColor, Color.secondaryColor]),
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .foregroundColor(.white)
            .cornerRadius(Constants.UI.cornerRadius)
    }

    /// 加载状态覆盖层
    func loadingOverlay(isLoading: Bool) -> some View {
        ZStack {
            self
            if isLoading {
                LoadingView()
            }
        }
    }
}

// MARK: - String Extensions
extension String {
    /// 去除首尾空格
    var trimmed: String {
        return self.trimmingCharacters(in: .whitespacesAndNewlines)
    }

    /// 是否为空(包括空格)
    var isBlank: Bool {
        return self.trimmed.isEmpty
    }
}

// MARK: - Date Extensions
extension Date {
    /// 格式化为字符串
    func formatted(with format: String = "yyyy-MM-dd HH:mm:ss") -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = format
        return formatter.string(from: self)
    }

    /// 相对时间描述(如"刚刚"、"5分钟前")
    var relativeDescription: String {
        let now = Date()
        let interval = now.timeIntervalSince(self)

        if interval < 60 {
            return "刚刚"
        } else if interval < 3600 {
            return "\(Int(interval / 60))分钟前"
        } else if interval < 86400 {
            return "\(Int(interval / 3600))小时前"
        } else if interval < 2592000 {
            return "\(Int(interval / 86400))天前"
        } else {
            return self.formatted(with: "yyyy-MM-dd")
        }
    }
}

// MARK: - Custom Shapes
/// 自定义圆角形状
struct RoundedCorner: Shape {
    var radius: CGFloat = .infinity
    var corners: UIRectCorner = .allCorners

    func path(in rect: CGRect) -> Path {
        let path = UIBezierPath(
            roundedRect: rect,
            byRoundingCorners: corners,
            cornerRadii: CGSize(width: radius, height: radius)
        )
        return Path(path.cgPath)
    }
}
