<template>
  <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-xl font-semibold text-wego-gray">Bar Chart Revenue Analysis (TTM, in Millions)</h2>
    </div>
    <div ref="chartContainer" class="h-[840px]"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import * as d3 from 'd3'
import Papa from 'papaparse'
import { companyNames, getCompanyColor, getCompanyLogo } from '../data/companyMeta'

// Define props to receive current period and selected companies from parent
const props = defineProps({
  currentPeriod: {
    type: String,
    default: ''
  },
  selectedCompanies: {
    type: Object,
    default: () => ({})
  }
})

const chartContainer = ref(null)
const chartData = ref([])
const periods = ref([])

// Helper function to check if component is visible (v-show)
const isComponentVisible = () => {
  if (!chartContainer.value) return false;
  // Check if element is visible (v-show sets display:none when hidden)
  return chartContainer.value.offsetParent !== null;
};

// company colors, names, and logos are centralized in src/data/companyMeta.js

const importFromGoogleSheet = async () => {
  // Google Sheets ID and GID for bar chart data
  // open in browser: https://docs.google.com/spreadsheets/d/e/2PACX-1vQYwQTSYwig7AZ0fjPniLVfUUJnLz3PP4f4fBtqkBNPYqrkKtQyZDaB99kHk2eCzuCh5i8oxTPCHeQ9/pub?gid=621483928
  const sheetId = '2PACX-1vQYwQTSYwig7AZ0fjPniLVfUUJnLz3PP4f4fBtqkBNPYqrkKtQyZDaB99kHk2eCzuCh5i8oxTPCHeQ9'
  const gid = '621483928'
  const sheetUrl = `https://docs.google.com/spreadsheets/d/e/${sheetId}/pub?gid=${gid}&output=csv`
  
  try {
    console.log('Starting Google Sheet import for bar chart...')
    console.log('Sheet URL:', sheetUrl)
    
    const response = await fetch(sheetUrl)
    console.log('Response status:', response.status)
    
    if (!response.ok) {
      throw new Error(`Failed to fetch data: ${response.status} ${response.statusText}`)
    }
    
    const csvText = await response.text()
    console.log('CSV Text length:', csvText.length)
    console.log('First 100 chars of CSV:', csvText.substring(0, 100))
    
    const parsedData = Papa.parse(csvText, { 
      header: true,
      skipEmptyLines: true,
      transformHeader: (header) => header.trim()
    })
    
    console.log('Parsed data rows:', parsedData.data.length)
    console.log('Sample parsed data:', parsedData.data.slice(0, 2))
    
    if (parsedData.errors.length > 0) {
      console.warn('Parse errors:', parsedData.errors)
    }
    
    // Process the data
    chartData.value = processData(parsedData.data)
    console.log('Processed chart data:', chartData.value.slice(0, 2))
    
    periods.value = [...new Set(chartData.value.map(d => d.period))]
    console.log('Available periods:', periods.value)
    
    // Initial render will be triggered by watch on props.currentPeriod
    console.log('Data loaded, waiting for currentPeriod prop...')
  } catch (error) {
    console.error('Error importing from Google Sheet:', error)
  }
}

const processData = (rawData) => {
  const result = [];
  const quarterPattern = /^\d{4}'Q[1-4]$/;

  console.log('Processing raw data:', {
    totalRows: rawData.length,
    firstRow: rawData[0],
    secondRow: rawData[1]
  });

  const revenueTtmIndex = rawData.findIndex(row => {
    if (!row) return false;
    const label = typeof row[''] === 'string' ? row[''].trim() : row[''];
    return label === 'Revenue TTM';
  });

  const dataStartIndex = revenueTtmIndex >= 0 ? revenueTtmIndex + 1 : 1;
  if (revenueTtmIndex === -1) {
    console.warn('Revenue TTM row not found. Processing all rows after header.');
  } else {
    console.log('Revenue TTM row found at index:', revenueTtmIndex, 'Data starts at:', dataStartIndex);
  }

  for (let i = dataStartIndex; i < rawData.length; i++) {
    const row = rawData[i];
    if (!row) continue;

    const periodRaw = row[''];
    if (!periodRaw) continue;
    const period = periodRaw.toString().trim();
    if (!quarterPattern.test(period)) {
      console.log('Skipping non-quarter row:', periodRaw);
      continue;
    }

    Object.entries(row).forEach(([company, value]) => {
      if (company === '' || company === undefined || company === null) return; // skip period column
      if (value === undefined || value === null || value === '') return;

      const cleanValue = value.toString().trim().replace(/[$,\s]/g, '');
      const numValue = parseFloat(cleanValue);
      if (!Number.isFinite(numValue) || numValue <= 0) return;

      result.push({
        period,
        company,
        value: numValue
      });
    });
  }

  console.log('Processed data summary:', {
    totalItems: result.length,
    uniquePeriods: [...new Set(result.map(d => d.period))],
    uniqueCompanies: [...new Set(result.map(d => d.company))],
    sample: result.slice(0, 5)
  });

  return result;
}

const renderChart = (forceRender = false) => {
  console.log('renderChart called for period:', props.currentPeriod, 'forceRender:', forceRender)
  
  // Check if component is visible before rendering (unless forced)
  if (!forceRender && !isComponentVisible()) {
    console.log('BarChart not visible, skipping render')
    return
  }
  
  if (!chartContainer.value) {
    console.error('Chart container not found')
    return
  }
  
  if (!props.currentPeriod) {
    console.warn('No current period specified')
    return
  }
  
  // Clear previous chart
  d3.select(chartContainer.value).selectAll('*').remove()
  
  // Filter data for current period and selected companies
  const currentData = chartData.value
    .filter(d => {
      const isPeriodMatch = d.period === props.currentPeriod;
      const isCompanySelected = Object.keys(props.selectedCompanies).length === 0 || 
                                props.selectedCompanies[d.company] === true;
      return isPeriodMatch && isCompanySelected;
    })
    .sort((a, b) => b.value - a.value)
    .slice(0, 15) // Show top 15 companies
  
  if (currentData.length === 0) {
    console.warn('No data available for current period')
    d3.select(chartContainer.value)
      .append('div')
      .attr('class', 'text-center py-8 text-gray-500')
      .text('No data available for this period')
    return
  }
  
  // Set up dimensions with more space for logos
  const margin = { top: 20, right: 160, bottom: 40, left: 250 } // Increased right margin for larger logos
  const width = chartContainer.value.clientWidth - margin.left - margin.right
  const height = chartContainer.value.clientHeight - margin.top - margin.bottom
  
  // Create SVG with explicit dimensions
  const svg = d3.select(chartContainer.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)
  
  // Set up scales - support both positive and negative values
  const minValue = d3.min(currentData, d => d.value) || 0;
  const maxValue = d3.max(currentData, d => d.value) || 0;
  
  // Add 10% padding on both sides
  const domainMin = minValue < 0 ? minValue * 1.1 : 0;
  const domainMax = maxValue > 0 ? maxValue * 1.1 : 0;
  
  const x = d3.scaleLinear()
    .domain([domainMin, domainMax])
    .range([0, width])
  
  // Set fixed spacing between bars
  const fixedBarSpacing = 20 // Fixed spacing between bars
  const barHeight = 36 // Bar height
  
  // Calculate total height needed
  const totalHeight = (barHeight + fixedBarSpacing) * currentData.length - fixedBarSpacing
  
  // Set up scales with fixed spacing
  const y = d3.scaleBand()
    .domain(currentData.map(d => d.company))
    .range([0, totalHeight])
    .padding(0) // No padding as we're manually controlling spacing
  
  // Adjust SVG height to match total height needed
  const svgHeight = totalHeight + margin.top + margin.bottom
  
  // Update SVG height
  d3.select(chartContainer.value)
    .select('svg')
    .attr('height', svgHeight)
  
  // Update bar positions with fixed spacing
  // For negative values, bars extend left from 0; for positive values, bars extend right from 0
  const bars = svg.selectAll('rect')
    .data(currentData)
    .enter()
    .append('rect')
    .attr('y', (d, i) => i * (barHeight + fixedBarSpacing))
    .attr('height', barHeight)
    .attr('x', d => d.value < 0 ? x(d.value) : x(0))
    .attr('width', d => Math.abs(x(d.value) - x(0)))
    .attr('fill', d => d.value < 0 ? '#ef4444' : getCompanyColor(d.company)) // Red for negative values
    .attr('rx', 6)
    .attr('ry', 6)
    .style('opacity', 0.85)
    .style('filter', 'drop-shadow(0 1px 2px rgb(0 0 0 / 0.1))')

  // Update other elements positions
  const tickers = svg.selectAll('.ticker-label')
    .data(currentData)
    .enter()
    .append('text')
    .attr('class', 'ticker-label')
    .attr('x', -10)
    .attr('y', (d, i) => i * (barHeight + fixedBarSpacing) + barHeight / 2 - 8)
    .attr('dy', '0.35em')
    .attr('text-anchor', 'end')
    .style('font-size', '15px')
    .style('font-weight', 'bold')
    .attr('fill', '#111827')
    .text(d => d.company)
  
  const companyLabels = svg.selectAll('.company-label')
    .data(currentData)
    .enter()
    .append('text')
    .attr('class', 'company-label')
    .attr('x', -10)
    .attr('y', (d, i) => i * (barHeight + fixedBarSpacing) + barHeight / 2 + 12)
    .attr('dy', '0.35em')
    .attr('text-anchor', 'end')
    .style('font-size', '13px')
    .attr('fill', '#6B7280')
    .text(d => companyNames[d.company] || d.company)
  
  const valueLabels = svg.selectAll('.value-label')
    .data(currentData)
    .enter()
    .append('text')
    .attr('class', 'value-label')
    .attr('x', d => Math.max(x(0), x(d.value)) + 5)  // Always at the right end of the bar
    .attr('y', (d, i) => i * (barHeight + fixedBarSpacing) + barHeight / 2)
    .attr('dy', '0.35em')
    .attr('text-anchor', 'start')  // Always left-aligned
    .text(d => d3.format(',.0f')(d.value))
    .attr('fill', d => d.value < 0 ? '#dc2626' : '#6B7280')
    .style('font-size', '13px')
    .style('font-weight', d => d.value < 0 ? '600' : 'normal')
  
  const logoSize = 120
  const logos = svg.selectAll('.company-logo')
    .data(currentData)
    .enter()
    .append('image')
    .attr('class', 'company-logo')
    .attr('x', d => Math.max(x(0), x(d.value)) + 60)  // Always to the right of the bar
    .attr('y', (d, i) => i * (barHeight + fixedBarSpacing) + (barHeight - logoSize) / 2)
    .attr('width', logoSize)
    .attr('height', logoSize)
    .attr('preserveAspectRatio', 'xMidYMid meet')
    .attr('data-company', d => d.company)
    .attr('href', d => getCompanyLogo(d.company) || '')
    .on('error', function() {
      // If logo fails to load, just remove it
      d3.select(this).remove()
    })
  
  // Add zero line if there are negative values
  if (minValue < 0) {
    svg.append('line')
      .attr('class', 'zero-line')
      .attr('x1', x(0))
      .attr('y1', 0)
      .attr('x2', x(0))
      .attr('y2', totalHeight)
      .attr('stroke', '#4e843d')
      .attr('stroke-width', 2)
      .attr('stroke-dasharray', '4,4')
      .attr('opacity', 0.6)
  }
}

const saveChart = async () => {
  const svg = chartContainer.value.querySelector('svg')
  if (!svg) return

  try {
    // 创建一个新的 SVG 元素用于导出
    const svgData = new XMLSerializer().serializeToString(svg)
    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' })
    const URL = window.URL || window.webkitURL || window
    const blobURL = URL.createObjectURL(svgBlob)

    // 创建图片元素并加载 SVG
    const image = new Image()
    image.src = blobURL

    // 等待图片加载完成
    await new Promise((resolve, reject) => {
      image.onload = resolve
      image.onerror = reject
    })

    // 创建 canvas
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    
    // 设置 canvas 尺寸为 SVG 的 2 倍以获得更高的清晰度
    const scale = 2
    canvas.width = svg.clientWidth * scale
    canvas.height = svg.clientHeight * scale
    
    // 设置白色背景
    ctx.fillStyle = 'white'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    
    // 绘制 SVG
    ctx.scale(scale, scale)
    ctx.drawImage(image, 0, 0)

    // 获取所有 logo 图片
    const logoPromises = []
    const logos = svg.querySelectorAll('.company-logo')
    
    logos.forEach((logo) => {
      const logoPromise = new Promise((resolve) => {
        const img = new Image()
        img.crossOrigin = 'anonymous'
        img.onload = () => {
          const x = parseFloat(logo.getAttribute('x'))
          const y = parseFloat(logo.getAttribute('y'))
          const width = parseFloat(logo.getAttribute('width'))
          const height = parseFloat(logo.getAttribute('height'))
          ctx.drawImage(img, x * scale, y * scale, width * scale, height * scale)
          resolve()
        }
        img.onerror = () => {
          // If logo fails to load, just resolve without drawing it
          resolve()
        }
        const company = logo.getAttribute('data-company')
        img.src = getCompanyLogo(company) || ''
      })
      logoPromises.push(logoPromise)
    })

    // 等待所有 logo 加载完成
    await Promise.all(logoPromises)

    // 转换为 PNG 并下载
    const pngURL = canvas.toDataURL('image/png')
    const downloadLink = document.createElement('a')
    downloadLink.href = pngURL
    downloadLink.download = `bar-chart-${currentPeriod.value}.png`
    document.body.appendChild(downloadLink)
    downloadLink.click()
    document.body.removeChild(downloadLink)

    // 清理
    URL.revokeObjectURL(blobURL)
  } catch (error) {
    console.error('Error saving chart:', error)
  }
}

// Watch for window resize
let resizeTimeout
window.addEventListener('resize', () => {
  clearTimeout(resizeTimeout)
  resizeTimeout = setTimeout(renderChart, 250)
})

// Watch for currentPeriod prop changes
watch(() => props.currentPeriod, (newPeriod) => {
  console.log('currentPeriod prop changed:', newPeriod)
  if (newPeriod && chartData.value.length > 0) {
    renderChart()
  }
}, { immediate: true })  // Add immediate option to run on initial mount

// Watch for selectedCompanies prop changes
watch(() => props.selectedCompanies, (newSelection) => {
  console.log('selectedCompanies prop changed in BarChart:', newSelection)
  if (props.currentPeriod && chartData.value.length > 0) {
    console.log('Auto-refreshing BarChart due to company selection change')
    renderChart()
  }
}, { deep: true })

// Watch for chartData changes (initial load)
watch(chartData, (newData) => {
  console.log('chartData changed:', newData.length)
  if (newData.length > 0 && props.currentPeriod) {
    renderChart()
  }
})

onMounted(async () => {
  console.log('BarChart component mounted')
  await importFromGoogleSheet()
  
  // After data is loaded, check if we need to render
  if (props.currentPeriod && chartData.value.length > 0) {
    console.log('Initial render with existing period:', props.currentPeriod)
    renderChart()
  }
})

defineExpose({
  refresh: () => {
    console.log('BarChart refresh called, forcing render');
    // Force render without visibility check since this is explicitly called
    renderChart(true);
  }
})
</script>

<style scoped>
/* Add any component-specific styles here */
</style> 