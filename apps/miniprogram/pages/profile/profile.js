// pages/profile/profile.js
const app = getApp()

Page({
  data: {
    userInfo: {},
    freeLimit: 2,
    selectedPrice: 'month',
    historyList: []
  },

  onLoad() {
    this.loadUserInfo()
    this.loadHistory()
  },

  onShow() {
    // 每次显示时刷新用户信息和历史记录
    this.loadUserInfo()
    this.loadHistory()
  },

  // 加载用户信息
  loadUserInfo() {
    const userId = app.globalData.userId
    if (!userId) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      })
      return
    }

    wx.request({
      url: `${app.globalData.baseUrl}/user/${userId}`,
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({
            userInfo: res.data
          })
          app.globalData.userInfo = res.data
        }
      },
      fail: () => {
        wx.showToast({
          title: '加载失败',
          icon: 'none'
        })
      }
    })
  },

  // 加载面试记录
  loadHistory() {
    const userId = app.globalData.userId
    if (!userId) return

    wx.request({
      url: `${app.globalData.baseUrl}/user/${userId}/history`,
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200) {
          const historyList = res.data.map(item => ({
            ...item,
            date: this.formatDate(item.created_at),
            level: item.total_score ? this.getScoreLevel(item.total_score) : '未完成',
            score: item.total_score ? item.total_score.toFixed(1) : '-'
          }))
          this.setData({ historyList })
        }
      }
    })
  },

  // 格式化日期
  formatDate(dateString) {
    const date = new Date(dateString)
    const month = date.getMonth() + 1
    const day = date.getDate()
    const hour = date.getHours()
    const minute = date.getMinutes()
    return `${month}月${day}日 ${hour}:${minute.toString().padStart(2, '0')}`
  },

  // 获取评级
  getScoreLevel(score) {
    if (score >= 90) return '优秀'
    if (score >= 80) return '良好'
    if (score >= 70) return '中等'
    if (score >= 60) return '及格'
    return '需努力'
  },

  // 选择价格方案
  selectPrice(e) {
    const type = e.currentTarget.dataset.type
    this.setData({ selectedPrice: type })
  },

  // 跳转到VIP页面
  goToVipPage() {
    wx.navigateTo({
      url: '/pages/vip/vip'
    })
  },

  // 继续面试
  continueInterview(e) {
    const sessionId = e.currentTarget.dataset.sessionId

    wx.showLoading({ title: '加载中...' })

    // 获取会话详情
    wx.request({
      url: `${app.globalData.baseUrl}/interview/session/${sessionId}`,
      method: 'GET',
      success: (res) => {
        wx.hideLoading()

        if (res.statusCode === 200) {
          const session = res.data

          // 跳转到面试页面，传递会话信息用于恢复
          wx.navigateTo({
            url: `/pages/interview/interview?sessionId=${sessionId}&resume=true`
          })
        } else {
          wx.showToast({
            title: '加载失败',
            icon: 'none'
          })
        }
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        })
      }
    })
  },

  // 查看报告
  viewReport(e) {
    const sessionId = e.currentTarget.dataset.sessionId
    wx.navigateTo({
      url: `/pages/report/report?sessionId=${sessionId}`
    })
  },

  // 查看全部历史
  viewAllHistory() {
    wx.navigateTo({
      url: '/pages/history/history'
    })
  },

  // 跳转到首页
  goToIndex() {
    wx.switchTab({
      url: '/pages/index/index'
    })
  },

  // 清除缓存
  clearCache() {
    wx.showModal({
      title: '确认清除',
      content: '确定要清除本地缓存吗？',
      success: (res) => {
        if (res.confirm) {
          wx.clearStorage({
            success: () => {
              wx.showToast({
                title: '清除成功',
                icon: 'success'
              })
            }
          })
        }
      }
    })
  },

  // 联系客服
  contactSupport() {
    wx.showModal({
      title: '联系客服',
      content: '客服微信: ai_interview_support',
      showCancel: false
    })
  },

  // 关于我们
  aboutUs() {
    wx.showModal({
      title: 'AI面试练习',
      content: '版本: 1.0.0\n智能面试练习平台\n帮助求职者提升面试技能',
      showCancel: false
    })
  },

  // 退出登录
  logout() {
    wx.showModal({
      title: '确认退出',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          app.globalData.userInfo = null
          app.globalData.userId = null
          wx.clearStorage()
          wx.reLaunch({
            url: '/pages/index/index'
          })
        }
      }
    })
  }
})
