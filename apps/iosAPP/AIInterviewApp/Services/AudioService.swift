// AudioService.swift
// 音频录制和播放服务
//
// 对应小程序: wx.getRecorderManager() 和 wx.createInnerAudioContext()

import AVFoundation
import Foundation

class AudioService: NSObject, ObservableObject {
    static let shared = AudioService()

    @Published var isRecording = false
    @Published var isPlaying = false

    private var audioRecorder: AVAudioRecorder?
    private var audioPlayer: AVAudioPlayer?
    private var recordingURL: URL?

    private override init() {
        super.init()
        setupAudioSession()
    }

    // MARK: - Setup

    private func setupAudioSession() {
        let session = AVAudioSession.sharedInstance()
        do {
            try session.setCategory(.playAndRecord, mode: .default, options: [.defaultToSpeaker, .allowBluetooth])
            try session.setActive(true)
            print("✅ [Audio] 音频会话设置成功")
        } catch {
            print("❌ [Audio] 音频会话设置失败: \(error)")
        }
    }

    // MARK: - Microphone Permission

    func requestMicrophonePermission(completion: @escaping (Bool) -> Void) {
        AVAudioSession.sharedInstance().requestRecordPermission { granted in
            DispatchQueue.main.async {
                if granted {
                    print("✅ [Audio] 麦克风权限已授予")
                } else {
                    print("❌ [Audio] 麦克风权限被拒绝")
                }
                completion(granted)
            }
        }
    }

    func checkMicrophonePermission() -> Bool {
        let status = AVAudioSession.sharedInstance().recordPermission
        return status == .granted
    }

    // MARK: - Recording

    func startRecording(completion: @escaping (URL?) -> Void) {
        guard checkMicrophonePermission() else {
            print("❌ [Audio] 没有麦克风权限")
            completion(nil)
            return
        }

        let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let audioFilename = documentsPath.appendingPathComponent("recording_\(Date().timeIntervalSince1970).m4a")

        let settings: [String: Any] = [
            AVFormatIDKey: Int(kAudioFormatMPEG4AAC),
            AVSampleRateKey: 44100,
            AVNumberOfChannelsKey: 1,
            AVEncoderAudioQualityKey: AVAudioQuality.high.rawValue
        ]

        do {
            audioRecorder = try AVAudioRecorder(url: audioFilename, settings: settings)
            audioRecorder?.prepareToRecord()
            let success = audioRecorder?.record() ?? false

            if success {
                self.isRecording = true
                self.recordingURL = audioFilename
                print("🎙️ [Audio] 开始录音: \(audioFilename.lastPathComponent)")
                completion(audioFilename)
            } else {
                print("❌ [Audio] 录音启动失败")
                completion(nil)
            }
        } catch {
            print("❌ [Audio] 录音失败: \(error)")
            completion(nil)
        }
    }

    func stopRecording() -> URL? {
        audioRecorder?.stop()
        self.isRecording = false
        print("⏹️ [Audio] 停止录音")
        return recordingURL
    }

    func cancelRecording() {
        audioRecorder?.stop()
        audioRecorder?.deleteRecording()
        self.isRecording = false
        print("🗑️ [Audio] 取消录音")
    }

    // MARK: - Playback

    func play(url: URL, completion: @escaping () -> Void) {
        do {
            audioPlayer = try AVAudioPlayer(contentsOf: url)
            audioPlayer?.prepareToPlay()
            audioPlayer?.play()
            self.isPlaying = true

            print("▶️ [Audio] 播放音频: \(url.lastPathComponent)")

            // 播放结束回调
            DispatchQueue.main.asyncAfter(deadline: .now() + (audioPlayer?.duration ?? 0)) {
                self.isPlaying = false
                completion()
                print("⏹️ [Audio] 播放完成")
            }
        } catch {
            print("❌ [Audio] 播放失败: \(error)")
            self.isPlaying = false
            completion()
        }
    }

    func playFromURL(urlString: String, completion: @escaping () -> Void) {
        guard let url = URL(string: urlString) else {
            print("❌ [Audio] 无效的URL: \(urlString)")
            completion()
            return
        }

        // 下载音频文件
        URLSession.shared.dataTask(with: url) { [weak self] data, response, error in
            if let error = error {
                print("❌ [Audio] 下载音频失败: \(error)")
                completion()
                return
            }

            guard let data = data else {
                print("❌ [Audio] 音频数据为空")
                completion()
                return
            }

            // 保存到临时文件
            let tempURL = FileManager.default.temporaryDirectory.appendingPathComponent("temp_audio.mp3")
            do {
                try data.write(to: tempURL)
                DispatchQueue.main.async {
                    self?.play(url: tempURL, completion: completion)
                }
            } catch {
                print("❌ [Audio] 保存音频失败: \(error)")
                completion()
            }
        }.resume()
    }

    func stopPlaying() {
        audioPlayer?.stop()
        self.isPlaying = false
        print("⏹️ [Audio] 停止播放")
    }

    // MARK: - Cleanup

    func cleanup() {
        stopRecording()
        stopPlaying()
        recordingURL = nil
    }
}
