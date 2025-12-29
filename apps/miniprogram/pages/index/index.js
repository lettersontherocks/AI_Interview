// pages/index/index.js
const app = getApp()

Page({
  data: {
    userInfo: null,
    selectedPositionId: '',
    selectedPositionName: '',
    selectedRound: '',
    resume: '',
    isPreparingInterview: false,
    loadingTips: [
      '根据您的岗位生成面试题库',
      '智能匹配面试官风格',
      '制定个性化面试流程'
    ],
    categories: [],
    searchKeyword: '',
    searchResults: [],
    rounds: [
      { label: 'HR面', value: 'HR面', desc: '了解基本情况、沟通能力' },
      { label: '技术一面', value: '技术一面', desc: '基础技术能力考察' },
      { label: '技术二面', value: '技术二面', desc: '深入技术问题探讨' },
      { label: '总监面', value: '总监面', desc: '综合能力与发展潜力' }
    ]
  },

  onLoad() {
    this.loadUserInfo()
    this.loadPositions()
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

  // 加载岗位列表
  loadPositions() {
    wx.request({
      url: `${app.globalData.baseUrl}/positions`,
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200) {
          // 默认展开第一个分类（技术类）
          const categories = res.data.categories.map((cat, index) => ({
            ...cat,
            expanded: index === 0  // 第一个分类默认展开
          }))
          this.setData({ categories })
        }
      },
      fail: (err) => {
        console.error('加载岗位失败:', err)
        wx.showToast({
          title: '加载岗位失败',
          icon: 'none'
        })
      }
    })
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

  // 搜索输入
  onSearchInput(e) {
    const keyword = e.detail.value
    this.setData({ searchKeyword: keyword })

    if (keyword.trim().length === 0) {
      this.setData({ searchResults: [] })
      return
    }

    // 防抖搜索
    clearTimeout(this.searchTimer)
    this.searchTimer = setTimeout(() => {
      this.searchPositions(keyword)
    }, 300)
  },

  // 搜索确认
  onSearchConfirm(e) {
    const keyword = e.detail.value
    if (keyword.trim().length > 0) {
      this.searchPositions(keyword)
    }
  },

  // 执行搜索
  searchPositions(keyword) {
    wx.request({
      url: `${app.globalData.baseUrl}/positions/search?keyword=${encodeURIComponent(keyword)}`,
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200) {
          this.setData({ searchResults: res.data })
        }
      },
      fail: (err) => {
        console.error('搜索失败:', err)
      }
    })
  },

  // 从搜索结果选择岗位
  selectPositionFromSearch(e) {
    const { id, name } = e.currentTarget.dataset
    this.setData({
      selectedPositionId: id,
      selectedPositionName: name,
      searchKeyword: '',
      searchResults: []
    })
  },

  // 展开/收起分类
  toggleCategory(e) {
    const index = e.currentTarget.dataset.index
    const categories = this.data.categories
    categories[index].expanded = !categories[index].expanded
    this.setData({ categories })
  },

  // 选择岗位（父级）
  selectPosition(e) {
    const { id, name, hasChildren } = e.currentTarget.dataset

    if (hasChildren === 'true' || hasChildren === true) {
      // 有子岗位，展开子岗位列表
      const categories = this.data.categories
      for (let cat of categories) {
        for (let pos of cat.positions) {
          if (pos.id === id) {
            pos.showSub = !pos.showSub
            break
          }
        }
      }
      this.setData({ categories })
    } else {
      // 无子岗位，直接选择
      this.setData({
        selectedPositionId: id,
        selectedPositionName: name
      })
    }
  },

  // 选择子岗位
  selectSubPosition(e) {
    const { id, name, parentName } = e.currentTarget.dataset
    this.setData({
      selectedPositionId: id,
      selectedPositionName: `${parentName} - ${name}`
    })
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
    const { selectedPositionId, selectedPositionName, selectedRound, resume, userInfo } = this.data

    if (!selectedPositionId || !selectedRound) {
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
        content: '今日免费次数已用完，会员功能即将上线，敬请期待！',
        showCancel: false,
        confirmText: '知道了'
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
      position_id: selectedPositionId,
      position_name: selectedPositionName,
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
