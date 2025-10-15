# Racing Bar可视化项目指南

Peter, 2025年10月

## 完整项目套件应包含以下组件：

1. **原始数据源**: [动画气泡图：航空业历史财务数据](https://docs.google.com/spreadsheets/d/1Jrx8L6fFqix5yyc-NPgbRCw8FkSG1ty890aBh7byu1o/view?gid=544316000#gid=544316000)
2. **主要可视化脚本**: [./airline_plotly_viz.py](./airline_plotly_viz.py) - 生成主要动画图表
3. **时间轴组件脚本**: [../02.project-web-in-travel/web_timeline/index.html](../02.project-web-in-travel/web_timeline/index.html) - 使用 `Live Server` 打开此 `index.html` 文件以授予其访问其他文件的权限，否则无法显示内容
   - `Live Server` 是一个需要安装的 VS Code 扩展
4. **辅助材料**: [../99.utility/airline-bar-video](../99.utility/airline-bar-video) - 包含标志和其他图形材料

## 工作流程

（这是一个快速概览；详细说明请查看下面的"首次设置"部分）

整个项目本质上是屏幕录制和视频编辑，由5个组件组成：

1. **竞赛条形图** - 代码生成HTML，然后屏幕录制
2. **时间轴** - 修改HTML依赖的JS，打开HTML，然后屏幕录制
3. **彩色地图** - 图像材料（截图，非原始图像）
4. **新闻评论图形**（淡入淡出） - 在PowerPoint中编辑，然后截图
5. **页脚注释**（常驻）- 直接在视频编辑软件中插入

## 首次设置

**强烈建议使用 Cursor 进行辅助编辑**
**我没有完整的第一手材料，所以我的方法可能不是最佳选择**

让我们先回答几个关键问题：

### 问题：数据和材料从哪里来？

**答案：**

- 导出 `TTM(bounded)` 工作表为 `.csv` 格式获取原始数据。将其重命名为 `airlines_final.csv` 并放置在 [../99.utility/airline-bar-video](../99.utility/airline-bar-video) 文件夹中
  ![数据导出过程](https://drive.google.com/PLACEHOLDER_DATA_EXPORT.png)

  仅供参考：TTM（过去12个月）将年度数据除以4生成季度数据，然后汇总最近4个季度。如果需要验证数据，请查看 `Quarterly Revenue&EBITDA` 和 `Raw: Annual Revenue/EBITDA`。
- 使用 `Timeline` 工作表获取新闻评论

### 问题：我只需要拼接最新的两个季度视频吗？如何保持材料组合的一致性？

**答案：** 浏览器几乎无法生成完全相同的材料（颜色、亮度、锯齿），所以你不能只更新最新的两个季度材料。你必须从头开始录制每个组件并一起编辑。当然，Ned也可能对之前的材料提出新的修改要求。

使用 **Eloquia Display Regular** 作为字体（我不确定确切的字体名称）

### 问题：如果我缺少某些材料怎么办？

**答案：** 可以是前一个视频的片段、冻结帧或截图。你可以使用色度抠图（即抠绿幕）的方法去除灰色网格线。一些新闻材料就是通过这种方法获得的。

![色度键处理过程](https://drive.google.com/PLACEHOLDER_CHROMA_KEY.png)

**重要注意事项：**

- 色度键需要正确的色度、边缘羽化和模糊设置
- 色度过高会额外去除新闻截图中的灰色，让图片破碎
- 边缘羽化或模糊过高会使整个图像模糊（为了去除网格线，一些模糊是不可避免的）
- 逐步增加色度、羽化和模糊，直到网格线被去除
- **关键：** 判断网格线是否被去除的标准不是视频编辑软件的预览（因为预览是低分辨率的）。你必须留有余量，并检查最终导出的视频中是否能看到网格线。

## 代码修改指南

1. **像素密度警告**：任何元素的像素都不能太少，否则浏览器的抗锯齿功能会模糊边缘像素，导致明显的粗细变化和闪烁
