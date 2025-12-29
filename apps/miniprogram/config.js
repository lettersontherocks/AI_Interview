// 环境配置文件
module.exports = {
  // 开发环境配置
  development: {
    // 开发者工具预览时使用（localhost）
    localhost: 'http://localhost:8003/api/v1',
    // 真机调试时使用（局域网IP，需要手动修改为你的电脑IP）
    localNetwork: 'http://10.136.186.248:8003/api/v1',
    // 阿里云服务器地址（HTTP，临时测试用）
    aliyun: 'http://123.57.224.48:8003/api/v1'
  },

  // 生产环境配置
  production: {
    // 线上服务器地址（需要 HTTPS + 备案域名）
    // 暂时使用 HTTP 进行测试，后续需要配置 HTTPS
    apiUrl: 'http://123.57.224.48:8003/api/v1'
  },

  // 当前使用的开发环境模式
  // 可选值: 'localhost' | 'localNetwork' | 'aliyun'
  // 阿里云测试请使用 'aliyun'
  currentDevMode: 'aliyun'
}
