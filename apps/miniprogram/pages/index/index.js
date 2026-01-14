// pages/index/index.js
const app = getApp()

Page({
  data: {
    userInfo: null,
    remainingCount: 2,  // 剩余次数
    selectedPositionId: '',
    selectedPositionName: '',
    selectedRound: '',
    selectedInterviewerStyle: '',  // 选中的面试官风格
    interviewerStyles: [],  // 面试官风格列表
    recommendedStyle: '',  // 推荐的面试官风格
    resume: '',  // 手动输入的简历
    uploadedResume: '',  // 上传文件解析的简历
    showResumeInput: false,  // 是否显示简历输入浮层
    isPreparingInterview: false,
    loadingTips: [
      '根据您的岗位生成面试题库',
      '智能匹配面试官风格',
      '制定个性化面试流程'
    ],
    categories: [],
    searchKeyword: '',
    searchResults: [],
    showPositionList: false,  // 是否显示岗位列表
    showStyleList: false,     // 是否显示风格列表
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
    this.loadInterviewerStyles()
  },

  onShow() {
    // 页面显示时刷新用户信息（确保配额是最新的）
    this.refreshUserInfo()
  },

  // 加载用户信息（从本地缓存）
  loadUserInfo() {
    if (app.globalData.userInfo) {
      this.updateUserInfo(app.globalData.userInfo)
    }
  },

  // 刷新用户信息（从后端获取最新数据）
  refreshUserInfo() {
    const userInfo = app.globalData.userInfo
    if (!userInfo || !userInfo.user_id) {
      // 未登录，只显示本地数据
      this.loadUserInfo()
      return
    }

    // 静默刷新，不显示loading
    wx.request({
      url: `${app.globalData.baseUrl}/user/${userInfo.user_id}`,
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200) {
          const latestUserInfo = res.data
          // 更新全局和本地用户信息
          app.globalData.userInfo = latestUserInfo
          this.updateUserInfo(latestUserInfo)
          console.log('✅ [首页] 用户信息已刷新，剩余次数:', this.data.remainingCount)
        } else {
          // 刷新失败，使用本地缓存数据
          console.warn('⚠️ [首页] 刷新用户信息失败，使用缓存数据')
          this.loadUserInfo()
        }
      },
      fail: (err) => {
        // 网络错误，使用本地缓存数据
        console.warn('⚠️ [首页] 网络错误，使用缓存数据:', err)
        this.loadUserInfo()
      }
    })
  },

  // 更新用户信息并计算剩余次数
  updateUserInfo(userInfo) {
    let remainingCount
    if (userInfo.vip_type === 'super') {
      remainingCount = 999  // 超级VIP无限次
    } else {
      // 使用后端返回的daily_limit
      const dailyLimit = userInfo.daily_limit || 1
      remainingCount = Math.max(0, dailyLimit - userInfo.free_count_today)
    }
    this.setData({
      userInfo: userInfo,
      remainingCount: remainingCount
    })
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
            ...cat
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

  // 加载面试官风格列表
  loadInterviewerStyles() {
    console.log('[加载面试官风格] 请求URL:', `${app.globalData.baseUrl}/interviewer-styles`)

    // 临时fallback数据（后端部署后可以移除）
    const fallbackStyles = [
      { id: 'friendly', name: '友好型', description: '温和友善，鼓励性强，适合缓解紧张', icon: '😊' },
      { id: 'professional', name: '专业型', description: '严谨专业，注重深度，追求技术细节', icon: '💼' },
      { id: 'challenging', name: '挑战型', description: '有压力感，善于提出尖锐问题', icon: '🔥' },
      { id: 'mentor', name: '导师型', description: '像导师一样引导，善于启发思考', icon: '🎓' }
    ]

    wx.request({
      url: `${app.globalData.baseUrl}/interviewer-styles`,
      method: 'GET',
      success: (res) => {
        console.log('[加载面试官风格] 响应状态码:', res.statusCode)
        console.log('[加载面试官风格] 响应数据:', res.data)
        if (res.statusCode === 200 && res.data && res.data.styles) {
          this.setData({
            interviewerStyles: res.data.styles
          })
          console.log('[加载面试官风格] 从API加载成功，数量:', res.data.styles.length)
        } else {
          // API失败，使用fallback
          console.log('[加载面试官风格] API失败，使用fallback数据')
          this.setData({
            interviewerStyles: fallbackStyles
          })
        }
      },
      fail: (err) => {
        console.error('[加载面试官风格] 网络错误，使用fallback数据:', err)
        this.setData({
          interviewerStyles: fallbackStyles
        })
      }
    })
  },

  // 更新推荐的面试官风格
  updateRecommendedStyle() {
    const { selectedRound } = this.data
    if (!selectedRound) {
      this.setData({ recommendedStyle: '' })
      return
    }

    // Fallback推荐映射（与后端保持一致）
    const fallbackRecommendations = {
      'HR面': 'friendly',
      '技术一面': 'friendly',
      '技术二面': 'professional',
      '总监面': 'challenging'
    }

    wx.request({
      url: `${app.globalData.baseUrl}/interviewer-styles?round=${encodeURIComponent(selectedRound)}`,
      method: 'GET',
      success: (res) => {
        console.log('[推荐风格] 响应:', res)
        if (res.statusCode === 200 && res.data && res.data.recommended) {
          this.setData({
            recommendedStyle: res.data.recommended
          })
        } else {
          // 使用fallback
          this.setData({
            recommendedStyle: fallbackRecommendations[selectedRound] || 'friendly'
          })
        }
      },
      fail: (err) => {
        console.error('[推荐风格] 网络错误，使用fallback:', err)
        this.setData({
          recommendedStyle: fallbackRecommendations[selectedRound] || 'friendly'
        })
      }
    })
  },

  // 登录（简化版 - 不使用微信授权）
  handleLogin() {
    // 调用微信登录
    app.wxLogin((userInfo) => {
      // 登录成功回调
      this.updateUserInfo(userInfo)
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
    const url = `${app.globalData.baseUrl}/positions/search?keyword=${encodeURIComponent(keyword)}`
    console.log('[搜索岗位] 请求URL:', url)
    console.log('[搜索岗位] 关键词:', keyword)

    wx.request({
      url: url,
      method: 'GET',
      success: (res) => {
        console.log('[搜索岗位] 响应状态码:', res.statusCode)
        console.log('[搜索岗位] 响应数据:', res.data)
        if (res.statusCode === 200) {
          this.setData({ searchResults: res.data })
          console.log('[搜索岗位] 搜索结果数量:', res.data.length)
        } else {
          console.error('[搜索岗位] 请求失败:', res)
          wx.showToast({
            title: '搜索失败',
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        console.error('[搜索岗位] 网络错误:', err)
        wx.showToast({
          title: '网络错误',
          icon: 'none'
        })
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
      searchResults: [],
      showPositionList: false  // 选择后自动收起
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
        selectedPositionName: name,
        showPositionList: false  // 选择后自动收起
      })
    }
  },

  // 选择子岗位
  selectSubPosition(e) {
    const { id, name, parentName } = e.currentTarget.dataset
    this.setData({
      selectedPositionId: id,
      selectedPositionName: `${parentName} - ${name}`,
      showPositionList: false  // 选择后自动收起
    })
  },

  // 选择轮次
  selectRound(e) {
    const round = e.currentTarget.dataset.round
    this.setData({ selectedRound: round })
    // 选择轮次后，更新推荐的面试官风格
    this.updateRecommendedStyle()
  },

  // 选择面试官风格
  selectInterviewerStyle(e) {
    const style = e.currentTarget.dataset.style
    this.setData({
      selectedInterviewerStyle: style,
      showStyleList: false  // 选择后自动收起
    })
  },

  // 切换岗位列表展开/收起
  togglePositionList() {
    this.setData({
      showPositionList: !this.data.showPositionList
    })
  },

  // 阻止事件冒泡（用于浮层内容区）
  stopPropagation() {
    // 空函数，仅用于阻止事件冒泡
  },

  // 切换风格列表展开/收起
  toggleStyleList() {
    // 如果未选择轮次，提示用户
    if (!this.data.selectedRound) {
      wx.showToast({
        title: '请先选择面试轮次',
        icon: 'none',
        duration: 2000
      })
      return
    }

    this.setData({
      showStyleList: !this.data.showStyleList
    })
  },

  // 输入简历
  inputResume(e) {
    this.setData({ resume: e.detail.value })
  },

  // 切换简历输入浮层
  toggleResumeInput() {
    this.setData({
      showResumeInput: !this.data.showResumeInput
    })
  },

  // 简历输入框内容变化
  onResumeInput(e) {
    this.setData({ resume: e.detail.value })
  },

  // 清空简历
  clearResume() {
    this.setData({
      resume: '',
      showResumeInput: false
    })
    wx.showToast({
      title: '已清空',
      icon: 'success',
      duration: 1500
    })
  },

  // 确认简历输入
  confirmResume() {
    this.setData({ showResumeInput: false })
    if (this.data.resume) {
      wx.showToast({
        title: '简历信息已保存',
        icon: 'success',
        duration: 2000
      })
    }
  },

  // 上传文件
  handleUploadFile() {
    const self = this
    wx.chooseMessageFile({
      count: 1,
      type: 'file',
      extension: ['pdf', 'doc', 'docx', 'jpg', 'png', 'jpeg'],
      success(res) {
        const file = res.tempFiles[0]
        console.log('[文件选择] 文件信息:', file)

        // 检查文件大小(10MB)
        if (file.size > 10 * 1024 * 1024) {
          wx.showToast({
            title: '文件过大,最大10MB',
            icon: 'none'
          })
          return
        }

        // 显示加载
        wx.showLoading({
          title: '解析中...',
          mask: true
        })

        // 上传文件到后端
        wx.uploadFile({
          url: `${app.globalData.baseUrl}/resume/parse`,
          filePath: file.path,
          name: 'file',
          success(uploadRes) {
            console.log('[文件上传] 响应:', uploadRes)
            wx.hideLoading()

            if (uploadRes.statusCode === 200) {
              const data = JSON.parse(uploadRes.data)

              // 保存上传的简历到 uploadedResume，不影响手动输入的 resume
              self.setData({
                uploadedResume: data.text
              })

              wx.showToast({
                title: '简历解析成功',
                icon: 'success',
                duration: 2000
              })

              console.log('[简历上传] 解析成功，字数:', data.text.length)
            } else {
              const errorData = JSON.parse(uploadRes.data)
              wx.showToast({
                title: errorData.detail || '解析失败',
                icon: 'none',
                duration: 3000
              })
            }
          },
          fail(err) {
            console.error('[文件上传] 失败:', err)
            wx.hideLoading()
            wx.showToast({
              title: '上传失败',
              icon: 'none'
            })
          }
        })
      },
      fail(err) {
        console.error('[文件选择] 失败:', err)
        wx.showToast({
          title: '取消选择',
          icon: 'none'
        })
      }
    })
  },

  // 清除简历
  clearResume() {
    this.setData({
      resume: '',
      showManualInput: false,
      resumeUploaded: false
    })
  },

  // 开始面试
  startInterview() {
    const { selectedPositionId, selectedPositionName, selectedRound, selectedInterviewerStyle, resume, uploadedResume, userInfo } = this.data

    if (!selectedPositionId || !selectedRound) {
      wx.showToast({
        title: '请选择岗位和轮次',
        icon: 'none'
      })
      return
    }

    // 检查是否已登录
    if (!userInfo) {
      wx.showModal({
        title: '需要登录',
        content: '请先登录后再使用面试功能',
        showCancel: true,
        cancelText: '取消',
        confirmText: '去登录',
        success: (res) => {
          if (res.confirm) {
            // 触发登录
            this.handleLogin()
          }
        }
      })
      return
    }

    // 先刷新用户信息，确保配额数据是最新的
    wx.showLoading({ title: '检查中...' })

    wx.request({
      url: `${app.globalData.baseUrl}/user/${userInfo.user_id}`,
      method: 'GET',
      success: (res) => {
        wx.hideLoading()

        if (res.statusCode === 200) {
          const latestUserInfo = res.data

          // 更新本地用户信息
          app.globalData.userInfo = latestUserInfo
          this.updateUserInfo(latestUserInfo)

          // 检查最新的配额
          const dailyLimit = latestUserInfo.daily_limit || 1
          if (latestUserInfo.vip_type !== 'super' && latestUserInfo.free_count_today >= dailyLimit) {
            // 次数不足，引导用户购买VIP
            wx.showModal({
              title: '今日面试次数已用完',
              content: `今日免费次数已用完（${dailyLimit}次/天）\n\n开通VIP会员，享受更多面试机会！`,
              cancelText: '取消',
              confirmText: '开通VIP',
              confirmColor: '#667eea',
              success: (modalRes) => {
                if (modalRes.confirm) {
                  // 跳转到VIP页面
                  wx.navigateTo({
                    url: '/pages/vip/vip'
                  })
                }
              }
            })
            return
          }

          // 配额充足，继续开始面试
          this.proceedToInterview()
        } else {
          wx.showToast({
            title: '获取用户信息失败',
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

  // 继续开始面试（配额检查通过后）
  proceedToInterview() {
    const { selectedPositionId, selectedPositionName, selectedRound, selectedInterviewerStyle, resume, uploadedResume } = this.data

    // 合并手动输入和上传的简历（优先使用手动输入，否则使用上传的）
    const finalResume = resume || uploadedResume || null

    // 跳转到准备页面，由准备页面负责调用接口和显示动画
    wx.navigateTo({
      url: `/pages/prepare/prepare?position_id=${selectedPositionId}&position_name=${encodeURIComponent(selectedPositionName)}&round=${encodeURIComponent(selectedRound)}&resume=${encodeURIComponent(finalResume || '')}&interviewer_style=${encodeURIComponent(selectedInterviewerStyle || '')}`
    })
  },

  // 旧的实现（已废弃，保留备份）
  startInterviewOld() {
    const { selectedPositionId, selectedPositionName, selectedRound, selectedInterviewerStyle, resume, uploadedResume, userInfo } = this.data

    // 显示加载界面
    this.setData({
      isPreparingInterview: true
    })

    // 合并手动输入和上传的简历
    const finalResume = resume || uploadedResume || null

    // 调用开始面试接口
    const requestUrl = `${app.globalData.baseUrl}/interview/start`
    const requestData = {
      position_id: selectedPositionId,
      position_name: selectedPositionName,
      round: selectedRound,
      user_id: app.globalData.userId || null,
      resume: finalResume,
      interviewer_style: selectedInterviewerStyle || null
    }

    console.log('[开始面试] 请求URL:', requestUrl)
    console.log('[开始面试] 请求数据:', requestData)

    wx.request({
      url: requestUrl,
      method: 'POST',
      timeout: 180000,
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
