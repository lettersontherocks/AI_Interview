// pages/vip/vip.js
const app = getApp()

Page({
  data: {
    userInfo: {},
    selectedPlan: '',
    selectedPrice: 0,
    selectedPlanName: '',
    planNames: {
      single: '单次面试',
      normal_month: '普通VIP · 月度',
      normal_quarter: '普通VIP · 季度',
      normal_half: '普通VIP · 半年',
      normal_year: '普通VIP · 年度',
      super_month: '超级VIP · 月度',
      super_quarter: '超级VIP · 季度',
      super_half: '超级VIP · 半年',
      super_year: '超级VIP · 年度'
    }
  },

  onLoad() {
    this.loadUserInfo()
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
        }
      }
    })
  },

  // 选择方案
  selectPlan(e) {
    const { type, price } = e.currentTarget.dataset
    this.setData({
      selectedPlan: type,
      selectedPrice: parseFloat(price),
      selectedPlanName: this.data.planNames[type]
    })
  },

  // 确认购买
  confirmPurchase() {
    const { selectedPlan, selectedPrice, selectedPlanName } = this.data

    if (!selectedPlan) {
      wx.showToast({
        title: '请选择购买方案',
        icon: 'none'
      })
      return
    }

    wx.showModal({
      title: '确认购买',
      content: `确定购买【${selectedPlanName}】吗？\n价格: ¥${selectedPrice}`,
      success: (res) => {
        if (res.confirm) {
          this.doPurchase()
        }
      }
    })
  },

  // 执行购买（暂未对接支付）
  doPurchase() {
    wx.showLoading({
      title: '处理中...'
    })

    // 模拟支付流程
    setTimeout(() => {
      wx.hideLoading()

      // TODO: 对接微信支付
      wx.showModal({
        title: '功能开发中',
        content: '支付功能正在开发中，敬请期待！',
        showCancel: false,
        success: () => {
          // 支付成功后的逻辑
          // 1. 调用后端接口更新用户VIP状态
          // 2. 刷新用户信息
          // 3. 返回上一页
        }
      })
    }, 1000)
  }
})
