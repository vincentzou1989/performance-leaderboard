#!/usr/bin/env bash
# 部署到 GitHub Pages（公开）
# 用法: bash deploy.sh <GitHub用户名> <Personal Access Token> [仓库名]
# PAT 需要 repo 权限。脚本会创建公开仓库、推送 main 分支并开启 Pages。
set -e

USER="$1"
TOKEN="$2"
REPO="${3:-performance-leaderboard}"

if [ -z "$USER" ] || [ -z "$TOKEN" ]; then
  echo "用法: bash deploy.sh <GitHub用户名> <PAT> [仓库名]"
  exit 1
fi

echo "==> 创建公开仓库 $REPO ..."
curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"$REPO\",\"description\":\"坐席绩效业绩排行榜\",\"auto_init\":false,\"private\":false}" \
  https://api.github.com/user/repos >/dev/null || true

echo "==> 配置远程并推送 ..."
git remote remove origin >/dev/null 2>&1 || true
git remote add origin "https://$USER:$TOKEN@github.com/$USER/$REPO.git"
git branch -M main
git push -u origin main

echo "==> 开启 GitHub Pages（main 分支根目录）..."
# Pages 可能在首次推送后稍迟就绪，失败可稍后手动开启
sleep 6
curl -s -X POST \
  -H "Authorization: token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"source":{"branch":"main","path":"/"}}' \
  https://api.github.com/repos/$USER/$REPO/pages >/dev/null || echo "Pages 创建稍后请到仓库 Settings > Pages 手动开启"

echo ""
echo "完成！稍候 1-2 分钟构建后访问："
echo "  https://$USER.github.io/$REPO/"
