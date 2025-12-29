// pages/index/index.js
const app = getApp()

Page({
  data: {
    userInfo: null,
    selectedPosition: '',
    selectedRound: '',
    resume: '',
    isPreparingInterview: false,
    loadingTips: [
      '根据您的岗位生成面试题库',
      '智能匹配面试官风格',
      '制定个性化面试流程'
    ],
    positions: [
      { label: '前端工程师', value: '前端工程师', icon: '💻' },
      { label: '后端工程师', value: '后端工程师', icon: '⚙️' },
      { label: '产品经理', value: '产品经理', icon: '📊' },
      { label: '算法工程师', value: '算法工程师', icon: '🤖' },
      { label: '数据分析师', value: '数据分析师', icon: '📈' },
      { label: '销售', value: '销售', icon: '💼' },
      { label: '市场运营', value: '市场运营', icon: '📢' }
    ],
    rounds: [
      { label: 'HR面', value: 'HR面', desc: '了解基本情况、沟通能力' },
      { label: '技术一面', value: '技术一面', desc: '基础技术能力考察' },
      { label: '技术二面', value: '技术二面', desc: '深入技术问题探讨' },
      { label: '总监面', value: '总监面', desc: '综合能力与发展潜力' }
    ]
  },

  onLoad() {
    this.loadUserInfo()
  },

  onShow() {
    this.loadUserInfo()
  },

  // 加载用户信息
  loadUserInfo() {
    if (app.globalData.userInfo) {
      this.setData({
        userInfo: app.globalData.userInfo
      })
    }
  },

  // 登录（简化版 - 不使用微信授权）
  handleLogin() {
    wx.showLoading({ title: '登录中...' })

    wx.request({
      url: `${app.globalData.baseUrl}/user/register`,
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      data: {
        openid: 'user_' + Date.now(),
        nickname: '用户' + Math.floor(Math.random() * 10000),
        avatar: ''
      },
      success: (res) => {
        wx.hideLoading()
        if (res.statusCode === 200) {
          app.globalData.userId = res.data.user_id
          app.globalData.userInfo = res.data
          wx.setStorageSync('userId', res.data.user_id)

          this.setData({ userInfo: res.data })
          wx.showToast({
            title: '登录成功',
            icon: 'success'
          })
        } else {
          wx.showToast({
            title: '登录失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        wx.hideLoading()
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        })
      }
    })
  },

  // 选择岗位
  selectPosition(e) {
    const position = e.currentTarget.dataset.position
    this.setData({ selectedPosition: position })
  },

  // 选择轮次
  selectRound(e) {
    const round = e.currentTarget.dataset.round
    this.setData({ selectedRound: round })
  },

  // 输入简历
  inputResume(e) {
    this.setData({ resume: e.detail.value })
  },

  // 开始面试
  startInterview() {
    const { selectedPosition, selectedRound, resume, userInfo } = this.data

    if (!selectedPosition || !selectedRound) {
      wx.showToast({
        title: '请选择岗位和轮次',
        icon: 'none'
      })
      return
    }

    // 检查配额（仅对已登录用户）
    if (userInfo && !userInfo.is_vip && userInfo.free_count_today >= 2) {
      wx.showModal({
        title: '次数不足',
        content: '今日免费次数已用完，是否购买？',
        confirmText: '购买会员',
        cancelText: '取消',
        success: (res) => {
          if (res.confirm) {
            wx.navigateTo({
              url: '/pages/profile/profile'
            })
          }
        }
      })
      return
    }

    // 显示加载界面
    this.setData({
      isPreparingInterview: true
    })

    // 调用开始面试接口
    const requestUrl = `${app.globalData.baseUrl}/interview/start`
    const requestData = {
      position: selectedPosition,
      round: selectedRound,
      user_id: app.globalData.userId || null,
      resume: resume || null
    }

    console.log('[开始面试] 请求URL:', requestUrl)
    console.log('[开始面试] 请求数据:', requestData)

    wx.request({
      url: requestUrl,
      method: 'POST',
      timeout: 180000, // 超时时间设置为180秒（3分钟）- 真机调试需要更长时间
      header: {
        'content-type': 'application/json'
      },
      data: requestData,
      success: (res) => {
        console.log('[开始面试] 响应状态码:', res.statusCode)
        console.log('[开始面试] 响应数据:', res.data)

        // 隐藏加载界面
        this.setData({
          isPreparingInterview: false
        })

        if (res.statusCode === 200) {
          const { session_id, question } = res.data

          // 跳转到面试页面
          wx.navigateTo({
            url: `/pages/interview/interview?sessionId=${session_id}&firstQuestion=${encodeURIComponent(question)}`
          })
        } else {
          console.error('[开始面试] 请求失败:', res)
          wx.showToast({
            title: res.data.detail || '启动失败',
            icon: 'none',
            duration: 3000
          })
        }
      },
      fail: (err) => {
        console.error('[开始面试] 网络错误:', err)

        // 隐藏加载界面
        this.setData({
          isPreparingInterview: false
        })

        wx.showToast({
          title: `网络错误: ${err.errMsg}`,
          icon: 'none',
          duration: 3000
        })
      }
    })
  }
})
