# How to Complete the Racing Bar Visualization with Plotly

Peter, Oct 2025

## The full project deck should contain the following components:

1. **Original Data Source**: [Animated Bubble Chart: Historic Financials Aviation Industry](https://docs.google.com/spreadsheets/d/1Jrx8L6fFqix5yyc-NPgbRCw8FkSG1ty890aBh7byu1o/view?gid=544316000#gid=544316000)
2. **Main Visualization Script**: [./airline_plotly_viz.py](./airline_plotly_viz.py) - generates the main animated plot
3. **Timeline Component Script**: [../02.project-web-in-travel/web_timeline/index.html](../02.project-web-in-travel/web_timeline/index.html) - open this `index.html` with `Live Server` to grant it access to other files, otherwise you can't see anything
   - `Live Server` is a VS Code extension that needs to be installed
4. **Supporting Materials**: [../99.utility/airline-bar-video](../99.utility/airline-bar-video) - contains logos and other graphic materials

## Production Workflow

(This is a quick walkthrough; detailed instructions are provided in the "First Time Setup" section below)

The entire project is essentially screen recording and video editing, consisting of 5 components:

1. **Racing Bar Chart** - Code generates HTML, then screen record
2. **Timeline** - Modify HTML-dependent JS, open HTML, then screen record
3. **Colored Map** - Image materials (screenshots, not original images)
4. **News Comments Graphics** (fade in/out) - Edit in PowerPoint, then screenshot
5. **Persistent Footer Text** - Insert directly in video editing software

## First Time Setup

**Strongly recommend using Cursor for assisted editing**
**I don't have complete first-hand materials, so my approach may not be the perfect choice**

Let's answer two key questions first:

### Q: Where do the data and materials come from?

**A:**

- Export `TTM(bounded)` sheet as `.csv` for original data. Rename it to `airlines_final.csv` and place it in the [../99.utility/airline-bar-video](../99.utility/airline-bar-video) folder
  ![Data Export Process](https://drive.google.com/PLACEHOLDER_DATA_EXPORT.png)

  FYI: TTM (Trailing Twelve Months) divides annual data by 4 to generate quarterly data, then sums the last 4 quarters. If you need to verify data, check `Quarterly Revenue&EBITDA` and `Raw: Annual Revenue/EBITDA`.
- Use `Timeline` sheet for news comments

### Q: Do I only need to splice the latest two quarters of video? How to maintain consistency in material composition?

**A:** Browsers can hardly generate completely identical materials (colors, brightness, aliasing), so you cannot just update the latest two quarters of materials. You must record each component from scratch and edit them together. Of course, Ned may also request modifications to previous materials.

Use **Eloquia Display Regular** as the font (I'm not certain about the exact font name)

### Q: What if I'm missing certain materials?

**A:** Can be a segment, frozen frame, or screenshot from the previous video. You can use chroma key (green screen method) to remove gray grid lines. Some news materials were obtained using this method.

![Chroma Key Process](https://drive.google.com/PLACEHOLDER_CHROMA_KEY.png)

**Important Notes:**

- Chroma key requires correct chroma, edge feathering, and blur settings
- Chroma too high will remove gray from news screenshots
- Edge feathering and blur too high will make the entire image blurry (some blur is inevitable to remove grid lines)
- Gradually increase chroma, feathering, and blur until grid lines are removed
- **Critical:** The standard for judging whether grid lines are removed is NOT the video editing software preview (because preview is low resolution). You must leave margin and check the final exported video to see if grid lines are visible.

## Code Modification Guidelines

1. **Pixel Density Warning**: Any element cannot have too few pixels, otherwise the browser's anti-aliasing function will blur edge pixels, causing obvious thickness changes and flickering
