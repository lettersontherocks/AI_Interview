// pages/report/report.js
const app = getApp()

Page({
  data: {
    sessionId: '',
    report: null,
    loading: true,
    scoreLevel: ''
  },

  onLoad(options) {
    const { sessionId } = options
    this.setData({ sessionId })
    this.loadReport()
  },

  // 加载报告
  loadReport() {
    wx.request({
      url: `${app.globalData.baseUrl}/interview/report/${this.data.sessionId}`,
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200) {
          const report = res.data
          const scoreLevel = this.getScoreLevel(report.total_score)

          this.setData({
            report,
            scoreLevel,
            loading: false
          })
        } else {
          wx.showToast({
            title: '加载失败',
            icon: 'none'
          })
        }
      },
      fail: () => {
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        })
      }
    })
  },

  // 获取评级
  getScoreLevel(score) {
    if (score >= 90) return '优秀'
    if (score >= 80) return '良好'
    if (score >= 70) return '中等'
    if (score >= 60) return '及格'
    return '需努力'
  },

  // 返回首页
  backToHome() {
    wx.reLaunch({
      url: '/pages/index/index'
    })
  },

  // 分享报告
  shareReport() {
    wx.showShareMenu({
      withShareTicket: true,
      menus: ['shareAppMessage', 'shareTimeline']
    })
  },

  // 分享配置
  onShareAppMessage() {
    return {
      title: `我在AI面试练习中获得了${this.data.report.total_score}分！`,
      path: '/pages/index/index'
    }
  }
})
