# 服务器命令速查

## 连接服务器
```bash
ssh root@123.57.224.48
cd /root/ai_interview
```

## 本地构建并上传镜像
```bash
# 本地构建
cd /Users/yifeihuang/Documents/ClaudeAPIServicePlat/ai_interview
docker-compose build

# 保存镜像
docker save -o ai_interview_backend.tar ai_interview-interview-backend:latest

# 上传到服务器
scp ai_interview_backend.tar root@123.57.224.48:/root/

# 服务器加载镜像
ssh root@123.57.224.48
docker load -i /root/ai_interview_backend.tar
cd /root/ai_interview
docker-compose up -d
```

## Docker 常用操作
```bash
# 启动/停止/重启
docker-compose up -d
docker-compose down
docker-compose restart

# 查看状态和日志
docker-compose ps
docker-compose logs -f interview-backend
docker-compose logs --tail=100 interview-backend

# 进入容器
docker exec -it ai_interview-interview-backend-1 bash
```

## 测试服务
```bash
# 健康检查
curl http://localhost:8003/health
curl http://123.57.224.48:8003/health

# 测试面试接口
curl -X POST http://123.57.224.48:8003/api/v1/interview/start \
  -H "Content-Type: application/json" \
  -d '{"position":"后端工程师","round":"技术一面"}'
```

## 更新代码
```bash
# 上传项目文件
scp -r ai_interview root@123.57.224.48:/root/

# 重新部署
ssh root@123.57.224.48
cd /root/ai_interview
docker-compose down
docker-compose up -d
```

## 备份数据库
```bash
cp /root/ai_interview/apps/interview_backend/data/ai_interview.db backup_$(date +%Y%m%d).db
```
