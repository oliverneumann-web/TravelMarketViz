<template>
  <div class="chart-container" ref="chartRef">
    <div class="flex justify-end mb-4 gap-4">
      <button
        @click="toggleDataDisplay"
        class="px-4 py-2 bg-wego-green text-white rounded hover:bg-wego-green-dark flex items-center gap-2"
      >
        {{ showLabels ? 'Only Show Dots' : 'Show Labels' }}
      </button>
      <button
        @click="saveChart"
        class="px-4 py-2 bg-wego-green text-white rounded hover:bg-wego-green-dark flex items-center gap-2"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path d="M7.707 10.293a1 1 0 10-1.414 1.414l3 3a1 1 0 001.414 0l3-3a1 1 0 00-1.414-1.414L11 11.586V6h-2v5.586l-1.293-1.293z" />
          <path d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" />
        </svg>
        Save Chart
      </button>
    </div>
    <div id="static-chart" class="w-full h-full relative">
      <div v-if="isLoading" class="absolute inset-0 flex items-center justify-center bg-white bg-opacity-90 z-50">
        <div class="text-center">
          <div class="text-lg font-semibold text-gray-700">Loading...</div>
          <div class="text-sm text-gray-600">may take around 2 seconds</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
  min-height: 840px;
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.zero-line {
  opacity: 0.5;
}

.dot, .cross {
  cursor: pointer;
  transition: all 0.2s ease;
}

.dot:hover, .cross:hover {
  transform: scale(1.5);
}

.quarter-label {
  pointer-events: none;
  user-select: none;
}

.active {
  stroke: #000;
  stroke-width: 2px;
}

.logo {
  cursor: move;
  user-select: none;
}
</style>

<script setup>
import { onMounted, ref } from 'vue';
import * as d3 from 'd3';
import * as XLSX from 'xlsx';
import { getCompanyColor, getCompanyLogo } from '../data/companyMeta';

let chartData = ref([]);
const isLoading = ref(false);

// Fixed domains for consistent scaling
const globalXDomain = [-0.15, 0.60];  // EBITDA margin range
const globalYDomain = [-0.15, 0.85];  // Revenue growth range

const logoPositions = ref({});

const showLabels = ref(false);

const toggleDataDisplay = () => {
  showLabels.value = !showLabels.value;
  initChart();
};

const EXCEL_URL = 'https://1drv.ms/x/c/130fda80f0432a83/EaUo2h8IJTZDsA5Rmm-FVDcB_-0mTOTuBOEN26R8EDarGQ?download=1';

// Shared parsing logic used by both URL fetch and manual file upload.
// Looks for 'Revenue growth TTM\n12m trailing' and 'EBITDA Margin TTM\n12m trailing'
// as section headers, then uses the last data row from each section.
const processSheetData = (workbook) => {
  const ttmSheet = workbook.Sheets['TTM (bounded)'];
  if (!ttmSheet) throw new Error('TTM (bounded) sheet not found');

  const jsonData = XLSX.utils.sheet_to_json(ttmSheet, { header: 1 });
  console.log('Total rows parsed:', jsonData.length);

  // Company names from first row, preserving column alignment with null for blanks
  const headerRow = jsonData[0] || [];
  const headers = headerRow.slice(1).map(h => (h && String(h).trim()) || null);
  console.log('Headers:', headers.filter(Boolean));

  // Normalize line endings so \r\n and \r both become \n
  const normalizeCell = (val) => String(val).replace(/\r\n|\r/g, '\n').trim();

  const revenueGrowthRowIndex = jsonData.findIndex(row =>
    row && row[0] && normalizeCell(row[0]).includes('Revenue growth TTM')
  );

  const ebitdaRowIndex = jsonData.findIndex(row =>
    row && row[0] && normalizeCell(row[0]).includes('EBITDA Margin TTM')
  );

  if (revenueGrowthRowIndex === -1) throw new Error('Revenue growth TTM section not found in sheet');
  if (ebitdaRowIndex === -1) throw new Error('EBITDA Margin TTM section not found in sheet');

  console.log(`Revenue growth TTM section at row ${revenueGrowthRowIndex}: "${normalizeCell(jsonData[revenueGrowthRowIndex][0])}"`);
  console.log(`EBITDA Margin TTM section at row ${ebitdaRowIndex}: "${normalizeCell(jsonData[ebitdaRowIndex][0])}"`);

  // Each section ends where the next section starts (or end of data)
  const totalRows = jsonData.length;
  const [revenueEnd, ebitdaEnd] = revenueGrowthRowIndex < ebitdaRowIndex
    ? [ebitdaRowIndex, totalRows]
    : [totalRows, revenueGrowthRowIndex];

  // Returns the last row within [startIndex+1, endIndex) that has at least one numeric value
  const getLastDataRow = (startIndex, endIndex) => {
    let lastRow = null;
    for (let i = startIndex + 1; i < endIndex; i++) {
      const row = jsonData[i];
      if (!row || !row[0]) continue;
      const hasNumeric = headers.some((_, j) => !isNaN(parseFloat(row[j + 1])));
      if (hasNumeric) lastRow = row;
    }
    return lastRow;
  };

  const revenueRow = getLastDataRow(revenueGrowthRowIndex, revenueEnd);
  const ebitdaRow = getLastDataRow(ebitdaRowIndex, ebitdaEnd);

  if (!revenueRow) throw new Error('No data rows found in Revenue growth TTM section');
  if (!ebitdaRow) throw new Error('No data rows found in EBITDA Margin TTM section');

  console.log(`Using revenue growth row labelled: "${revenueRow[0]}"`);
  console.log(`Using EBITDA margin row labelled: "${ebitdaRow[0]}"`);

  const processedData = [];

  headers.forEach((company, j) => {
    if (!company) return;
    const colIndex = j + 1;
    const revenueGrowth = parseFloat(revenueRow[colIndex]);
    const ebitdaMargin = parseFloat(ebitdaRow[colIndex]);

    console.log(`${company}: revenueGrowth=${revenueGrowth}, ebitdaMargin=${ebitdaMargin}`);

    if (!isNaN(revenueGrowth) && !isNaN(ebitdaMargin)) {
      processedData.push({
        company,
        ebitdaMargin: ebitdaMargin / 100,
        revenueGrowth: revenueGrowth / 100
      });
    }
  });

  console.log(`Processed ${processedData.length} valid data points`);
  return processedData;
};

const fetchDataFromUrl = async () => {
  console.log('Fetching data from URL:', EXCEL_URL);
  isLoading.value = true;
  try {
    const response = await fetch(EXCEL_URL);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

    const arrayBuffer = await response.arrayBuffer();
    const workbook = XLSX.read(new Uint8Array(arrayBuffer), { type: 'array' });
    console.log('Available sheets:', workbook.SheetNames);

    const processedData = processSheetData(workbook);

    if (processedData.length === 0) throw new Error('No valid data points found');

    chartData.value = processedData;
    initChart();
  } catch (error) {
    console.error('Error fetching data:', error);
    console.error('Error stack:', error.stack);

    const container = d3.select('#static-chart')
      .append('div')
      .style('text-align', 'center')
      .style('padding-top', '40px')
      .style('color', '#e74c3c');

    container.append('div')
      .style('font-size', '18px')
      .style('font-weight', 'bold')
      .style('margin-bottom', '12px')
      .text('Error loading data');

    container.append('div')
      .style('font-size', '14px')
      .text('Please try refreshing the page or contact support if the issue persists.');
  } finally {
    isLoading.value = false;
  }
};

const processExcelData = (file) => {
  console.log('Processing uploaded Excel file:', file.name);
  const reader = new FileReader();

  reader.onload = async (e) => {
    try {
      const data = new Uint8Array(e.target.result);
      const workbook = XLSX.read(data, { type: 'array' });
      console.log('Available sheets:', workbook.SheetNames);

      const processedData = processSheetData(workbook);

      if (processedData.length === 0) throw new Error('No valid data points found');

      chartData.value = processedData;
      initChart();
    } catch (error) {
      console.error('Error processing Excel file:', error);
      console.error('Error stack:', error.stack);
    }
  };

  reader.onerror = (error) => console.error('Error reading file:', error);
  reader.readAsArrayBuffer(file);
};

onMounted(async () => {
  console.log('Component mounted, fetching data...');
  await fetchDataFromUrl();
});

// Initialize chart
const initChart = () => {
  try {
    console.log('Starting chart initialization with data:', chartData.value);

    // Clear previous chart
    d3.select('#static-chart').selectAll('*').remove();

    if (!chartData.value || chartData.value.length === 0) {
      console.log('No data to display');
      const container = d3.select('#static-chart')
        .append('div')
        .style('text-align', 'center')
        .style('padding-top', '40px')
        .style('color', '#4e843d');

      container.append('div')
        .style('font-size', '18px')
        .style('font-weight', 'bold')
        .style('margin-bottom', '12px')
        .text('No data to display');

      container.append('div')
        .style('font-size', '14px')
        .text('Please click the "Upload XLSX" button in the header to load your data.');

      return;
    }

    chartData.value.forEach(d => {
      console.log('Processing data point:', {
        company: d.company,
        ebitdaMargin: d.ebitdaMargin,
        revenueGrowth: d.revenueGrowth,
        hasLogo: !!getCompanyLogo(d.company),
        color: getCompanyColor(d.company)
      });
    });

    // Create SVG
    const svg = d3.select('#static-chart').append('svg')
      .attr('width', '100%')
      .attr('height', '100%')
      .attr('viewBox', '0 0 1200 840')
      .attr('preserveAspectRatio', 'xMidYMid meet');

    const margin = { top: 40, right: 20, bottom: 50, left: 60 };
    const width = 1200 - margin.left - margin.right;
    const height = 840 - margin.top - margin.bottom;

    const g = svg.append("g")
      .attr("transform", `translate(${margin.left}, ${margin.top})`);

    const xScale = d3.scaleLinear()
      .domain(globalXDomain)
      .range([0, width]);

    const yScale = d3.scaleLinear()
      .domain(globalYDomain)
      .range([height, 0]);

    const xAxis = d3.axisBottom(xScale).tickFormat(d3.format('.0%'));
    const yAxis = d3.axisLeft(yScale).tickFormat(d3.format('.0%'));

    g.append('g')
      .attr('class', 'x-axis')
      .attr('transform', `translate(0,${height})`)
      .call(xAxis);

    g.append('g')
      .attr('class', 'y-axis')
      .call(yAxis);

    g.append('text')
      .attr('class', 'x-label')
      .attr('text-anchor', 'middle')
      .attr('x', width / 2)
      .attr('y', height + 40)
      .text('EBITDA Margin TTM')
      .style('font-size', '14px');

    g.append('text')
      .attr('class', 'y-label')
      .attr('text-anchor', 'middle')
      .attr('transform', 'rotate(-90)')
      .attr('y', -45)
      .attr('x', -height / 2)
      .text('Revenue Growth YoY TTM')
      .style('font-size', '14px');

    g.append('line')
      .attr('class', 'zero-line')
      .attr('x1', xScale(0))
      .attr('y1', 0)
      .attr('x2', xScale(0))
      .attr('y2', height)
      .attr('stroke', '#4e843d')
      .attr('stroke-dasharray', '4,4');

    g.append('line')
      .attr('class', 'zero-line')
      .attr('x1', 0)
      .attr('y1', yScale(0))
      .attr('x2', width)
      .attr('y2', yScale(0))
      .attr('stroke', '#4e843d')
      .attr('stroke-dasharray', '4,4');

    chartData.value.forEach(d => {
      console.log('Drawing data point:', d);

      if (!d.company || isNaN(d.ebitdaMargin) || isNaN(d.revenueGrowth)) {
        console.log('Skipping invalid data point:', d);
        return;
      }

      if (showLabels.value) {
        g.append('text')
          .attr('class', 'data-label')
          .attr('x', xScale(d.ebitdaMargin))
          .attr('y', yScale(d.revenueGrowth))
          .attr('text-anchor', 'middle')
          .attr('dy', '0.35em')
          .style('font-size', '12px')
          .style('fill', getCompanyColor(d.company))
          .text(`${(d.revenueGrowth * 100).toFixed(1)}% / ${(d.ebitdaMargin * 100).toFixed(1)}%`);
      } else {
        g.append('circle')
          .attr('class', 'data-dot')
          .attr('cx', xScale(d.ebitdaMargin))
          .attr('cy', yScale(d.revenueGrowth))
          .attr('r', 6)
          .style('fill', getCompanyColor(d.company))
          .style('stroke', 'white')
          .style('stroke-width', '2px');
      }

      const logoSrc = getCompanyLogo(d.company);
      if (logoSrc) {
        const img = new Image();
        img.onload = () => {
          const logoGroup = g.append('g')
            .attr('class', 'logo-group')
            .style('cursor', 'move');

          const logoSize = 96;
          const x = xScale(d.ebitdaMargin) - logoSize/2;
          const y = yScale(d.revenueGrowth) - logoSize/2 - 30;

          logoGroup.append('image')
            .attr('class', 'logo')
            .attr('width', logoSize)
            .attr('height', logoSize)
            .attr('xlink:href', logoSrc)
            .attr('x', x)
            .attr('y', y);

          logoGroup.insert('rect', 'image')
            .attr('class', 'logo-hit-area')
            .attr('x', x)
            .attr('y', y)
            .attr('width', logoSize)
            .attr('height', logoSize)
            .attr('fill', 'transparent');

          logoGroup.call(d3.drag()
            .on('start', function() {
              d3.select(this).raise();
            })
            .on('drag', function(event) {
              const dx = event.dx;
              const dy = event.dy;
              const currentX = parseFloat(d3.select(this).select('image').attr('x'));
              const currentY = parseFloat(d3.select(this).select('image').attr('y'));

              d3.select(this).select('rect')
                .attr('x', currentX + dx)
                .attr('y', currentY + dy);

              d3.select(this).select('image')
                .attr('x', currentX + dx)
                .attr('y', currentY + dy);
            }));
        };
        img.src = logoSrc;
      }
    });

  } catch (error) {
    console.error('Error initializing chart:', error);
    console.error('Error stack:', error.stack);
  }
};

const saveChart = async () => {
  try {
    const svgNode = document.querySelector('#static-chart svg');
    const svgWidth = svgNode.viewBox.baseVal.width || 1200;
    const svgHeight = svgNode.viewBox.baseVal.height || 840;

    const images = svgNode.querySelectorAll('image');
    await Promise.all(Array.from(images).map(async (image) => {
      try {
        const url = image.getAttribute('href') || image.getAttribute('xlink:href');
        const response = await fetch(url);
        if (!response.ok) throw new Error('Image load failed');
        const blob = await response.blob();
        const base64 = await new Promise((resolve) => {
          const reader = new FileReader();
          reader.onload = () => resolve(reader.result);
          reader.readAsDataURL(blob);
        });
        image.setAttribute('href', base64);
      } catch (error) {
        image.remove();
      }
    }));

    const svgData = new XMLSerializer().serializeToString(svgNode);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();

    const scale = 8;
    canvas.width = svgWidth * scale;
    canvas.height = svgHeight * scale;

    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';

    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const svgUrl = URL.createObjectURL(svgBlob);
    img.src = svgUrl;

    img.onload = () => {
      URL.revokeObjectURL(svgUrl);
      ctx.scale(scale, scale);
      ctx.drawImage(img, 0, 0, svgWidth, svgHeight);

      const link = document.createElement('a');
      link.download = 'TTM_Market_Performance.png';
      canvas.toBlob((blob) => {
        link.href = URL.createObjectURL(blob);
        link.click();
        URL.revokeObjectURL(link.href);
      }, 'image/png', 1.0);
    };
  } catch (error) {
    console.error('Error saving chart:', error);
  }
};

defineExpose({
  processExcelData,
  saveChart
});
</script>
