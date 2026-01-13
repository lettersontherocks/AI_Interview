// pages/history/history.js
const app = getApp()

Page({
  data: {
    historyList: [],
    loading: false
  },

  onLoad() {
    this.loadHistory()
  },

  onShow() {
    // 每次显示时刷新
    this.loadHistory()
  },

  // 加载面试记录
  loadHistory() {
    const userId = app.globalData.userId
    if (!userId) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      })
      setTimeout(() => {
        wx.switchTab({
          url: '/pages/index/index'
        })
      }, 1500)
      return
    }

    this.setData({ loading: true })

    wx.request({
      url: `${app.globalData.baseUrl}/user/${userId}/history`,
      method: 'GET',
      success: (res) => {
        this.setData({ loading: false })

        if (res.statusCode === 200) {
          const historyList = res.data.map(item => ({
            ...item,
            date: this.formatDate(item.created_at),
            level: item.total_score ? this.getScoreLevel(item.total_score) : '未完成',
            score: item.total_score ? item.total_score.toFixed(1) : '-'
          }))
          this.setData({ historyList })
        }
      },
      fail: () => {
        this.setData({ loading: false })
        wx.showToast({
          title: '加载失败',
          icon: 'none'
        })
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

  // 继续面试
  continueInterview(e) {
    const sessionId = e.currentTarget.dataset.sessionId

    wx.showLoading({ title: '加载中...' })

    wx.request({
      url: `${app.globalData.baseUrl}/interview/session/${sessionId}`,
      method: 'GET',
      success: (res) => {
        wx.hideLoading()

        if (res.statusCode === 200) {
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

  // 下拉刷新
  onPullDownRefresh() {
    this.loadHistory()
    setTimeout(() => {
      wx.stopPullDownRefresh()
    }, 1000)
  },

  // 返回首页
  goToIndex() {
    wx.switchTab({
      url: '/pages/index/index'
    })
  }
})
