// Global variables
let isPlaying = true;
let playInterval;
let currentYearIndex = 0;
// Timeline years for animation: 2000..2025 plus Q1/Q2 of 2025 as fractional years
// Use integer years for axis ticks; append 2025.25 (Q1) and 2025.5 (Q2) for animation range end
let years = Array.from({length: 2025 - 2000 + 1}, (_, i) => 2000 + i).concat([2025.25, 2025.5]);
let tickYears = Array.from({length: 2025 - 2000 + 1}, (_, i) => 2000 + i);
let timeline;
// Scale factor to shorten the overall timeline width for recording
const TIMELINE_WIDTH_SCALE = 0.9; // tweak between 0.7 ~ 1.0 as needed

// Function to create timeline
function createTimeline() {
    const timelineWidth = document.getElementById('timeline').offsetWidth;
    const timelineWidthScaled = Math.max(600, Math.floor(timelineWidth * TIMELINE_WIDTH_SCALE));
    const margin = { left: 20, right: 80 };
    const width = timelineWidthScaled - margin.left - margin.right;

    // Create SVG
    const svg = d3.select('#timeline')
        .append('svg')
        .attr('width', timelineWidthScaled)
        .attr('height', 60);

    const g = svg.append('g')
        .attr('transform', `translate(${margin.left}, 30)`);

    // Create scale
    const xScale = d3.scaleLinear()
        .domain([2000, 2025.5]) // extend to 2025 Q2
        .range([0, width]);

    // Create axis
    const xAxis = d3.axisBottom(xScale)
        .tickFormat(d => d.toString())
        .ticks(tickYears.length)
        .tickValues(tickYears);

    // Add axis
    g.append('g')
        .attr('class', 'timeline-axis')
        .call(xAxis)
        .selectAll('text')
        .style('text-anchor', 'middle')
        .style('font-family', 'Monda')
        .style('font-size', '18px');

    // Make timeline ticks more visible (year ticks)
    g.selectAll('.tick line')
        .style('stroke', '#ccc')
        .style('stroke-width', '1px')
        .attr('y2', '8');

    // Only keep short quarter ticks for 2025 Q1/Q2 (Q1 without label, Q2 with small label)
    const quarterPositions = [];
    quarterPositions.push({ pos: 2025.25, label: null });
    quarterPositions.push({ pos: 2025.5,  label: 'Q2' });

    const qGroup = g.append('g').attr('class', 'quarter-ticks');
    quarterPositions.forEach(q => {
        const x = xScale(q.pos);
        // short tick line (shorter than year tick)
        qGroup.append('line')
            .attr('x1', x)
            .attr('x2', x)
            .attr('y1', 0)
            .attr('y2', 5)
            .attr('stroke', '#ccc')
            .attr('stroke-width', 1);
        if (q.label) {
            qGroup.append('text')
                .attr('x', x)
                .attr('y', 18)
                .attr('text-anchor', 'middle')
                .style('font-family', 'Monda')
                .style('font-size', '12px')
                .style('fill', '#888')
                .text(q.label);
        }
    });

    // Add triangle marker
    const triangle = g.append('path')
        .attr('d', d3.symbol().type(d3.symbolTriangle).size(100))
        .attr('fill', '#4CAF50')
        .attr('transform', `translate(${xScale(years[currentYearIndex])}, -10) rotate(180)`);

    timeline = {
        scale: xScale,
        triangle: triangle
    };
}

// Function to update timeline
function updateTimeline(year) {
    if (timeline && timeline.triangle) {
        timeline.triangle
            .transition()
            .duration(500)
            .attr('transform', `translate(${timeline.scale(year)}, -10) rotate(180)`);
    }
}

// Initialize the visualization
function init() {
    try {
        currentYearIndex = 0;
        createTimeline();
        
        // Optimized animation loop
        setTimeout(() => {
            isPlaying = true;
            let startTime = null;
            const animationDuration = 300000; // 缩短到30秒
            const frameInterval = 16; // 提高帧率到60fps (16.67ms间隔)
            let lastUpdateTime = 0;
            
            function animate(currentTime) {
                if (!isPlaying) return;
                
                if (!startTime) startTime = currentTime;
                const now = currentTime;
                
                // Limit frame rate
                if (now - lastUpdateTime < frameInterval) {
                    requestAnimationFrame(animate);
                    return;
                }
                
                const elapsed = (now - startTime) % animationDuration;
                const progress = elapsed / animationDuration;
                
                // 计算当前年份位置，让2025.25和2025.5也均匀分布
                // 将进度映射到2000-2025.5的完整范围
                const totalRange = 2025.5 - 2000; // 25.5年
                const currentYear = 2000 + progress * totalRange;
                
                // Update timeline marker
                if (timeline && timeline.triangle) {
                    const currentX = timeline.scale(currentYear);
                    timeline.triangle.attr('transform', `translate(${currentX}, -10) rotate(180)`);
                }
                
                lastUpdateTime = now;
                requestAnimationFrame(animate);
            }
            
            requestAnimationFrame(animate);
        }, 500);
        
    } catch (error) {
        console.error('Error initializing visualization:', error);
        document.getElementById('timeline').innerHTML = `
            <div style="color: red; padding: 20px;">
                Error loading visualization: ${error.message}<br>
                Please check the browser console for more details.
            </div>
        `;
    }
}

// Start the visualization when the page loads
document.addEventListener('DOMContentLoaded', init); 