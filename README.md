# 香港餐饮 POS 竞品分析（静态站点）

- 最新版入口：docs/index.html（GitHub Pages 会发布它）
- 历史版本：docs/versions/

## 发布到 GitHub Pages（同事无需 GitHub 账号）

1. 在 GitHub 新建 **Public** 仓库（例如 hk-pos-competitive-analysis）。
2. 本地推送本仓库到 GitHub：

`powershell
cd "C:\Users\Administrator\Desktop\hk-pos-competitive-analysis"
git init
git add -A
git commit -m "publish v1.1"
# 把下面 URL 换成你自己的仓库地址
git remote add origin https://github.com/<you>/<repo>.git
git branch -M main
git push -u origin main
`

3. GitHub 仓库里：Settings -> Pages

- Source: Deploy from a branch
- Branch: main
- Folder: /docs

保存后等待 1-2 分钟，会得到一个网址，发给同事直接打开即可。

## 更新流程

- 修改 docs/index.html
- 在 docs/versions/ 里再存一份版本（可选）
- git commit + git push

