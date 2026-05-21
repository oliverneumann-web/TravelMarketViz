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

    <!-- Chart Controls Section -->
    <form class="mt-8">
      <div class="space-y-12">
        <div class="grid grid-cols-1 gap-x-8 gap-y-10 border-b border-gray-900/10 pb-12 md:grid-cols-3">
          <div>
            <h2 class="text-base/7 font-semibold text-gray-900">Chart Settings</h2>
            <p class="mt-1 text-sm/6 text-gray-600">Adjust the chart dimensions and axis ranges to customize the visualization.</p>
          </div>

          <div class="grid max-w-2xl grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6 md:col-span-2">
            <!-- Chart Dimensions -->
            <div class="sm:col-span-3">
              <label for="chart-width" class="block text-sm/6 font-medium text-gray-900">Width (px)</label>
              <div class="mt-2 grid grid-cols-1">
                <input
                  type="text"
                  id="chart-width"
                  v-model="chartDimensions.width"
                  @input="validateAndUpdateDimensions('width')"
                  :class="[
                    'col-start-1 row-start-1 block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6',
                    chartDimensions.widthError ? 'outline-red-300 focus:outline-red-600' : 'outline-gray-300 focus:outline-indigo-600'
                  ]"
                  placeholder="1200"
                />
                <ExclamationCircleIcon
                  v-if="chartDimensions.widthError"
                  class="pointer-events-none col-start-1 row-start-1 mr-3 size-5 self-center justify-self-end text-red-500 sm:size-4"
                />
              </div>
              <p v-if="chartDimensions.widthError" class="mt-1 text-sm text-red-600">{{ chartDimensions.widthError }}</p>
            </div>

            <div class="sm:col-span-3">
              <label for="chart-height" class="block text-sm/6 font-medium text-gray-900">Height (px)</label>
              <div class="mt-2 grid grid-cols-1">
                <input
                  type="text"
                  id="chart-height"
                  v-model="chartDimensions.height"
                  @input="validateAndUpdateDimensions('height')"
                  :class="[
                    'col-start-1 row-start-1 block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6',
                    chartDimensions.heightError ? 'outline-red-300 focus:outline-red-600' : 'outline-gray-300 focus:outline-indigo-600'
                  ]"
                  placeholder="840"
                />
                <ExclamationCircleIcon
                  v-if="chartDimensions.heightError"
                  class="pointer-events-none col-start-1 row-start-1 mr-3 size-5 self-center justify-self-end text-red-500 sm:size-4"
                />
              </div>
              <p v-if="chartDimensions.heightError" class="mt-1 text-sm text-red-600">{{ chartDimensions.heightError }}</p>
            </div>

            <!-- X-Axis Range -->
            <div class="sm:col-span-3">
              <label for="x-min" class="block text-sm/6 font-medium text-gray-900">X-Axis Min (%)</label>
              <div class="mt-2 grid grid-cols-1">
                <input
                  type="text"
                  id="x-min"
                  v-model="xAxisRange.min"
                  @input="validateAndUpdateRange('x', 'min')"
                  :class="[
                    'col-start-1 row-start-1 block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6',
                    xAxisRange.minError ? 'outline-red-300 focus:outline-red-600' : 'outline-gray-300 focus:outline-indigo-600'
                  ]"
                  placeholder="-15"
                />
                <ExclamationCircleIcon
                  v-if="xAxisRange.minError"
                  class="pointer-events-none col-start-1 row-start-1 mr-3 size-5 self-center justify-self-end text-red-500 sm:size-4"
                />
              </div>
              <p v-if="xAxisRange.minError" class="mt-1 text-sm text-red-600">{{ xAxisRange.minError }}</p>
            </div>

            <div class="sm:col-span-3">
              <label for="x-max" class="block text-sm/6 font-medium text-gray-900">X-Axis Max (%)</label>
              <div class="mt-2 grid grid-cols-1">
                <input
                  type="text"
                  id="x-max"
                  v-model="xAxisRange.max"
                  @input="validateAndUpdateRange('x', 'max')"
                  :class="[
                    'col-start-1 row-start-1 block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6',
                    xAxisRange.maxError ? 'outline-red-300 focus:outline-red-600' : 'outline-gray-300 focus:outline-indigo-600'
                  ]"
                  placeholder="60"
                />
                <ExclamationCircleIcon
                  v-if="xAxisRange.maxError"
                  class="pointer-events-none col-start-1 row-start-1 mr-3 size-5 self-center justify-self-end text-red-500 sm:size-4"
                />
              </div>
              <p v-if="xAxisRange.maxError" class="mt-1 text-sm text-red-600">{{ xAxisRange.maxError }}</p>
            </div>

            <!-- Y-Axis Range -->
            <div class="sm:col-span-3">
              <label for="y-min" class="block text-sm/6 font-medium text-gray-900">Y-Axis Min (%)</label>
              <div class="mt-2 grid grid-cols-1">
                <input
                  type="text"
                  id="y-min"
                  v-model="yAxisRange.min"
                  @input="validateAndUpdateRange('y', 'min')"
                  :class="[
                    'col-start-1 row-start-1 block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6',
                    yAxisRange.minError ? 'outline-red-300 focus:outline-red-600' : 'outline-gray-300 focus:outline-indigo-600'
                  ]"
                  placeholder="-15"
                />
                <ExclamationCircleIcon
                  v-if="yAxisRange.minError"
                  class="pointer-events-none col-start-1 row-start-1 mr-3 size-5 self-center justify-self-end text-red-500 sm:size-4"
                />
              </div>
              <p v-if="yAxisRange.minError" class="mt-1 text-sm text-red-600">{{ yAxisRange.minError }}</p>
            </div>

            <div class="sm:col-span-3">
              <label for="y-max" class="block text-sm/6 font-medium text-gray-900">Y-Axis Max (%)</label>
              <div class="mt-2 grid grid-cols-1">
                <input
                  type="text"
                  id="y-max"
                  v-model="yAxisRange.max"
                  @input="validateAndUpdateRange('y', 'max')"
                  :class="[
                    'col-start-1 row-start-1 block w-full rounded-md bg-white px-3 py-1.5 text-base text-gray-900 outline outline-1 -outline-offset-1 outline-gray-300 placeholder:text-gray-400 focus:outline focus:outline-2 focus:-outline-offset-2 focus:outline-indigo-600 sm:text-sm/6',
                    yAxisRange.maxError ? 'outline-red-300 focus:outline-red-600' : 'outline-gray-300 focus:outline-indigo-600'
                  ]"
                  placeholder="85"
                />
                <ExclamationCircleIcon
                  v-if="yAxisRange.maxError"
                  class="pointer-events-none col-start-1 row-start-1 mr-3 size-5 self-center justify-self-end text-red-500 sm:size-4"
                />
              </div>
              <p v-if="yAxisRange.maxError" class="mt-1 text-sm text-red-600">{{ yAxisRange.maxError }}</p>
            </div>
          </div>
        </div>
      </div>
    </form>
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
import { ExclamationCircleIcon } from '@heroicons/vue/16/solid';
import * as d3 from 'd3';
import * as XLSX from 'xlsx';
import { getCompanyColor, getCompanyLogo } from '../data/companyMeta';

const chartData = ref([]);
const isLoading = ref(false);
const chartTitle = ref('');

const showLabels = ref(false);

// Chart dimension controls (mirrors AnimatedBubbleChart)
const chartDimensions = ref({
  width: '1200',
  height: '840',
  widthError: '',
  heightError: '',
});

const xAxisRange = ref({
  min: '-15',
  max: '60',
  minError: '',
  maxError: '',
});

const yAxisRange = ref({
  min: '-15',
  max: '85',
  minError: '',
  maxError: '',
});

const validateAndUpdateDimensions = (dimension) => {
  const value = parseInt(chartDimensions.value[dimension]);
  chartDimensions.value[`${dimension}Error`] = '';

  if (isNaN(value)) {
    chartDimensions.value[`${dimension}Error`] = 'Please enter a valid number';
    return;
  }
  if (value < 200) {
    chartDimensions.value[`${dimension}Error`] = 'Value must be at least 200px';
    return;
  }
  if (value > 5000) {
    chartDimensions.value[`${dimension}Error`] = 'Value must not exceed 5000px';
    return;
  }

  if (!chartDimensions.value.widthError && !chartDimensions.value.heightError) {
    initChart();
  }
};

const validateAndUpdateRange = (axis, bound) => {
  const range = axis === 'x' ? xAxisRange.value : yAxisRange.value;
  const value = parseFloat(range[bound]);
  range[`${bound}Error`] = '';

  if (isNaN(value)) {
    range[`${bound}Error`] = 'Please enter a valid number';
    return;
  }

  const otherBound = bound === 'min' ? 'max' : 'min';
  const otherValue = parseFloat(range[otherBound]);
  if (!isNaN(otherValue)) {
    if (bound === 'min' && value >= otherValue) {
      range[`${bound}Error`] = 'Min value must be less than max';
      return;
    }
    if (bound === 'max' && value <= otherValue) {
      range[`${bound}Error`] = 'Max value must be greater than min';
      return;
    }
  }

  if (!range.minError && !range.maxError) {
    initChart();
  }
};

const toggleDataDisplay = () => {
  showLabels.value = !showLabels.value;
  initChart();
};

const GOOGLE_SHEET_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQYwQTSYwig7AZ0fjPniLVfUUJnLz3PP4f4fBtqkBNPYqrkKtQyZDaB99kHk2eCzuCh5i8oxTPCHeQ9/pub?gid=1144102204&output=csv';


// Proper RFC 4180 CSV parser — handles quoted cells containing commas and
// newlines (the founding-year row in this sheet has both).
const parseRfc4180 = (text) => {
  var results = [];
  var row = [];
  var cell = '';
  var inQuotes = false;
  var colIndex = 0;
  var pushCell = function(str, col) {
    // First column is always a label — keep as string to preserve values like "2026 Q1"
    if (col === 0) { row.push(str); return; }
    var n = parseFloat(str);
    row.push(isNaN(n) ? str : n);
  };
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
        pushCell(cell.trim(), colIndex);
        cell = '';
        colIndex++;
      } else if (c === '\n') {
        pushCell(cell.trim(), colIndex);
        results.push(row);
        row = [];
        cell = '';
        colIndex = 0;
      } else if (c !== '\r') {
        cell += c;
      }
    }
  }
  if (cell.length > 0 || row.length > 0) {
    pushCell(cell.trim(), colIndex);
    results.push(row);
  }
  return results;
};

// Return just the first line of a multi-line cell value.
var firstLine = function(val) {
  return String(val).split(‘\n’)[0].trim();
};

// Format a raw period label (e.g. "2024'Q4", "Dec 2024") into a readable title.
const formatPeriodLabel = (raw) => {
  if (!raw) return '';
  const label = firstLine(raw);
  // Handle "YYYY'QN" format produced by the animated chart sheets
  const quarterMatch = label.match(/^(\d{4})'(Q[1-4])$/);
  if (quarterMatch) return `${quarterMatch[1]} ${quarterMatch[2]}`;
  return label;
};

const parseCsvData = (csvText) => {
  var rows = parseRfc4180(csvText);

  var headers = rows[0];
  console.log('CSV headers:', headers);

  var revenueGrowthTTMIndex = -1;
  var ebitdaMarginTTMIndex = -1;
  for (var i = 0; i < rows.length; i++) {
    var label = firstLine(rows[i][0]);
    if (label === 'Revenue growth TTM') revenueGrowthTTMIndex = i;
    if (label === 'EBITDA Margin TTM') ebitdaMarginTTMIndex = i;
  }

  if (revenueGrowthTTMIndex === -1) throw new Error('Revenue growth TTM section not found');
  if (ebitdaMarginTTMIndex === -1) throw new Error('EBITDA Margin TTM section not found');

  console.log('Revenue growth TTM at row', revenueGrowthTTMIndex);
  console.log('EBITDA Margin TTM at row', ebitdaMarginTTMIndex);

  var nextBlankRowAfter = function(startIndex) {
    for (var k = startIndex + 1; k < rows.length; k++) {
      if (!rows[k] || !String(rows[k][0] || '').trim()) return k;
    }
    return rows.length;
  };

  // Return the last row in [startIndex+1, endIndex) that has data for at least
  // 2 companies. Requiring >= 2 skips lone early reporters (e.g. a single
  // company that has already filed for the next quarter) so we land on the most
  // recent quarter where a meaningful group of companies has reported.
  var getLastDataRow = function(startIndex, endIndex) {
    var lastRow = null;
    for (var r = startIndex + 1; r < endIndex; r++) {
      var row = rows[r];
      if (!row || !row[0]) continue;
      var count = 0;
      for (var col = 1; col < row.length; col++) {
        var v = row[col];
        if (typeof v === 'number' && !isNaN(v)) count++;
      }
      if (count >= 2) lastRow = row;
    }
    return lastRow;
  };

  var revenueEnd = nextBlankRowAfter(revenueGrowthTTMIndex);
  var ebitdaEnd = nextBlankRowAfter(ebitdaMarginTTMIndex);

  var revenueRow = getLastDataRow(revenueGrowthTTMIndex, revenueEnd);
  var ebitdaRow = getLastDataRow(ebitdaMarginTTMIndex, ebitdaEnd);

  if (!revenueRow) throw new Error('No data rows in Revenue growth TTM section');
  if (!ebitdaRow) throw new Error('No data rows in EBITDA Margin TTM section');

  console.log('Using revenue row:', firstLine(revenueRow[0]));
  console.log('Using EBITDA row:', firstLine(ebitdaRow[0]));

  // Derive title from the period label in the data row
  const periodLabel = formatPeriodLabel(revenueRow[0]);

  var processedData = [];

  for (var j = 1; j < headers.length; j++) {
    var company = headers[j];
    if (!company) continue;
    var companyStr = String(company).trim();
    if (!companyStr) continue;

    var revenueGrowth = typeof revenueRow[j] === 'number' ? revenueRow[j] : parseFloat(String(revenueRow[j] || ''));
    var ebitdaMargin = typeof ebitdaRow[j] === 'number' ? ebitdaRow[j] : parseFloat(String(ebitdaRow[j] || ''));

    console.log(companyStr + ': revenue=' + revenueGrowth + ', ebitda=' + ebitdaMargin);

    // Raw sheet values are stored as e.g. 12.6 (meaning 12.6%). Divide by 100
    // to get the decimal fraction 0.126 that the chart's axis format expects.
    if (!isNaN(revenueGrowth) && !isNaN(ebitdaMargin)) {
      processedData.push({
        company: companyStr,
        ebitdaMargin: ebitdaMargin / 100,
        revenueGrowth: revenueGrowth / 100,
      });
    }
  }

  console.log('Parsed ' + processedData.length + ' data points');
  return { data: processedData, periodLabel };
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
    const { data: processedData, periodLabel } = parseCsvData(csvText);
    if (processedData.length === 0) throw new Error('No valid data points found');
    chartData.value = processedData;
    if (periodLabel) chartTitle.value = 'Four Quarters Ending ' + periodLabel;
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
      let foundPeriodLabel = '';
      for (let s = 0; s < workbook.SheetNames.length; s++) {
        try {
          const csvText = XLSX.utils.sheet_to_csv(workbook.Sheets[workbook.SheetNames[s]]);
          const { data, periodLabel } = parseCsvData(csvText);
          if (data.length > 0) {
            processedData = data;
            foundPeriodLabel = periodLabel;
            console.log('Found TTM data in sheet: ' + workbook.SheetNames[s]);
            break;
          }
        } catch (err) {
          // sheet does not have TTM sections, try next
        }
      }
      if (processedData.length === 0) throw new Error('No TTM data found in any sheet');
      chartData.value = processedData;
      if (foundPeriodLabel) chartTitle.value = 'Four Quarters Ending ' + foundPeriodLabel;
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

    const svgWidth = parseInt(chartDimensions.value.width) || 1200;
    const svgHeight = parseInt(chartDimensions.value.height) || 840;

    const xMin = parseFloat(xAxisRange.value.min) / 100;
    const xMax = parseFloat(xAxisRange.value.max) / 100;
    const yMin = parseFloat(yAxisRange.value.min) / 100;
    const yMax = parseFloat(yAxisRange.value.max) / 100;

    const xDomain = [isNaN(xMin) ? -0.15 : xMin, isNaN(xMax) ? 0.60 : xMax];
    const yDomain = [isNaN(yMin) ? -0.15 : yMin, isNaN(yMax) ? 0.85 : yMax];

    const svg = d3.select('#static-chart').append('svg')
      .attr('width', '100%')
      .attr('height', '100%')
      .attr('viewBox', '0 0 ' + svgWidth + ' ' + svgHeight)
      .attr('preserveAspectRatio', 'xMidYMid meet');

    const margin = { top: 60, right: 20, bottom: 50, left: 60 };
    const width = svgWidth - margin.left - margin.right;
    const height = svgHeight - margin.top - margin.bottom;

    // Dynamic title
    svg.append('text')
      .attr('text-anchor', 'middle')
      .attr('x', svgWidth / 2)
      .attr('y', 30)
      .style('font-size', '18px')
      .style('font-weight', '600')
      .style('fill', '#1e293b')
      .text(chartTitle.value);

    const g = svg.append('g')
      .attr('transform', 'translate(' + margin.left + ', ' + margin.top + ')');

    const xScale = d3.scaleLinear()
      .domain(xDomain)
      .range([0, width]);

    const yScale = d3.scaleLinear()
      .domain(yDomain)
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

    // Zero lines (only when 0 is within the visible domain)
    if (xDomain[0] <= 0 && xDomain[1] >= 0) {
      g.append('line')
        .attr('class', 'zero-line')
        .attr('x1', xScale(0)).attr('y1', 0)
        .attr('x2', xScale(0)).attr('y2', height)
        .attr('stroke', '#4e843d')
        .attr('stroke-dasharray', '4,4');
    }

    if (yDomain[0] <= 0 && yDomain[1] >= 0) {
      g.append('line')
        .attr('class', 'zero-line')
        .attr('x1', 0).attr('y1', yScale(0))
        .attr('x2', width).attr('y2', yScale(0))
        .attr('stroke', '#4e843d')
        .attr('stroke-dasharray', '4,4');
    }

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
