// pages/prepare/prepare.js
const app = getApp()

Page({
  data: {
    sessionId: '',
    firstQuestion: '',
    currentTip: '',
    hintText: '正在为您准备最佳面试体验',
    progress: 0,
    isReady: false,

    // 提示文案（正式+俏皮混合）
    tips: [
      '正在分析岗位要求',
      '智能匹配面试题库',
      '准备个性化问题',
      '面试官正在喝口水',
      '翻阅您的简历中',
      '调试语音系统',
      '营造专业面试氛围',
      '精选最适合的题目',
      '面试官整理思路中',
      '优化面试体验'
    ],

    currentTipIndex: 0,
    tipTimer: null,
    progressTimer: null
  },

  onLoad(options) {
    console.log('[准备页面] 接收参数:', options)

    const { position_id, position_name, round, resume, interviewer_style } = options

    // 解码参数
    const decodedParams = {
      position_id,
      position_name: decodeURIComponent(position_name || ''),
      round: decodeURIComponent(round || ''),
      resume: resume && resume !== 'null' && resume !== '' ? decodeURIComponent(resume) : null,
      interviewer_style: interviewer_style && interviewer_style !== 'null' && interviewer_style !== '' ? decodeURIComponent(interviewer_style) : null
    }

    console.log('[准备页面] 解码后参数:', decodedParams)

    // 开始准备动画
    this.startPreparation()

    // 调用后端接口开始面试
    this.startInterview(decodedParams)
  },

  onUnload() {
    // 清理定时器
    if (this.data.tipTimer) {
      clearInterval(this.data.tipTimer)
    }
    if (this.data.progressTimer) {
      clearInterval(this.data.progressTimer)
    }
  },

  // 开始准备动画
  startPreparation() {
    // 显示第一条提示
    this.setData({
      currentTip: this.data.tips[0]
    })

    // 每2秒切换提示文案
    const tipTimer = setInterval(() => {
      const nextIndex = (this.data.currentTipIndex + 1) % this.data.tips.length
      this.setData({
        currentTipIndex: nextIndex,
        currentTip: this.data.tips[nextIndex]
      })
    }, 2000)

    // 渐进式进度条（不会到100%，除非真的准备好）
    let currentProgress = 0
    const progressTimer = setInterval(() => {
      if (currentProgress < 90) {
        // 使用对数曲线：越接近90%增长越慢
        // 前半部分(0-45%)增长更慢，后半部分(45-90%)逐渐减速
        const remaining = 90 - currentProgress
        const increment = remaining * 0.02 + Math.random() * 0.5
        currentProgress += increment
        currentProgress = Math.min(currentProgress, 90)
        this.setData({ progress: Math.floor(currentProgress) })
      }
    }, 300)

    this.setData({ tipTimer, progressTimer })
  },

  // 调用开始面试接口
  startInterview(params) {
    const requestUrl = `${app.globalData.baseUrl}/interview/start`
    const requestData = {
      position_id: params.position_id,
      position_name: params.position_name,
      round: params.round,
      user_id: app.globalData.userId || null,
      resume: params.resume,
      interviewer_style: params.interviewer_style
    }

    console.log('[准备页面] 请求URL:', requestUrl)
    console.log('[准备页面] 请求数据:', requestData)

    wx.request({
      url: requestUrl,
      method: 'POST',
      timeout: 120000,
      header: {
        'content-type': 'application/json'
      },
      data: requestData,
      success: (res) => {
        console.log('[准备页面] 响应状态码:', res.statusCode)
        console.log('[准备页面] 响应数据:', res.data)

        if (res.statusCode === 200) {
          const { session_id, question, audio_url } = res.data

          // 准备完成
          this.onPrepareComplete(session_id, question, audio_url)
        } else if (res.statusCode === 403) {
          // 配额不足 - 引导用户购买VIP
          const errorMsg = res.data?.detail || '今日面试次数已用完'
          console.error('[准备页面] 配额不足:', errorMsg)

          // 清除定时器
          if (this.data.tipTimer) {
            clearInterval(this.data.tipTimer)
          }
          if (this.data.progressTimer) {
            clearInterval(this.data.progressTimer)
          }

          wx.showModal({
            title: '今日面试次数已用完',
            content: `${errorMsg}\n\n开通VIP会员，享受更多面试机会！`,
            cancelText: '返回',
            confirmText: '开通VIP',
            confirmColor: '#667eea',
            success: (modalRes) => {
              if (modalRes.confirm) {
                // 返回首页并跳转到VIP页面
                wx.navigateBack({
                  success: () => {
                    wx.navigateTo({
                      url: '/pages/vip/vip'
                    })
                  }
                })
              } else {
                // 返回首页
                wx.navigateBack()
              }
            }
          })
        } else {
          // 其他错误 - 允许重试
          const errorMsg = res.data?.detail || '面试准备失败，请重试'
          console.error('[准备页面] 错误信息:', errorMsg)
          this.onPrepareError(errorMsg)
        }
      },
      fail: (err) => {
        console.error('[准备页面] 请求失败:', err)
        this.onPrepareError('网络错误，请检查网络连接')
      }
    })
  },

  // 准备完成
  onPrepareComplete(sessionId, firstQuestion, audioUrl) {
    console.log('[准备页面] 准备完成:', { sessionId, firstQuestion, audioUrl })

    // 清除定时器
    if (this.data.tipTimer) {
      clearInterval(this.data.tipTimer)
    }
    if (this.data.progressTimer) {
      clearInterval(this.data.progressTimer)
    }

    // 显示完成状态
    this.setData({
      hintText: '马上开始您的精彩面试',
      isReady: true,
      sessionId,
      firstQuestion,
      audioUrl
    })

    // 平滑过渡到100%（如果还没到100%）
    const currentProgress = this.data.progress
    if (currentProgress < 100) {
      let progress = currentProgress
      const completeTimer = setInterval(() => {
        progress += (100 - currentProgress) * 0.15
        if (progress >= 99.5) {
          clearInterval(completeTimer)
          this.setData({ progress: 100 })
        } else {
          this.setData({ progress: Math.floor(progress) })
        }
      }, 50)
    } else {
      // 已经到达100%，直接设置
      this.setData({ progress: 100 })
    }

    // 1秒后跳转到面试页，传递音频URL
    setTimeout(() => {
      const audioParam = audioUrl ? `&audioUrl=${encodeURIComponent(audioUrl)}` : ''
      wx.redirectTo({
        url: `/pages/interview/interview?sessionId=${sessionId}&firstQuestion=${encodeURIComponent(firstQuestion)}&resume=false${audioParam}`
      })
    }, 1000)
  },

  // 准备失败
  onPrepareError(message) {
    // 清除定时器
    if (this.data.tipTimer) {
      clearInterval(this.data.tipTimer)
    }
    if (this.data.progressTimer) {
      clearInterval(this.data.progressTimer)
    }

    wx.showModal({
      title: '准备失败',
      content: message,
      showCancel: true,
      cancelText: '返回',
      confirmText: '重试',
      success: (res) => {
        if (res.confirm) {
          // 重新加载页面
          const pages = getCurrentPages()
          const currentPage = pages[pages.length - 1]
          const options = currentPage.options

          // 重置状态
          this.setData({
            progress: 0,
            isReady: false,
            currentTipIndex: 0,
            currentTip: this.data.tips[0],
            hintText: '正在为您准备最佳面试体验'
          })

          // 重新开始
          this.startPreparation()
          this.startInterview({
            position_id: options.position_id,
            position_name: options.position_name,
            round: options.round,
            resume: options.resume || null,
            interviewer_style: options.interviewer_style || null
          })
        } else {
          // 返回首页
          wx.navigateBack()
        }
      }
    })
  }
})
