// RecordingButton.swift
// 录音按钮组件
//
// 可重用的录音按钮,支持按住录音

import SwiftUI

struct RecordingButton: View {
    let isRecording: Bool
    let onTap: () -> Void

    @State private var scale: CGFloat = 1.0
    @State private var isPressing = false

    var body: some View {
        Button(action: {}) {
            ZStack {
                // 外圈动画
                if isRecording {
                    Circle()
                        .stroke(Color.red.opacity(0.3), lineWidth: 4)
                        .frame(width: 100, height: 100)
                        .scaleEffect(scale)
                        .opacity(2 - scale)
                }

                // 主按钮
                Circle()
                    .fill(
                        LinearGradient(
                            gradient: Gradient(colors: [
                                isRecording ? Color.red : Color.primaryColor,
                                isRecording ? Color.red.opacity(0.7) : Color.primaryColor.opacity(0.7)
                            ]),
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 80, height: 80)
                    .shadow(
                        color: (isRecording ? Color.red : Color.primaryColor).opacity(0.4),
                        radius: isPressing ? 12 : 8,
                        x: 0,
                        y: isPressing ? 6 : 4
                    )
                    .scaleEffect(isPressing ? 0.95 : 1.0)

                // 图标
                Image(systemName: isRecording ? "stop.circle.fill" : "mic.fill")
                    .font(.system(size: 32))
                    .foregroundColor(.white)
            }
        }
        .buttonStyle(RecordingButtonStyle(
            isRecording: isRecording,
            onPressChanged: { pressing in
                isPressing = pressing
                if pressing {
                    onTap()
                }
            }
        ))
        .onAppear {
            if isRecording {
                startPulseAnimation()
            }
        }
        .onChange(of: isRecording) { newValue in
            if newValue {
                startPulseAnimation()
            } else {
                scale = 1.0
            }
        }
    }

    private func startPulseAnimation() {
        withAnimation(
            Animation
                .easeInOut(duration: 1.0)
                .repeatForever(autoreverses: false)
        ) {
            scale = 1.5
        }
    }
}

// MARK: - Button Style

struct RecordingButtonStyle: ButtonStyle {
    let isRecording: Bool
    let onPressChanged: (Bool) -> Void

    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .onChange(of: configuration.isPressed) { isPressed in
                onPressChanged(isPressed)
            }
    }
}

// MARK: - Preview

struct RecordingButton_Previews: PreviewProvider {
    static var previews: some View {
        VStack(spacing: 40) {
            RecordingButton(isRecording: false, onTap: {})
            RecordingButton(isRecording: true, onTap: {})
        }
        .padding()
    }
}
