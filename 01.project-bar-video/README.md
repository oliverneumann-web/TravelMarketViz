# How to Complete the Racing Bar Visualization with Plotly

Peter, Oct 2025

## The full project deck should contain the following components:

1. **Original Data Source**: [Animated Bubble Chart: Historic Financials Aviation Industry](https://docs.google.com/spreadsheets/d/1Jrx8L6fFqix5yyc-NPgbRCw8FkSG1ty890aBh7byu1o/view?gid=544316000#gid=544316000)
2. **Main Visualization Script**: [./airline_plotly_viz.py](./airline_plotly_viz.py) - generates the main animated plot
3. **Timeline Component Script**: [../02.project-web-in-travel/web_timeline/index.html](../02.project-web-in-travel/web_timeline/index.html) - open this `index.html` with `Live Server` to grant it access to other files, otherwise you can't see anything
   - `Live Server` is a VS Code extension that needs to be installed
4. **Supporting Materials**: [../99.utility/airline-bar-video](../99.utility/airline-bar-video) - contains logos and other graphic materials. We can visit [Google Drive](https://drive.google.com/drive/folders/14BTHi1ul925V-JyWS1wE7BEZznGh6ynu?usp=sharing) to download my folder.

As well as

5. **Code Editor**: VScode / Cursor / Pycharm
6. **Screen Recording Software**: macOS native screen recorder / OBS / Nvidia graphics card recorder (win+G)
7. **Video Editing Software**: FinalCutPro trial / 必剪
8. **Image Editing Software**: I use PPT + [web-based Photopea](https://www.photopea.com) to combine news graphics and remove backgrounds (I find this much simpler than inserting text and images separately in video editing software)

## Production Workflow

(This is a quick walkthrough; detailed instructions are provided in the "First Time Setup" section below)

The entire project is essentially screen recording and video editing, consisting of 5+1 components:

1. **Racing Bar Chart** - Code generates HTML, then screen record
2. **Timeline** - Modify HTML-dependent JS, open HTML, then screen record
3. **Colored Map** - Image materials (screenshots, not original images)
4. **News Comments Graphics** (fade in/out) - Edit in PowerPoint, then screenshot
5. **Footer Notes** (persistent) - Insert directly in video editing software
6. **White Background** - Place at the bottom layer

Then we need to combine the components in video editing software and align the timeline. Please note,

## First Time Setup

**Strongly recommend using Cursor for assisted editing**
**I don't have complete first-hand materials, so my approach may not be the perfect choice**

Let's answer a few key questions first:

### Q: Where do the data and materials come from?

**A:**

- Export `TTM(bounded)` sheet as `.csv` for original data. Rename it to `airlines_final.csv` and place it in the [../99.utility/airline-bar-video](../99.utility/airline-bar-video) folder

  FYI: TTM (Trailing Twelve Months) divides annual data by 4 to generate quarterly data, then sums the last 4 quarters. If you need to verify data, check `Quarterly Revenue&EBITDA` and `Raw: Annual Revenue/EBITDA`.
- Use `Timeline` sheet for news comments and images

### Q: How to run this code?
**A:** First, make sure we have cloned this repository, and visit [Google Drive](https://drive.google.com/drive/folders/14BTHi1ul925V-JyWS1wE7BEZznGh6ynu?usp=sharing) to download the missing folders from the repository (to save Github storage quota), and move them to the correct location. Then, we must **cd first** to [../01.project-bar-video](./) , then run [../01.project-bar-video/airline_plotly_viz.py](./airline_plotly_viz.py)

If you don't quite understand, let me put it this way: If we are now using VScode/Cursor, we should open the `TRAVELMARKETVIZ` folder (because git records are under the main folder). At this time, our working folder is `TRAVELMARKETVIZ`. If we now find [../01.project-bar-video/airline_plotly_viz.py](./airline_plotly_viz.py) and click run, it will report an error due to incorrect path (because the relative path in the code starts from `.py`, first goes out to find `TRAVELMARKETVIZ` and then goes down, rather than standardly taking the outer folder as the working folder and going down directly; or the design concept is to cd first, not to run directly).

So, if we now standardly use VScode/Cursor to open `TRAVELMARKETVIZ`, we should first
`cd /01.project-bar-video`
(If we open the command line software directly on the desktop, we need to cd to the complete directory)
Then
`py airline_plotly_viz.py`

### Q: Do I only need to splice the latest two quarters of video? How to maintain consistency in material composition?

**A:** Browsers can hardly generate completely identical materials (affected by color, brightness, aliasing), so we cannot just update the latest two quarters of materials and add them to the end of the video. We must record each component from scratch and edit them together. Of course, Ned may also request new modifications to previous materials - redoing everything is inevitable. However, for previous news graphics, we can indeed take a shortcut - use chroma key to extract them (see the next question for details) instead of making them ourselves.

To maintain consistency, use **Eloquia Display Regular** as the font (my guess). But this font costs money. If we don't want to pay, download **Eloquia Display Extra Bold** and **Eloquia Text Extra Light**. Unfortunately, bolded extra light cannot fully mimic regular, but we've tried our best.

### Q: What if I'm missing certain materials?

**A:** Can be a segment, frozen frame, or screenshot from the previous video. We can use chroma key (i.e., green screen method) to remove gray grid lines. Some news materials were obtained using this method.

**Important Notes:**

- Chroma key requires correct chroma, edge feathering, and blur settings
- Chroma too high will additionally remove gray from news screenshots, causing image fragmentation
- Edge feathering or blur too high will make the entire image blurry (some blur is inevitable to remove grid lines)
- Gradually increase chroma, feathering, and blur until grid lines are removed
- **Critical:** The standard for judging whether grid lines are removed is NOT the video editing software preview (because preview is low resolution). We must leave margin and check **in the final exported video** whether grid lines are visible.

### Q: Are there any standards for video editing?

**A:** Graphics can be set like this: Total duration 4s, fade in and out 1 second each, so that the time point when fade-in is complete (100% brightness) is approximately when the data changes correspondingly (large movement, logo change). Please note that we don't need to arrange news strictly by real dates. What matters is to fit in all the news Ned wants to show while trying to ensure **news can explain data changes at that time**. If there is a lot of news in a certain period, they can be moved forward or backward by a few months in the video, or the display duration can be appropriately shortened.

## Code Modification Guidelines

1. **Thicken line width to prevent flickering**: Any element cannot have too few pixels, otherwise the browser's anti-aliasing function will blur edge pixels, causing obvious thickness changes and flickering
2. **Display names and unique names of airlines**

Please note how we currently handle **airline mergers**. In the source data `TTM(bounded)` sheet, we have manually deleted the data of smaller airlines that merged, and only record the data in the larger airline's column. For example, `AF` and `KL` merged into `AF/KL` in May 2004, so the `AF` and `KL` columns never have data, while the `AF/KL` column shows the data of the previously higher-revenue airline `AF` before the merger. Therefore, the data is continuous, the change is obvious, and we only need to modify the displayed IATA code and logo at the appropriate time. Here, `AF/KL` is the unique name of the data (column name/index), while the previous `AF` and the subsequent `AF/KL` are the display names we set.

However, because we only have quarterly data, the code maps months to March, June, September, and December, so if we set `switch to AF/KL when greater than May 2004`, then at the beginning of the second quarter animation, i.e., April, because the month of the second quarter is June, which satisfies `greater than May 2004`, the display name will change. To avoid this ambiguity, I artificially moved it back by one quarter to avoid displaying before the merger.

FYI, this setting is first to simplify the code, and second because the merged airline is not a new entrant, so it should not be shown as a small airline exiting the market (decreasing to 0) and a large airline entering the market (growing from 0), but should directly "pick the peach" and transform on the spot at the point of change. Distinguishing display names and unique names is the simplest method I think. The only disadvantage is that, to reduce code modifications, I did not choose to write a separate `.js` file to record this change, but hardcoded it in the function `update_display_names_for_quarter`.

3. **Bar chart logic overview**

The entire animation can be understood as interpolated frames between two frames drawn for two quarters. We did not set complex logic, but simply and crudely redraw each frame and rank within each frame. Therefore, the entire html is very large, essentially using `.py` to generate `.html` with hardcoded each frame (including logos). In most cases, don't try to overthrow this logic, I don't know what will happen either.

I fixed a bug: This bug used to cause interpolation between frames to be based on the "nth place" of each of the two frames, and refresh the name and logo of the "nth place" when switching quarters, rather than interpolating based on the airline's own numbers. For example, `AF` grows from 1 to 4, while `BA` grows from 2 to 3, the animation would let the first place bar slowly grow from 2 to 4, and always display `AF` during quarterly interpolation, and finally when it fully grows to 4, switch to `BA`. This makes the inter-quarter animation not actually correspond to the displayed airline, and causes very obvious "jumps" (rankings suddenly change significantly, and there is no intermediate state where two bars meet). Now, bars will correctly grow and move based on the airline's own data. I believe the code will no longer cause such "jumps"; if there are, please first check if it is an error in the source data (abnormal data will present abnormal rankings, visually approximating "jumps").

4. **Testing phase and production phase**

In the testing phase, we can search for `const quarterDuration` and modify it to 200 (unit is ms) for quick preview. In the production phase, please restore it to the default value 3000. This ensures smoother animation and gives us more lead time to open the screen recording software. After drawing is complete, the `.html` file will automatically be opened with a browser. We can also double-click the file in the folder to open it.

Please note that if we use Nvidia or automatic window capture, do not start recording on the code editor page and wait for the webpage to open automatically - screen recording will lock the editor window. Must wait for the webpage to open, then press Win+G to start screen recording. The code will start drawing from 1997, we only need to start the screen recording software before 2000.

5. **Logo display**

Logo display has two logics: one is to display different logos at different times, and the other is to make each logo (text in the logo) visually about the same size. Therefore, the logo workflow is relatively detailed:
1. Search and download logo images at [https://logos-world.net/], fill in the applicable years and paths in `logo_mapping` (the code will use the new logo in the first quarter of `start year`, not accurate enough, but it's troublesome so I didn't change it)
2. When filling in, note that old images are `.png`, while the latest images are often `.jpeg`. It may be that new images reuse header material and have different logic. Check when writing paths, don't write it wrong.
3. Use [https://www.photopea.com/] to crop images and remove backgrounds (because the animation background is white, so after cropping well you generally don't need to remove the background, if you remove the background you must save as `.png`). Cropping white borders is to make the logo fit the real logo pattern as much as possible.
4. Adjust `logo_sizes` according to the real layout of logo icons and text to make logos look about the same size. For example, Emirates has small text so adjust it larger.
