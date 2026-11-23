# Automation · 自动化说明

本仓库有两个工作流，都只使用 GitHub 自动提供的 `GITHUB_TOKEN`，**不需要配置任何 Secret**。

| 工作流 | 文件 | 触发 | 权限 |
| --- | --- | --- | --- |
| Contribution snake | `.github/workflows/snake.yml` | 每天 00:17 UTC、手动、修改该文件时 | `contents: write`（仅用于推送 `output` 分支） |
| README checks | `.github/workflows/readme-check.yml` | 修改 Markdown 时、每周一 03:23 UTC、手动 | `contents: read` |

## 首次启用

1. 推送后打开仓库的 **Actions** 页，如果提示工作流被禁用，点击启用。
2. 进入 **Contribution snake**，点 **Run workflow** 手动运行一次。
3. 运行成功后仓库会多出 `output` 分支，里面有两张 SVG。
4. 编辑 `README.md`：删除 `<!-- SNAKE:START …` 和 `SNAKE:END -->` 这两行注释标记，并删掉下面的 "Coming soon" 一行。
5. 删除 `.lycheeignore` 里的那条规则，让链接检查覆盖贪吃蛇图片。

## 排查

### Contribution snake

| 现象 | 原因与处理 |
| --- | --- |
| 发布步骤报 403 / `Permission denied` | **Settings → Actions → General → Workflow permissions** 被限制为只读且禁止工作流提权。改为 "Read and write permissions"，或确认组织/账号策略允许工作流声明 `contents: write`。 |
| 生成步骤报 API 错误或限流 | 多为 GitHub API 临时问题，重新运行即可。 |
| 图片没更新 | GitHub 图片代理有缓存，通常几分钟到几小时内刷新。 |
| 定时任务不再运行 | 仓库连续 60 天没有活动时 GitHub 会停用定时工作流，到 Actions 页重新启用。 |

### README checks

| 现象 | 原因与处理 |
| --- | --- |
| Markdown format 失败 | 日志会给出规则编号（如 `MD032`）和行号，按提示修改；确属版式需要的规则在 `.markdownlint-cli2.yaml` 中关闭并写明原因。 |
| Links and images 失败 | 日志列出失败的 URL。先在浏览器确认是否真的失效；第三方服务（统计卡、打字效果）临时不可用时重新运行即可。若某服务长期不稳定，把对应区块从 README 移除，而不是忽略检查。 |

## Action 版本

以下主版本号于 2026-11-23 核对为各项目的最新发布线：

| Action | 使用的版本 |
| --- | --- |
| `actions/checkout` | `v7` |
| `Platane/snk/svg-only` | `v3` |
| `crazy-max/ghaction-github-pages` | `v5` |
| `DavidAnson/markdownlint-cli2-action` | `v25` |
| `lycheeverse/lychee-action` | `v2` |
