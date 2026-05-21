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

const chartData = ref([]);
const isLoading = ref(false);

const globalXDomain = [-0.15, 0.60];
const globalYDomain = [-0.15, 0.85];

const showLabels = ref(false);

const toggleDataDisplay = () => {
  showLabels.value = !showLabels.value;
  initChart();
};

const GOOGLE_SHEET_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQYwQTSYwig7AZ0fjPniLVfUUJnLz3PP4f4fBtqkBNPYqrkKtQyZDaB99kHk2eCzuCh5i8oxTPCHeQ9/pub?gid=1144102204&output=csv';

const SECTION_HEADERS = new Set([
  'Rev Growth YoY',
  'Revenue YoY',
  'Revenue growth TTM',
  'EBITDA Margin % Annual',
  'EBITDA Margin % Quarterly',
  'EBITDA Margin TTM',
  "Rule of 40' TTM",
]);

// Proper RFC 4180 CSV parser — handles quoted cells containing commas and
// newlines (the founding-year row in this sheet has both).
const parseRfc4180 = (text) => {
  var results = [];
  var row = [];
  var cell = '';
  var inQuotes = false;
  for (var i = 0; i < text.length; i++) {
    var c = text[i];
    var next = text[i + 1];
    if (inQuotes) {
      if (c === '"' && next === '"') { cell += '"'; i++; }
      else if (c === '"') { inQuotes = false; }
      else { cell += c; }
    } else {
      if (c === '"') { inQuotes = true; }
      else if (c === ',') {
        var n = parseFloat(cell.trim());
        row.push(isNaN(n) ? cell.trim() : n);
        cell = '';
      } else if (c === '\n') {
        var n2 = parseFloat(cell.trim());
        row.push(isNaN(n2) ? cell.trim() : n2);
        results.push(row);
        row = [];
        cell = '';
      } else if (c !== '\r') {
        cell += c;
      }
    }
  }
  if (cell.length > 0 || row.length > 0) {
    var n3 = parseFloat(cell.trim());
    row.push(isNaN(n3) ? cell.trim() : n3);
    results.push(row);
  }
  return results;
};

const parseCsvData = (csvText) => {
  var rows = parseRfc4180(csvText);

  var headers = rows[0];
  console.log('CSV headers:', headers);

  var revenueGrowthTTMIndex = -1;
  var ebitdaMarginTTMIndex = -1;
  for (var i = 0; i < rows.length; i++) {
    var label = String(rows[i][0]).trim();
    if (label === 'Revenue growth TTM') revenueGrowthTTMIndex = i;
    if (label === 'EBITDA Margin TTM') ebitdaMarginTTMIndex = i;
  }

  if (revenueGrowthTTMIndex === -1) throw new Error('Revenue growth TTM section not found');
  if (ebitdaMarginTTMIndex === -1) throw new Error('EBITDA Margin TTM section not found');

  console.log('Revenue growth TTM at row', revenueGrowthTTMIndex);
  console.log('EBITDA Margin TTM at row', ebitdaMarginTTMIndex);

  var nextSectionAfter = function(startIndex) {
    for (var k = startIndex + 1; k < rows.length; k++) {
      if (SECTION_HEADERS.has(String(rows[k][0]).trim())) return k;
    }
    return rows.length;
  };

  // For each company column, find the most recent non-NaN value in the section.
  // This handles companies that report at different frequencies.
  var getLastValuePerColumn = function(startIndex, endIndex) {
    var colCount = headers.length;
    var lastValues = [];
    for (var c = 0; c < colCount; c++) lastValues.push(NaN);
    for (var r = startIndex + 1; r < endIndex; r++) {
      var row = rows[r];
      if (!row || !row[0]) continue;
      for (var col = 1; col < colCount; col++) {
        var v = typeof row[col] === 'number' ? row[col] : parseFloat(String(row[col] || ''));
        if (!isNaN(v)) lastValues[col] = v;
      }
    }
    return lastValues;
  };

  var revenueEnd = nextSectionAfter(revenueGrowthTTMIndex);
  var ebitdaEnd = nextSectionAfter(ebitdaMarginTTMIndex);

  var revenueValues = getLastValuePerColumn(revenueGrowthTTMIndex, revenueEnd);
  var ebitdaValues = getLastValuePerColumn(ebitdaMarginTTMIndex, ebitdaEnd);

  console.log('Revenue values sample (cols 1-5):', revenueValues.slice(1, 6));
  console.log('EBITDA values sample (cols 1-5):', ebitdaValues.slice(1, 6));

  var processedData = [];

  for (var j = 1; j < headers.length; j++) {
    var company = headers[j];
    if (!company) continue;
    var companyStr = String(company).trim();
    if (!companyStr) continue;

    var revenueGrowth = revenueValues[j];
    var ebitdaMargin = ebitdaValues[j];

    console.log(companyStr + ': revenue=' + revenueGrowth + ', ebitda=' + ebitdaMargin);

    // Values in the sheet are already decimal fractions (0.126 = 12.6%).
    // Do NOT divide by 100.
    if (!isNaN(revenueGrowth) && !isNaN(ebitdaMargin)) {
      processedData.push({
        company: companyStr,
        ebitdaMargin: ebitdaMargin,
        revenueGrowth: revenueGrowth,
      });
    }
  }

  console.log('Parsed ' + processedData.length + ' data points');
  return processedData;
};

const showError = (message) => {
  d3.select('#static-chart').selectAll('*').remove();
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
    .text(message);
};

const fetchDataFromUrl = async () => {
  console.log('Fetching data from Google Sheet...');
  isLoading.value = true;
  try {
    const response = await fetch(GOOGLE_SHEET_URL);
    if (!response.ok) throw new Error('HTTP error: ' + response.status);
    const csvText = await response.text();
    const processedData = parseCsvData(csvText);
    if (processedData.length === 0) throw new Error('No valid data points found');
    chartData.value = processedData;
    initChart();
  } catch (error) {
    console.error('Error fetching data:', error);
    showError('Please try refreshing the page or contact support if the issue persists.');
  } finally {
    isLoading.value = false;
  }
};

const processExcelData = (file) => {
  console.log('Processing uploaded file:', file.name);
  const reader = new FileReader();
  reader.onload = function(e) {
    try {
      const workbook = XLSX.read(new Uint8Array(e.target.result), { type: 'array' });
      console.log('Sheets:', workbook.SheetNames);
      let processedData = [];
      for (let s = 0; s < workbook.SheetNames.length; s++) {
        try {
          const csvText = XLSX.utils.sheet_to_csv(workbook.Sheets[workbook.SheetNames[s]]);
          processedData = parseCsvData(csvText);
          if (processedData.length > 0) {
            console.log('Found TTM data in sheet: ' + workbook.SheetNames[s]);
            break;
          }
        } catch (err) {
          // sheet does not have TTM sections, try next
        }
      }
      if (processedData.length === 0) throw new Error('No TTM data found in any sheet');
      chartData.value = processedData;
      initChart();
    } catch (error) {
      console.error('Error processing file:', error);
    }
  };
  reader.onerror = function(error) { console.error('File read error:', error); };
  reader.readAsArrayBuffer(file);
};

onMounted(async function() {
  console.log('Component mounted, fetching data...');
  await fetchDataFromUrl();
});

const initChart = () => {
  try {
    d3.select('#static-chart').selectAll('*').remove();

    if (!chartData.value || chartData.value.length === 0) {
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
        .text('Please click the Upload XLSX button in the header to load your data.');
      return;
    }

    const svg = d3.select('#static-chart').append('svg')
      .attr('width', '100%')
      .attr('height', '100%')
      .attr('viewBox', '0 0 1200 840')
      .attr('preserveAspectRatio', 'xMidYMid meet');

    const margin = { top: 40, right: 20, bottom: 50, left: 60 };
    const width = 1200 - margin.left - margin.right;
    const height = 840 - margin.top - margin.bottom;

    const g = svg.append('g')
      .attr('transform', 'translate(' + margin.left + ', ' + margin.top + ')');

    const xScale = d3.scaleLinear()
      .domain(globalXDomain)
      .range([0, width]);

    const yScale = d3.scaleLinear()
      .domain(globalYDomain)
      .range([height, 0]);

    g.append('g')
      .attr('class', 'x-axis')
      .attr('transform', 'translate(0,' + height + ')')
      .call(d3.axisBottom(xScale).tickFormat(d3.format('.0%')));

    g.append('g')
      .attr('class', 'y-axis')
      .call(d3.axisLeft(yScale).tickFormat(d3.format('.0%')));

    g.append('text')
      .attr('text-anchor', 'middle')
      .attr('x', width / 2)
      .attr('y', height + 40)
      .text('EBITDA Margin TTM')
      .style('font-size', '14px');

    g.append('text')
      .attr('text-anchor', 'middle')
      .attr('transform', 'rotate(-90)')
      .attr('y', -45)
      .attr('x', -(height / 2))
      .text('Revenue Growth TTM')
      .style('font-size', '14px');

    g.append('line')
      .attr('class', 'zero-line')
      .attr('x1', xScale(0)).attr('y1', 0)
      .attr('x2', xScale(0)).attr('y2', height)
      .attr('stroke', '#4e843d')
      .attr('stroke-dasharray', '4,4');

    g.append('line')
      .attr('class', 'zero-line')
      .attr('x1', 0).attr('y1', yScale(0))
      .attr('x2', width).attr('y2', yScale(0))
      .attr('stroke', '#4e843d')
      .attr('stroke-dasharray', '4,4');

    chartData.value.forEach(function(d) {
      if (!d.company || isNaN(d.ebitdaMargin) || isNaN(d.revenueGrowth)) return;

      if (showLabels.value) {
        g.append('text')
          .attr('x', xScale(d.ebitdaMargin))
          .attr('y', yScale(d.revenueGrowth))
          .attr('text-anchor', 'middle')
          .attr('dy', '0.35em')
          .style('font-size', '12px')
          .style('fill', getCompanyColor(d.company))
          .text((d.revenueGrowth * 100).toFixed(1) + '% / ' + (d.ebitdaMargin * 100).toFixed(1) + '%');
      } else {
        g.append('circle')
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
        img.onload = function() {
          const logoGroup = g.append('g')
            .attr('class', 'logo-group')
            .style('cursor', 'move');

          const logoSize = 96;
          const x = xScale(d.ebitdaMargin) - logoSize / 2;
          const y = yScale(d.revenueGrowth) - logoSize / 2 - 30;

          logoGroup.append('image')
            .attr('class', 'logo')
            .attr('width', logoSize)
            .attr('height', logoSize)
            .attr('xlink:href', logoSrc)
            .attr('x', x)
            .attr('y', y);

          logoGroup.insert('rect', 'image')
            .attr('x', x).attr('y', y)
            .attr('width', logoSize).attr('height', logoSize)
            .attr('fill', 'transparent');

          logoGroup.call(d3.drag()
            .on('start', function() { d3.select(this).raise(); })
            .on('drag', function(event) {
              const cx = parseFloat(d3.select(this).select('image').attr('x'));
              const cy = parseFloat(d3.select(this).select('image').attr('y'));
              d3.select(this).select('rect').attr('x', cx + event.dx).attr('y', cy + event.dy);
              d3.select(this).select('image').attr('x', cx + event.dx).attr('y', cy + event.dy);
            })
          );
        };
        img.src = logoSrc;
      }
    });

  } catch (error) {
    console.error('Error initializing chart:', error);
  }
};

const saveChart = async () => {
  try {
    const svgNode = document.querySelector('#static-chart svg');
    const svgWidth = svgNode.viewBox.baseVal.width || 1200;
    const svgHeight = svgNode.viewBox.baseVal.height || 840;

    const images = svgNode.querySelectorAll('image');
    await Promise.all(Array.from(images).map(async function(image) {
      try {
        const url = image.getAttribute('href') || image.getAttribute('xlink:href');
        const response = await fetch(url);
        if (!response.ok) throw new Error('Image load failed');
        const blob = await response.blob();
        const base64 = await new Promise(function(resolve) {
          const reader = new FileReader();
          reader.onload = function() { resolve(reader.result); };
          reader.readAsDataURL(blob);
        });
        image.setAttribute('href', base64);
      } catch (err) {
        image.remove();
      }
    }));

    const svgData = new XMLSerializer().serializeToString(svgNode);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const scale = 8;
    canvas.width = svgWidth * scale;
    canvas.height = svgHeight * scale;
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const svgUrl = URL.createObjectURL(svgBlob);
    const img = new Image();
    img.src = svgUrl;
    img.onload = function() {
      URL.revokeObjectURL(svgUrl);
      ctx.scale(scale, scale);
      ctx.drawImage(img, 0, 0, svgWidth, svgHeight);
      const link = document.createElement('a');
      link.download = 'TTM_Market_Performance.png';
      canvas.toBlob(function(blob) {
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
  saveChart,
});
</script>
