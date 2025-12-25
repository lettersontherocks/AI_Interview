// 环境配置文件
module.exports = {
  // 开发环境配置
  development: {
    // 开发者工具预览时使用（localhost）
    localhost: 'http://localhost:8003/api/v1',
    // 真机调试时使用（局域网IP，需要手动修改为你的电脑IP）
    localNetwork: 'http://10.136.186.248:8003/api/v1',
    // ngrok 内网穿透地址（临时测试用）
    ngrok: 'https://your-ngrok-id.ngrok.io/api/v1'
  },

  // 生产环境配置
  production: {
    // 线上服务器地址（需要 HTTPS + 备案域名）
    apiUrl: 'https://your-domain.com/api/v1'
  },

  // 当前使用的开发环境模式
  // 可选值: 'localhost' | 'localNetwork' | 'ngrok'
  currentDevMode: 'localhost'
}
