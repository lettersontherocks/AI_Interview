// app.js
const config = require('./config.js')

App({
  globalData: {
    userInfo: null,
    userId: null,
    baseUrl: '' // 将在 onLaunch 中动态设置
  },

  onLaunch() {
    // 小程序启动时执行
    console.log('AI面试小程序启动')

    // 动态设置 API 地址
    this.initBaseUrl()

    // 检查登录状态
    this.checkLogin()

    // 清理旧的音频文件
    this.cleanupOldAudioFiles()
  },

  // 初始化 API 地址
  initBaseUrl() {
    const accountInfo = wx.getAccountInfoSync()
    const envVersion = accountInfo.miniProgram.envVersion

    // 根据环境自动切换
    if (envVersion === 'develop') {
      // 开发版：从配置文件读取
      const devMode = config.currentDevMode
      this.globalData.baseUrl = config.development[devMode]
      console.log(`开发环境：使用 ${devMode} 模式 - ${this.globalData.baseUrl}`)
    } else if (envVersion === 'trial') {
      // 体验版：使用线上地址
      this.globalData.baseUrl = config.production.apiUrl
      console.log('体验版环境：使用线上地址')
    } else if (envVersion === 'release') {
      // 正式版：使用线上地址
      this.globalData.baseUrl = config.production.apiUrl
      console.log('生产环境：使用线上地址')
    } else {
      // 兜底方案
      this.globalData.baseUrl = config.development.localhost
      console.log('未知环境：使用 localhost')
    }
  },

  // 检查登录状态
  checkLogin() {
    const userId = wx.getStorageSync('userId')
    if (userId) {
      this.globalData.userId = userId
      this.getUserInfo(userId)
    }
  },

  // 获取用户信息
  getUserInfo(userId) {
    wx.request({
      url: `${this.globalData.baseUrl}/user/${userId}`,
      method: 'GET',
      success: (res) => {
        if (res.statusCode === 200) {
          this.globalData.userInfo = res.data
        }
      }
    })
  },

  // 微信登录
  wxLogin(callback) {
    console.log('开始微信登录流程...')
    console.log('当前API地址:', this.globalData.baseUrl)

    // 第一步：获取用户信息（头像、昵称）
    wx.getUserProfile({
      desc: '用于完善用户资料',
      success: (profileRes) => {
        console.log('✅ 获取用户信息成功:', profileRes.userInfo)
        const { nickName, avatarUrl } = profileRes.userInfo

        // 第二步：获取登录凭证 code
        wx.login({
          success: (loginRes) => {
            console.log('✅ wx.login成功，code:', loginRes.code)
            if (loginRes.code) {
              // 发送 code 到后台换取 openId
              this.registerUser(loginRes.code, nickName, avatarUrl, callback)
            } else {
              console.error('❌ 获取code失败:', loginRes.errMsg)
              wx.showModal({
                title: '登录失败',
                content: '获取微信登录凭证失败，请重试',
                showCancel: false
              })
            }
          },
          fail: (err) => {
            console.error('❌ wx.login失败:', err)
            wx.showModal({
              title: '登录失败',
              content: `wx.login调用失败: ${err.errMsg}`,
              showCancel: false
            })
          }
        })
      },
      fail: (err) => {
        console.error('❌ 获取用户信息失败:', err)
        wx.showModal({
          title: '需要授权',
          content: '请授权获取您的头像和昵称，以便使用面试功能',
          showCancel: false
        })
      }
    })
  },

  // 注册用户（通过微信code换取openid）
  registerUser(code, nickname, avatar, callback) {
    const url = `${this.globalData.baseUrl}/user/wx-login`
    console.log('准备发送登录请求到:', url)
    console.log('请求数据:', { code, nickname, avatar })

    wx.request({
      url: url,
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      data: {
        code: code,
        nickname: nickname,
        avatar: avatar
      },
      success: (res) => {
        console.log('登录请求成功，状态码:', res.statusCode)
        console.log('响应数据:', res.data)

        if (res.statusCode === 200) {
          const userId = res.data.user_id
          this.globalData.userId = userId
          this.globalData.userInfo = res.data
          wx.setStorageSync('userId', userId)

          wx.showToast({
            title: '登录成功',
            icon: 'success'
          })

          if (callback) callback(res.data)
        } else {
          console.error('登录失败，状态码:', res.statusCode, '响应:', res)

          // 详细的错误信息
          let errorMsg = '登录失败'
          if (res.data && res.data.detail) {
            errorMsg = res.data.detail
          } else if (res.statusCode === 400) {
            errorMsg = '获取微信openid失败，请检查小程序配置'
          } else if (res.statusCode === 500) {
            errorMsg = '服务器错误，请稍后重试'
          }

          wx.showModal({
            title: '登录失败',
            content: errorMsg,
            showCancel: false,
            confirmText: '知道了'
          })
        }
      },
      fail: (err) => {
        console.error('登录请求失败:', err)
        wx.showModal({
          title: '网络错误',
          content: `无法连接到服务器\n地址: ${url}\n错误: ${err.errMsg}`,
          showCancel: false
        })
      }
    })
  },

  // 清理旧的音频文件
  cleanupOldAudioFiles() {
    const fs = wx.getFileSystemManager()
    const userDataPath = wx.env.USER_DATA_PATH

    try {
      // 读取用户数据目录下的所有文件
      fs.readdir({
        dirPath: userDataPath,
        success: (res) => {
          const audioFiles = res.files.filter(file => file.startsWith('tts_') && file.endsWith('.mp3'))

          if (audioFiles.length === 0) {
            console.log('[全局音频清理] 无音频文件需要清理')
            return
          }

          console.log(`[全局音频清理] 发现 ${audioFiles.length} 个音频文件`)

          let cleanedCount = 0
          let failedCount = 0
          const now = Date.now()
          const ONE_DAY = 24 * 60 * 60 * 1000 // 24小时

          audioFiles.forEach(fileName => {
            const filePath = `${userDataPath}/${fileName}`

            try {
              // 获取文件信息
              const stat = fs.statSync(filePath)
              const fileAge = now - stat.mtime

              // 删除超过24小时的音频文件
              if (fileAge > ONE_DAY) {
                fs.unlinkSync(filePath)
                cleanedCount++
                console.log(`[全局音频清理] 已删除旧文件: ${fileName} (${Math.floor(fileAge / ONE_DAY)}天前)`)
              }
            } catch (err) {
              failedCount++
              console.warn(`[全局音频清理] 处理文件失败 (${fileName}):`, err.errMsg)
            }
          })

          console.log(`[全局音频清理] 完成 - 清理: ${cleanedCount}, 保留: ${audioFiles.length - cleanedCount - failedCount}, 失败: ${failedCount}`)
        },
        fail: (err) => {
          console.warn('[全局音频清理] 读取目录失败:', err.errMsg)
        }
      })
    } catch (err) {
      console.warn('[全局音频清理] 初始化失败:', err)
    }
  }
})
