# GitHub 高级展示指南

## 1. 最简展示块（推荐）

```markdown
## 2021A Optical Optimization Showcase

![](2021A_optimized_showcase/outputs/gifs/github_cover.gif)
![](2021A_optimized_showcase/outputs/images/dashboard.png)
```

## 2. 全量展示块（含过程动画）

```markdown
## 2021A Optical Optimization Showcase

![](2021A_optimized_showcase/outputs/gifs/github_cover.gif)

<details>
<summary>查看参数演化过程</summary>

![](2021A_optimized_showcase/outputs/gifs/process_sweep.gif)

</details>

![](2021A_optimized_showcase/outputs/images/dashboard.png)
```

## 3. 提升高级感的排版技巧

1. 第一屏只放一个主 GIF，避免信息过载。
2. 第二屏放仪表板图，形成“动 + 静”节奏。
3. 将长文说明折叠到 `details`，突出视觉主线。
4. 用 `summary.json` 自动更新关键指标，避免手改。
