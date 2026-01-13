// pages/interview/interview.js
const app = getApp()

Page({
  data: {
    sessionId: '',
    messages: [],
    currentAnswer: '',
    canSend: false,  // 添加发送按钮状态标志
    currentQuestion: 1,
    progress: 0,  // 初始进度改为0
    loading: false,
    finished: false,
    scrollToView: '',
    // 语音相关
    inputMode: 'text', // 'text' | 'voice'
    isRecording: false,
    recordDuration: 0,
    recognizedText: '', // 识别后的文字
    // 沉浸模式相关
    viewMode: 'immersive', // 'chat' | 'immersive' - 默认沉浸模式
    isPlaying: false, // 是否正在播放语音
    hasPlayed: false, // 当前问题是否已播放过
    hasEnded: false, // 当前问题是否播放完毕
    autoPlayEnabled: true, // 是否自动播放
    showHistory: false, // 是否显示历史对话
    showQuestionText: false, // 是否显示问题文字（默认隐藏）
    currentQuestionText: '', // 当前问题文本
    ttsCache: {}, // TTS音频缓存 { "问题文本": "文件路径" }
    questionFadeOut: false, // 问题淡出动画状态
    questionVisible: true // 问题是否可见
  },

  recorderManager: null,

  // 计算动态进度（使用渐进式进度条，而不是固定百分比）
  calculateProgress(questionCount) {
    // 使用对数曲线，让进度条平滑增长但永远不会到100%（除非面试结束）
    // 前几个问题进度较快，后面逐渐变慢
    if (questionCount <= 0) return 0

    // 使用公式: progress = 100 * (1 - 1 / (1 + questionCount * 0.15))
    // 这样第1题约13%，第5题约43%，第10题约60%，第20题约75%
    const progress = 100 * (1 - 1 / (1 + questionCount * 0.15))
    return Math.min(progress, 95) // 最多到95%，100%留给完成状态
  },

  onLoad(options) {
    const { sessionId, firstQuestion, resume, audioUrl } = options

    // 初始化录音管理器
    this.initRecorder()

    if (resume === 'true') {
      // 恢复未完成的面试
      this.loadSessionData(sessionId)
    } else {
      // 新面试
      const questionText = decodeURIComponent(firstQuestion)
      const decodedAudioUrl = audioUrl ? decodeURIComponent(audioUrl) : null

      this.setData({
        sessionId,
        messages: [{
          role: 'interviewer',
          content: questionText
        }],
        currentQuestionText: questionText
      }, () => {
        // 默认沉浸模式，首次加载时自动播放第一个问题
        if (this.data.viewMode === 'immersive' && this.data.autoPlayEnabled) {
          setTimeout(() => {
            // 如果有预生成的音频，直接使用；否则调用TTS接口
            if (decodedAudioUrl) {
              console.log('[面试页面] 使用准备阶段生成的音频:', decodedAudioUrl)
              this.playAudioDirect(decodedAudioUrl, questionText)
            } else {
              console.log('[面试页面] 音频未预生成，调用TTS接口')
              this.playQuestion()
            }
          }, 500)
        }
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
            currentQuestion: session.question_count,
            progress: this.calculateProgress(session.question_count),
            currentQuestionText: session.current_question || '',
            hasPlayed: false // 新问题时重置播放状态
          })

          // 如果在沉浸模式且开启自动播放，则自动播放新问题
          if (this.data.viewMode === 'immersive' && this.data.autoPlayEnabled && session.current_question) {
            setTimeout(() => {
              this.playQuestion()
            }, 500)
          }

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

  // 输入回答（沉浸模式使用）
  onInput(e) {
    // 与 inputAnswer 相同的逻辑
    this.inputAnswer(e)
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

  // 切换录音状态（点击式录音）
  toggleRecord() {
    if (this.data.isRecording) {
      // 正在录音，点击结束
      this.stopRecord()
    } else {
      // 未录音，点击开始
      this.startRecord()
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

    // 在沉浸模式下，添加淡出动画
    if (this.data.viewMode === 'immersive') {
      this.setData({
        questionFadeOut: true
      })

      // 等待淡出动画完成后再显示loading状态
      setTimeout(() => {
        this.setData({
          questionVisible: false,
          loading: true
        })
      }, 300) // 300ms淡出动画
    } else {
      // 聊天模式直接显示loading
      this.setData({
        loading: true
      })
    }

    // 添加用户回答到消息列表
    const newMessages = [...messages, {
      role: 'candidate',
      content: text.trim(),
      isVoice: this.data.inputMode === 'voice' // 标记是否来自语音
    }]

    this.setData({
      messages: newMessages
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
      timeout: 120000, // 超时时间设置为120秒（2分钟）
      header: {
        'content-type': 'application/json'
      },
      data: {
        session_id: sessionId,
        answer: text.trim()
      },
      success: (res) => {
        if (res.statusCode === 200) {
          const { next_question, instant_score, hint, is_finished, audio_url } = res.data

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
              progress: 100,
              loading: false
            })
          } else {
            // 添加下一个问题
            newMessages.push({
              role: 'interviewer',
              content: next_question
            })

            const nextQuestionNum = currentQuestion + 1

            // 在沉浸模式下，先结束loading，然后淡入新问题
            if (this.data.viewMode === 'immersive') {
              // 先清除loading状态
              this.setData({
                messages: newMessages,
                currentQuestion: nextQuestionNum,
                progress: this.calculateProgress(nextQuestionNum),
                currentQuestionText: next_question,
                hasPlayed: false,
                hasEnded: false,
                loading: false,
                questionVisible: false,
                questionFadeOut: false
              })

              // 等待100ms后开始淡入
              setTimeout(() => {
                this.setData({
                  questionVisible: true
                })

                // 如果开启自动播放，则在淡入完成后播放
                if (this.data.autoPlayEnabled) {
                  setTimeout(() => {
                    // 优先使用预生成的音频
                    if (audio_url) {
                      console.log('[面试页面] 使用后端预生成的音频:', audio_url)
                      this.playAudioDirect(audio_url, next_question)
                    } else {
                      console.log('[面试页面] 音频未预生成，调用TTS接口')
                      this.playQuestion()
                    }
                  }, 400) // 等待淡入动画完成
                }
              }, 100)
            } else {
              // 聊天模式直接更新
              this.setData({
                messages: newMessages,
                currentQuestion: nextQuestionNum,
                progress: this.calculateProgress(nextQuestionNum),
                currentQuestionText: next_question,
                hasPlayed: false,
                hasEnded: false,
                loading: false
              })
            }

            // 滚动到最新消息
            setTimeout(() => {
              this.setData({
                scrollToView: `msg-${newMessages.length - 1}`
              })
            }, 100)
          }
        } else {
          this.setData({ loading: false })
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
    // 停止音频播放
    if (this.audioContext) {
      this.audioContext.destroy()
    }
  },

  // ========== 沉浸模式相关方法 ==========

  audioContext: null, // 音频上下文

  // 切换到沉浸模式
  switchToImmersive() {
    console.log('[模式切换] 切换到沉浸模式')
    this.setData({
      viewMode: 'immersive'
    })

    // 只在首次进入且开启自动播放且未播放过时才自动播放
    if (this.data.currentQuestionText && this.data.autoPlayEnabled && !this.data.hasPlayed) {
      console.log('[模式切换] 首次进入，自动播放')
      this.playQuestion()
    }
  },

  // 切换到聊天模式
  switchToChatMode() {
    console.log('[模式切换] 切换到聊天模式')
    this.setData({
      viewMode: 'chat'
    })
    // 暂停播放（不销毁音频上下文，保留缓存）
    this.pauseAudio()
  },

  // 返回
  onBack() {
    this.switchToChatMode()
  },

  // 播放当前问题
  playQuestion() {
    const { currentQuestionText, ttsCache } = this.data

    if (!currentQuestionText) {
      console.log('[TTS] 无问题文本')
      return
    }

    // 检查缓存
    if (ttsCache[currentQuestionText]) {
      console.log('[TTS] 使用缓存:', currentQuestionText)
      this.playAudioFile(ttsCache[currentQuestionText])
      return
    }

    console.log('[TTS] 开始播放:', currentQuestionText)

    // 调用火山引擎豆包TTS API
    wx.showLoading({ title: '生成语音中...', mask: true })

    wx.request({
      url: `${app.globalData.baseUrl}/tts/synthesize`,
      method: 'POST',
      header: {
        'content-type': 'application/x-www-form-urlencoded'
      },
      data: {
        text: currentQuestionText,
        voice: 'zh_male_shenyeboke_moon_bigtts'  // 使用火山引擎的深夜播客音色
      },
      responseType: 'arraybuffer',
      success: (res) => {
        wx.hideLoading()

        if (res.statusCode === 200) {
          // 将arraybuffer转为临时文件
          const fs = wx.getFileSystemManager()
          const filePath = `${wx.env.USER_DATA_PATH}/tts_${Date.now()}.mp3`

          fs.writeFile({
            filePath: filePath,
            data: res.data,
            success: () => {
              console.log('[TTS] 音频文件已保存:', filePath)

              // 保存到缓存
              const newCache = { ...this.data.ttsCache }
              newCache[currentQuestionText] = filePath
              this.setData({ ttsCache: newCache })
              console.log('[TTS] 已添加到缓存')

              this.playAudioFile(filePath)
            },
            fail: (err) => {
              console.error('[TTS] 保存音频失败:', err)
              wx.showToast({
                title: '播放失败',
                icon: 'none'
              })
            }
          })
        } else {
          console.error('[TTS] 合成失败:', res)
          wx.showToast({
            title: '语音合成失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        console.error('[TTS] 请求失败:', err)
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        })
      }
    })
  },

  // 直接播放已生成的音频（从URL）
  playAudioDirect(audioUrl, questionText) {
    console.log('[TTS] 直接播放预生成音频:', audioUrl)

    // 将相对路径转换为完整URL
    // 注意：静态文件路径不包含 /api/v1，需要移除
    let fullUrl
    if (audioUrl.startsWith('http')) {
      fullUrl = audioUrl
    } else {
      // 从 baseUrl 中移除 /api/v1 后缀
      const serverUrl = app.globalData.baseUrl.replace(/\/api\/v1$/, '')
      fullUrl = `${serverUrl}${audioUrl}`
    }
    console.log('[TTS] 完整音频URL:', fullUrl)

    // 保存到缓存（使用完整URL）
    const newCache = { ...this.data.ttsCache }
    newCache[questionText] = fullUrl
    this.setData({ ttsCache: newCache })

    // 直接播放服务器URL
    this.playAudioFile(fullUrl)
  },


  // 播放音频文件
  playAudioFile(filePath) {
    // 创建音频上下文
    if (!this.audioContext) {
      this.audioContext = wx.createInnerAudioContext()

      // 监听播放事件
      this.audioContext.onPlay(() => {
        console.log('[音频] 开始播放')
        this.setData({
          isPlaying: true,
          hasPlayed: true,
          hasEnded: false  // 开始播放时清除结束标记
        })
      })

      this.audioContext.onEnded(() => {
        console.log('[音频] 播放结束')
        this.setData({
          isPlaying: false,
          hasEnded: true  // 标记为播放完毕
        })
      })

      this.audioContext.onError((err) => {
        console.error('[音频] 播放错误:', err)
        this.setData({
          isPlaying: false
        })
        wx.showToast({
          title: '播放失败',
          icon: 'none'
        })
      })
    }

    // 播放音频
    this.audioContext.src = filePath
    this.audioContext.play()
  },

  // 切换音频播放/暂停
  toggleAudio() {
    if (this.data.isPlaying) {
      // 暂停
      this.pauseAudio()
    } else {
      // 播放
      if (this.data.hasPlayed && this.audioContext) {
        // 继续播放
        this.audioContext.play()
      } else {
        // 重新播放
        this.playQuestion()
      }
    }
  },

  // 暂停音频
  pauseAudio() {
    if (this.audioContext) {
      this.audioContext.pause()
      this.setData({
        isPlaying: false
      })
    }
  },

  // 停止音频
  stopAudio() {
    if (this.audioContext) {
      this.audioContext.stop()
      this.setData({
        isPlaying: false
      })
    }
  },

  // 切换自动播放
  toggleAutoPlay() {
    this.setData({
      autoPlayEnabled: !this.data.autoPlayEnabled
    })

    wx.showToast({
      title: this.data.autoPlayEnabled ? '已开启自动播放' : '已关闭自动播放',
      icon: 'none'
    })
  },

  // 显示历史对话
  showHistoryDrawer() {
    this.setData({
      showHistory: true
    })
  },

  // 隐藏历史对话
  hideHistory() {
    this.setData({
      showHistory: false
    })
  },

  // 阻止冒泡
  stopPropagation() {
    // 空方法，用于阻止事件冒泡
  },

  // 切换问题文字显示/隐藏
  toggleQuestionText() {
    const newValue = !this.data.showQuestionText
    this.setData({
      showQuestionText: newValue
    })
    console.log('[文字显示] 切换为:', newValue ? '显示' : '隐藏')
  }
})
