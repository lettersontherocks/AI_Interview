// ScoreRadarChart.swift
// 雷达图组件
//
// 用于显示五维能力评分

import SwiftUI

struct ScoreRadarChart: View {
    let technicalSkill: Double
    let communication: Double
    let logicThinking: Double
    let problemSolving: Double
    let projectExperience: Double

    private let labels = ["技术能力", "沟通表达", "逻辑思维", "问题解决", "项目经验"]

    var body: some View {
        GeometryReader { geometry in
            let center = CGPoint(x: geometry.size.width / 2, y: geometry.size.height / 2)
            let radius = min(geometry.size.width, geometry.size.height) / 2.5

            ZStack {
                // 背景网格
                radarGrid(center: center, radius: radius)

                // 数据区域
                radarDataPath(center: center, radius: radius)
                    .fill(Color.primaryColor.opacity(0.3))
                    .overlay(
                        radarDataPath(center: center, radius: radius)
                            .stroke(Color.primaryColor, lineWidth: 2)
                    )

                // 数据点
                radarDataPoints(center: center, radius: radius)

                // 标签
                radarLabels(center: center, radius: radius)
            }
        }
    }

    // MARK: - Grid

    private func radarGrid(center: CGPoint, radius: CGFloat) -> some View {
        ZStack {
            // 同心圆网格
            ForEach(1..<6) { i in
                let gridRadius = radius * CGFloat(i) / 5
                radarPolygonPath(center: center, radius: gridRadius)
                    .stroke(Color.gray.opacity(0.2), lineWidth: 1)
            }

            // 辐射线
            ForEach(0..<5) { i in
                let angle = angleForIndex(i)
                Path { path in
                    path.move(to: center)
                    path.addLine(to: pointOnCircle(center: center, radius: radius, angle: angle))
                }
                .stroke(Color.gray.opacity(0.2), lineWidth: 1)
            }
        }
    }

    // MARK: - Data Path

    private func radarDataPath(center: CGPoint, radius: CGFloat) -> Path {
        let scores = [technicalSkill, communication, logicThinking, problemSolving, projectExperience]

        var path = Path()
        for (index, score) in scores.enumerated() {
            let angle = angleForIndex(index)
            let distance = radius * CGFloat(score / 100)
            let point = pointOnCircle(center: center, radius: distance, angle: angle)

            if index == 0 {
                path.move(to: point)
            } else {
                path.addLine(to: point)
            }
        }
        path.closeSubpath()

        return path
    }

    // MARK: - Data Points

    private func radarDataPoints(center: CGPoint, radius: CGFloat) -> some View {
        let scores = [technicalSkill, communication, logicThinking, problemSolving, projectExperience]

        return ForEach(0..<scores.count, id: \.self) { index in
            let score = scores[index]
            let angle = angleForIndex(index)
            let distance = radius * CGFloat(score / 100)
            let point = pointOnCircle(center: center, radius: distance, angle: angle)

            Circle()
                .fill(Color.primaryColor)
                .frame(width: 8, height: 8)
                .position(point)
        }
    }

    // MARK: - Labels

    private func radarLabels(center: CGPoint, radius: CGFloat) -> some View {
        let scores = [technicalSkill, communication, logicThinking, problemSolving, projectExperience]

        return ForEach(0..<labels.count, id: \.self) { index in
            let angle = angleForIndex(index)
            let labelRadius = radius + 30
            let point = pointOnCircle(center: center, radius: labelRadius, angle: angle)

            VStack(spacing: 2) {
                Text(labels[index])
                    .font(.caption)
                    .fontWeight(.medium)
                    .foregroundColor(.primary)

                Text(String(format: "%.1f", scores[index]))
                    .font(.caption2)
                    .foregroundColor(.primaryColor)
            }
            .position(point)
        }
    }

    // MARK: - Helpers

    private func radarPolygonPath(center: CGPoint, radius: CGFloat) -> Path {
        var path = Path()
        for i in 0..<5 {
            let angle = angleForIndex(i)
            let point = pointOnCircle(center: center, radius: radius, angle: angle)

            if i == 0 {
                path.move(to: point)
            } else {
                path.addLine(to: point)
            }
        }
        path.closeSubpath()
        return path
    }

    private func angleForIndex(_ index: Int) -> Double {
        // 从顶部开始,顺时针
        let anglePerSection = 2 * Double.pi / 5
        return Double.pi / 2 - Double(index) * anglePerSection - Double.pi // -90度起始
    }

    private func pointOnCircle(center: CGPoint, radius: CGFloat, angle: Double) -> CGPoint {
        return CGPoint(
            x: center.x + radius * CGFloat(cos(angle)),
            y: center.y + radius * CGFloat(sin(angle))
        )
    }
}

// MARK: - Preview

struct ScoreRadarChart_Previews: PreviewProvider {
    static var previews: some View {
        VStack {
            ScoreRadarChart(
                technicalSkill: 85,
                communication: 78,
                logicThinking: 90,
                problemSolving: 82,
                projectExperience: 88
            )
            .frame(height: 300)
            .padding()
        }
    }
}
