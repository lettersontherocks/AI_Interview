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
      '📋 正在分析岗位要求...',
      '🎯 智能匹配面试题库...',
      '💡 准备个性化问题...',
      '☕ 面试官正在喝口水...',
      '📚 翻阅您的简历中...',
      '🎤 调试语音系统...',
      '✨ 营造专业面试氛围...',
      '🔍 精选最适合的题目...',
      '💼 面试官整理思路中...',
      '🎨 优化面试体验...'
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
        // 前90%按对数增长
        currentProgress += Math.random() * 8
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
          const { session_id, first_question } = res.data

          // 准备完成
          this.onPrepareComplete(session_id, first_question)
        } else {
          // 显示详细错误信息
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
  onPrepareComplete(sessionId, firstQuestion) {
    console.log('[准备页面] 准备完成:', { sessionId, firstQuestion })

    // 清除定时器
    if (this.data.tipTimer) {
      clearInterval(this.data.tipTimer)
    }
    if (this.data.progressTimer) {
      clearInterval(this.data.progressTimer)
    }

    // 显示完成状态
    this.setData({
      currentTip: '✓ 一切准备就绪',
      hintText: '马上开始您的精彩面试',
      progress: 100,
      isReady: true,
      sessionId,
      firstQuestion
    })

    // 1秒后跳转到面试页
    setTimeout(() => {
      wx.redirectTo({
        url: `/pages/interview/interview?sessionId=${sessionId}&firstQuestion=${encodeURIComponent(firstQuestion)}&resume=false`
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
