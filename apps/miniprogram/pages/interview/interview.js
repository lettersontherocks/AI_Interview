// pages/interview/interview.js
const app = getApp()

Page({
  data: {
    sessionId: '',
    messages: [],
    currentAnswer: '',
    canSend: false,  // 添加发送按钮状态标志
    currentQuestion: 1,
    progress: 10,
    loading: false,
    finished: false,
    scrollToView: '',
    // 语音相关
    inputMode: 'text', // 'text' | 'voice'
    isRecording: false,
    recordDuration: 0,
    recognizedText: '' // 识别后的文字
  },

  recorderManager: null,

  onLoad(options) {
    const { sessionId, firstQuestion, resume } = options

    // 初始化录音管理器
    this.initRecorder()

    if (resume === 'true') {
      // 恢复未完成的面试
      this.loadSessionData(sessionId)
    } else {
      // 新面试
      this.setData({
        sessionId,
        messages: [{
          role: 'interviewer',
          content: decodeURIComponent(firstQuestion)
        }]
      })
    }
  },

  // 初始化录音管理器
  initRecorder() {
    this.recorderManager = wx.getRecorderManager()

    // 录音开始
    this.recorderManager.onStart(() => {
      console.log('录音开始')
      this.setData({ isRecording: true, recordDuration: 0 })

      // 更新录音时长
      this.recordTimer = setInterval(() => {
        this.setData({
          recordDuration: this.data.recordDuration + 1
        })
      }, 1000)
    })

    // 录音停止
    this.recorderManager.onStop((res) => {
      console.log('录音停止', res)
      if (this.recordTimer) {
        clearInterval(this.recordTimer)
      }
      this.setData({ isRecording: false })

      // 如果录音时间太短
      if (res.duration < 500) {
        wx.showToast({
          title: '录音时间太短',
          icon: 'none'
        })
        return
      }

      // 上传到后端进行识别
      wx.showLoading({ title: '识别中...' })

      wx.uploadFile({
        url: `${app.globalData.baseUrl}/voice/recognize`,
        filePath: res.tempFilePath,
        name: 'audio',
        success: (uploadRes) => {
          wx.hideLoading()

          if (uploadRes.statusCode === 200) {
            const data = JSON.parse(uploadRes.data)
            const text = data.text || ''

            if (text) {
              // 将识别的文字填入输入框，让用户可以编辑
              // 切换回文字模式，让用户可以看到并修改
              this.setData({
                inputMode: 'text',
                currentAnswer: text,
                canSend: text.trim().length > 0
              })

              wx.showToast({
                title: '识别成功，可修改后发送',
                icon: 'none',
                duration: 2000
              })
            } else {
              wx.showToast({
                title: '未识别到内容',
                icon: 'none'
              })
            }
          } else {
            wx.showToast({
              title: '识别失败',
              icon: 'none'
            })
          }
        },
        fail: () => {
          wx.hideLoading()
          wx.showToast({
            title: '上传失败',
            icon: 'none'
          })
        }
      })
    })

    // 录音错误
    this.recorderManager.onError((err) => {
      console.error('录音错误', err)
      if (this.recordTimer) {
        clearInterval(this.recordTimer)
      }
      this.setData({ isRecording: false })
      wx.showToast({
        title: '录音失败',
        icon: 'none'
      })
    })
  },

  // 加载会话数据（恢复面试）
  loadSessionData(sessionId) {
    wx.showLoading({ title: '加载中...' })

    const app = getApp()
    wx.request({
      url: `${app.globalData.baseUrl}/interview/session/${sessionId}`,
      method: 'GET',
      success: (res) => {
        wx.hideLoading()

        if (res.statusCode === 200) {
          const session = res.data

          // 重建消息列表
          const messages = []

          // 从 transcript 恢复对话历史
          if (session.transcript && session.transcript.length > 0) {
            session.transcript.forEach(msg => {
              messages.push({
                role: msg.role,
                content: msg.content,
                score: msg.score,
                hint: msg.hint
              })
            })
          }

          // 如果有当前问题，检查是否已经在transcript中，避免重复
          if (session.current_question) {
            const lastMessage = messages[messages.length - 1]
            const isDuplicate = lastMessage &&
                               lastMessage.role === 'interviewer' &&
                               lastMessage.content === session.current_question

            // 只有当前问题不在最后一条消息中时才添加
            if (!isDuplicate) {
              messages.push({
                role: 'interviewer',
                content: session.current_question
              })
            }
          }

          this.setData({
            sessionId: session.session_id,
            messages: messages,
            currentQuestion: session.question_count + 1,
            progress: ((session.question_count + 1) / 10) * 100
          })

          // 滚动到底部
          setTimeout(() => {
            this.setData({
              scrollToView: `msg-${messages.length - 1}`
            })
          }, 100)
        } else {
          wx.showToast({
            title: '加载失败',
            icon: 'none'
          })
          setTimeout(() => {
            wx.navigateBack()
          }, 1500)
        }
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        })
        setTimeout(() => {
          wx.navigateBack()
        }, 1500)
      }
    })
  },

  // 输入回答
  inputAnswer(e) {
    const value = e.detail.value
    this.setData({
      currentAnswer: value,
      canSend: value.trim().length > 0  // 添加一个布尔值用于按钮状态
    })
  },

  // 切换输入模式
  toggleInputMode() {
    const newMode = this.data.inputMode === 'text' ? 'voice' : 'text'
    this.setData({ inputMode: newMode })

    wx.showToast({
      title: newMode === 'text' ? '已切换到文字输入' : '已切换到语音输入',
      icon: 'none',
      duration: 1500
    })
  },

  // 开始录音
  startRecord() {
    if (!this.recorderManager) {
      wx.showToast({
        title: '录音功能未初始化',
        icon: 'none'
      })
      return
    }

    // 开始录音
    this.recorderManager.start({
      duration: 60000, // 最长60秒
      format: 'mp3',
      sampleRate: 16000,
      numberOfChannels: 1,
      encodeBitRate: 48000
    })
  },

  // 停止录音
  stopRecord() {
    if (this.recorderManager) {
      this.recorderManager.stop()
    }
  },

  // 提交文字回答（统一的提交方法，文字和语音都用这个）
  submitTextAnswer(text) {
    const { sessionId, messages, currentQuestion } = this.data

    if (!text || !text.trim()) {
      wx.showToast({
        title: '内容为空',
        icon: 'none'
      })
      return
    }

    // 添加用户回答到消息列表
    const newMessages = [...messages, {
      role: 'candidate',
      content: text.trim(),
      isVoice: this.data.inputMode === 'voice' // 标记是否来自语音
    }]

    this.setData({
      messages: newMessages,
      loading: true
    })

    // 滚动到底部
    setTimeout(() => {
      this.setData({
        scrollToView: `msg-${newMessages.length - 1}`
      })
    }, 100)

    // 调用接口提交回答
    wx.request({
      url: `${app.globalData.baseUrl}/interview/answer`,
      method: 'POST',
      data: {
        session_id: sessionId,
        answer: text.trim()
      },
      success: (res) => {
        this.setData({ loading: false })

        if (res.statusCode === 200) {
          const { next_question, instant_score, hint, is_finished } = res.data

          // 更新上一条消息的评分和提示
          if (instant_score) {
            newMessages[newMessages.length - 1].score = instant_score
            newMessages[newMessages.length - 1].hint = hint
          }

          if (is_finished) {
            // 面试结束
            this.setData({
              messages: newMessages,
              finished: true,
              progress: 100
            })
          } else {
            // 添加下一个问题
            newMessages.push({
              role: 'interviewer',
              content: next_question
            })

            const nextQuestionNum = currentQuestion + 1
            this.setData({
              messages: newMessages,
              currentQuestion: nextQuestionNum,
              progress: (nextQuestionNum / 10) * 100
            })

            // 滚动到最新消息
            setTimeout(() => {
              this.setData({
                scrollToView: `msg-${newMessages.length - 1}`
              })
            }, 100)
          }
        } else {
          wx.showToast({
            title: '提交失败',
            icon: 'none'
          })
        }
      },
      fail: () => {
        this.setData({ loading: false })
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        })
      }
    })
  },

  // 提交文字输入框的回答
  submitAnswer() {
    const { currentAnswer } = this.data

    if (!currentAnswer.trim()) {
      return
    }

    // 清空输入框
    this.setData({
      currentAnswer: '',
      canSend: false
    })

    // 调用统一的提交方法
    this.submitTextAnswer(currentAnswer)
  },

  // 查看报告
  viewReport() {
    wx.redirectTo({
      url: `/pages/report/report?sessionId=${this.data.sessionId}`
    })
  },

  // 页面卸载时确认
  onUnload() {
    if (!this.data.finished) {
      wx.showModal({
        title: '提示',
        content: '面试尚未完成，确定要退出吗？',
        success: (res) => {
          if (!res.confirm) {
            // 阻止返回
            return false
          }
        }
      })
    }
  }
})
