<template>
  <div class="chart-container" ref="chartRef">
    <div id="additional-chart" class="w-full h-full relative">
      <!-- Loading indicator - only on chart canvas -->
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
                  placeholder="-50"
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
                  placeholder="80"
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
                  placeholder="-30"
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
                  placeholder="100"
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

#additional-chart {
  width: 100%;
  height: 100%;
  min-height: 800px;
}

svg {
  font-family: system-ui, -apple-system, sans-serif;
}

.x-label, .y-label {
  font-size: 14px;
  fill: #475569;
}

.quarter-display {
  font-size: 24px;
  fill: #1e293b;
  font-weight: 600;
}

.bubble circle {
  transition: all 0.3s ease;
}

.bubble:hover circle {
  opacity: 0.9;
  filter: brightness(1.1);
}

.bubble image {
  pointer-events: none;
}

/* Axes styling */
.domain {
  stroke: #cbd5e1;
}

.tick line {
  stroke: #e2e8f0;
}

.tick text {
  fill: #64748b;
  font-size: 12px;
}

/* Grid lines */
.grid line {
  stroke: #e2e8f0;
  stroke-opacity: 0.5;
  shape-rendering: crispEdges;
}

.grid path {
  stroke-width: 0;
}

/* Quadrant labels */
.quadrant-label {
  font-size: 12px;
  fill: #94a3b8;
  text-anchor: middle;
}

/* Animation controls */
.controls {
  display: none;
}

.control-button {
  display: none;
}

/* Tooltip */
.tooltip {
  position: absolute;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  font-size: 14px;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.tooltip.visible {
  opacity: 1;
}

.tooltip-company {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 4px;
}

.tooltip-data {
  color: #64748b;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

/* Legend */
.legend {
  position: absolute;
  top: 20px;
  right: 20px;
  background: white;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
}

.legend-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-label {
  font-size: 12px;
  color: #64748b;
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

/* Slider container */
.slider-container {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 80%;
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  z-index: 1000; /* Ensure slider is above chart */
}

.slider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.slider-title {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.slider-value {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
}

/* Custom slider styling */
input[type="range"] {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 4px;
  border-radius: 2px;
  background: #e2e8f0;
  outline: none;
  margin: 10px 0;
}

input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #4e843d;  /* Wego green */
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

input[type="range"]::-webkit-slider-thumb:hover {
  background: #3d6a31;  /* Darker Wego green */
  transform: scale(1.1);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
}

input[type="range"]::-moz-range-thumb {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #4e843d;  /* Wego green */
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

input[type="range"]::-moz-range-thumb:hover {
  background: #3d6a31;  /* Darker Wego green */
  transform: scale(1.1);
  box-shadow: 0 3px 6px rgba(0, 0, 0, 0.15);
}

/* Add track styling for better visual feedback */
input[type="range"]::-webkit-slider-runnable-track {
  width: 100%;
  height: 4px;
  background: linear-gradient(to right, #4e843d 0%, #4e843d var(--range-progress, 50%), #e2e8f0 var(--range-progress, 50%));
  border-radius: 2px;
  border: none;
}

input[type="range"]::-moz-range-track {
  width: 100%;
  height: 4px;
  background: linear-gradient(to right, #4e843d 0%, #4e843d var(--range-progress, 50%), #e2e8f0 var(--range-progress, 50%));
  border-radius: 2px;
  border: none;
}

input[type="range"]:focus {
  outline: none;
}

input[type="range"]:focus::-webkit-slider-thumb {
  box-shadow: 0 0 0 3px rgba(78, 132, 61, 0.2);  /* Wego green with opacity */
}

input[type="range"]:focus::-moz-range-thumb {
  box-shadow: 0 0 0 3px rgba(78, 132, 61, 0.2);  /* Wego green with opacity */
}

.logo {
  cursor: move;
  user-select: none;
}
</style>

<script setup>
import { onMounted, onUnmounted, ref, computed, watch, nextTick } from 'vue';
import { ExclamationCircleIcon } from '@heroicons/vue/16/solid';
import * as d3 from 'd3';
import * as XLSX from 'xlsx';
import { companyNames, getCompanyColor, getCompanyLogo } from '../data/companyMeta'


// companyNames, colors, and logos are centralized in src/data/companyMeta.js

const currentYearIndex = ref(0);
const years = ref([]);
const mergedData = ref([]);
const isLoading = ref(true);

// Define props - receive company filter from parent
const props = defineProps({
  companyFilter: {
    type: Object,
    default: () => ({})
  }
});

// Add emit definition
const emit = defineEmits(['data-update', 'company-select', 'quarters-loaded', 'companies-loaded']);

// Add these as component-level variables to maintain consistent scales
let xScale, yScale;

// Add chart dimensions
const margin = { top: 50, right: 100, bottom: 50, left: 60 };
const chartRef = ref(null);
let update; // Declare update function reference

// Create a map to store custom ranges for each quarter
const quarterRanges = ref({});
// Flag to track if user has manually set ranges for current quarter
const currentQuarterHasCustomRange = ref(false);

// Add axis range state
const xAxisRange = ref({
  min: '-50',
  max: '80',
  minError: '',
  maxError: ''
});

const yAxisRange = ref({
  min: '-30',
  max: '110',
  minError: '',
  maxError: ''
});

// Default ranges for when no data is available
const DEFAULT_X_DOMAIN = [-0.5, 0.8]; // Default EBITDA range: -50% to 80%
const DEFAULT_Y_DOMAIN = [-0.3, 1.1]; // Default Revenue growth range: -30% to 110%

// Add after the axis range state declarations
const chartDimensions = ref({
  width: '1200',
  height: '840',
  widthError: '',
  heightError: ''
});

// Add new validation function for dimensions
const validateAndUpdateDimensions = (dimension) => {
  const value = parseInt(chartDimensions.value[dimension]);
  
  // Clear error first
  chartDimensions.value[`${dimension}Error`] = '';
  
  // Validate input is a number
  if (isNaN(value)) {
    chartDimensions.value[`${dimension}Error`] = 'Please enter a valid number';
    return;
  }
  
  // Validate minimum size
  if (value < 200) {
    chartDimensions.value[`${dimension}Error`] = 'Value must be at least 200px';
    return;
  }
  
  // Validate maximum size
  if (value > 5000) {
    chartDimensions.value[`${dimension}Error`] = 'Value must not exceed 5000px';
    return;
  }
  
  // Update chart if input is valid
  if (!chartDimensions.value.widthError && !chartDimensions.value.heightError) {
    console.log('Updating chart dimensions:', {
      width: parseInt(chartDimensions.value.width),
      height: parseInt(chartDimensions.value.height)
    });
    initChart();
    update(currentYearIndex.value);
  }
};

// Add validation and update function
const validateAndUpdateRange = (axis, bound) => {
  const range = axis === 'x' ? xAxisRange.value : yAxisRange.value;
  const value = parseFloat(range[bound]);
  
  // Clear error first
  range[`${bound}Error`] = '';
  
  // Validate input is a number
  if (isNaN(value)) {
    range[`${bound}Error`] = 'Please enter a valid number';
    return;
  }
  
  // Validate min is less than max
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
  
  // Mark current quarter as having custom range
  if (years.value.length > 0) {
    const currentQuarter = years.value[currentYearIndex.value];
    if (currentQuarter) {
      currentQuarterHasCustomRange.value = true;
      
      // Initialize range for current quarter if it doesn't exist
      if (!quarterRanges.value[currentQuarter]) {
        quarterRanges.value[currentQuarter] = {
          xDomain: [
            parseFloat(xAxisRange.value.min) / 100,
            parseFloat(xAxisRange.value.max) / 100
          ],
          yDomain: [
            parseFloat(yAxisRange.value.min) / 100,
            parseFloat(yAxisRange.value.max) / 100
          ]
        };
      }
      
      // Update the specific axis that was changed
      if (axis === 'x') {
        const xMin = parseFloat(xAxisRange.value.min) / 100;
        const xMax = parseFloat(xAxisRange.value.max) / 100;
        if (!isNaN(xMin) && !isNaN(xMax) && xMin < xMax) {
          quarterRanges.value[currentQuarter].xDomain = [xMin, xMax];
          console.log(`Updated X axis domain for ${currentQuarter}:`, quarterRanges.value[currentQuarter].xDomain);
        }
      } else {
        const yMin = parseFloat(yAxisRange.value.min) / 100;
        const yMax = parseFloat(yAxisRange.value.max) / 100;
        if (!isNaN(yMin) && !isNaN(yMax) && yMin < yMax) {
          quarterRanges.value[currentQuarter].yDomain = [yMin, yMax];
          console.log(`Updated Y axis domain for ${currentQuarter}:`, quarterRanges.value[currentQuarter].yDomain);
        }
      }
    }
  }
  
  // Only update chart if both values are valid and min < max
  if (!range.minError && !range.maxError) {
    console.log('Updating chart with custom ranges');
    initChart();
    update(currentYearIndex.value);
  }
};

// Note: Company filter is managed by parent (App.vue) and passed as prop

// Helper function to check if component is visible (v-show)
const isComponentVisible = () => {
  if (!chartRef.value) return false;
  // Check if element is visible (v-show sets display:none when hidden)
  return chartRef.value.offsetParent !== null;
};

// Helper function to stop all D3 transitions
const stopAllTransitions = () => {
  if (!chartRef.value) return;
  d3.select(chartRef.value).selectAll('*').interrupt();
  console.log('Stopped all D3 transitions in AnimatedBubbleChart');
};

// Watch for company filter changes and refresh chart immediately
watch(() => props.companyFilter, (newFilter) => {
  console.log('Company filter changed:', newFilter);
  // Only update if component is visible
  if (update && years.value.length > 0 && isComponentVisible()) {
    console.log('Auto-refreshing chart due to filter change');
    update(currentYearIndex.value);
  } else if (!isComponentVisible()) {
    console.log('Component not visible, skipping update');
  }
}, { deep: true });

// Function to get chart dimensions
const getChartDimensions = () => {
  const container = document.getElementById('additional-chart');
  if (!container) return { width: 800, height: 600 };
  return {
    width: container.clientWidth,
    height: container.clientHeight
  };
};

// Function to process XLSX data
const processExcelData = (file) => {
  console.log('Starting to process Excel file:', file.name);
  const reader = new FileReader();
  
  reader.onload = async (e) => {
    try {
      const data = new Uint8Array(e.target.result);
      const workbook = XLSX.read(data, { type: 'array' });
      console.log('Available sheets:', workbook.SheetNames);
      
      // Get the TTM sheet
      const ttmSheet = workbook.Sheets['TTM (bounded)'];
      if (!ttmSheet) {
        throw new Error('TTM (bounded) sheet not found');
      }

      // Convert sheet to JSON with headers
      const jsonData = XLSX.utils.sheet_to_json(ttmSheet, { header: 1 });
      console.log('First row (headers):', jsonData[0]);
      
      // Get headers (company names) from first row, skip first column
      // 保留空表头以保持列索引与数据列对齐
      const rawHeaderRow = jsonData[0] || [];
      const headers = rawHeaderRow.slice(1).map(h => (h && String(h).trim()) || null);
      console.log('Processed headers (length, including nulls):', headers.length, headers);
      
      // Extract company names (filter out null/empty headers)
      const companiesFromBubbleData = headers.filter(h => h !== null && h !== '');
      console.log('Companies from bubble data:', companiesFromBubbleData);
      
      // Emit companies to parent for filter management
      emit('companies-loaded', companiesFromBubbleData);
      console.log('Emitted companies-loaded event with', companiesFromBubbleData.length, 'companies');
      
      // Find Revenue Growth row
      const revenueGrowthRowIndex = jsonData.findIndex(row => 
        row && row[0] && String(row[0]) === 'Rev Growth YoY'
      );
      
      // Find EBITDA Margin row
      const ebitdaStartIndex = jsonData.findIndex(row => 
        row && row[0] && String(row[0]) === 'EBITDA Margin % Quarterly'
      );
      
      if (revenueGrowthRowIndex === -1) {
        throw new Error('Revenue Growth row not found');
      }
      
      if (ebitdaStartIndex === -1) {
        throw new Error('EBITDA Margin row not found');
      }
      
      // Process data rows
      const processedData = [];
      const quarters = new Set();
      
      // 记录所有数据的最大最小值
      let globalMinEbitda = DEFAULT_X_DOMAIN[0];
      let globalMaxEbitda = DEFAULT_X_DOMAIN[1];
      let globalMinRevenue = DEFAULT_Y_DOMAIN[0];
      let globalMaxRevenue = DEFAULT_Y_DOMAIN[1];
      
      // Function to check if a string is a valid quarter
      const isValidQuarter = (str) => {
        if (!str) return false;
        str = String(str).trim();
        // Remove any potential whitespace or special characters
        str = str.replace(/\s+/g, '');
        const quarterPattern = /^\d{4}'Q[1-4]$/;
        if (!quarterPattern.test(str)) {
          console.log(`Quarter ${str} rejected: invalid format`);
          return false;
        }
        
        // Extract year and quarter
        const match = str.match(/^(\d{4})'Q(\d)$/);
        const yearNum = parseInt(match[1]);
        const quarterNum = parseInt(match[2]);
        
        // Only accept data between 2016'Q1 and 2025'Q1
        if (yearNum < 2016 || yearNum > 2025) {
          console.log(`Quarter ${str} rejected: year ${yearNum} outside range 2016-2025`);
          return false;
        }
        
        console.log(`Quarter ${str} accepted: within valid range`);
        return true;
      };
      
      // Process revenue growth data
      let currentRowIndex = revenueGrowthRowIndex + 1;
      
      // Debug log for revenue growth section
      console.log('=== Revenue Growth Section ===');
      console.log('First 5 rows after Revenue Growth:');
      for (let i = revenueGrowthRowIndex; i < revenueGrowthRowIndex + 6; i++) {
        console.log(`Row ${i}:`, jsonData[i]);
      }
      
      let currentQuarter = jsonData[currentRowIndex]?.[0];
      if (currentQuarter) {
        currentQuarter = String(currentQuarter).trim().replace(/\s+/g, '');
      }
      
      // Add safety check for data
      if (!currentQuarter) {
        console.error('No quarter data found at row:', currentRowIndex);
        console.error('Row data:', jsonData[currentRowIndex]);
        throw new Error('No valid quarter data found after Revenue Growth row');
      }
      
      while (currentRowIndex < jsonData.length && currentRowIndex < ebitdaStartIndex) {
        const rowData = jsonData[currentRowIndex];
        if (!rowData || !Array.isArray(rowData)) {
          console.warn(`Invalid row data at index ${currentRowIndex}`);
          currentRowIndex++;
          currentQuarter = jsonData[currentRowIndex]?.[0];
          if (currentQuarter) {
            currentQuarter = String(currentQuarter).trim().replace(/\s+/g, '');
          }
          continue;
        }
        
        currentQuarter = String(rowData[0] || '').trim().replace(/\s+/g, '');
        if (isValidQuarter(currentQuarter)) {
          quarters.add(currentQuarter);
          
          // Store revenue growth data for this quarter
          headers.forEach((company, j) => {
            if (!company) return;
            
            const colIndex = j + 1;
            const revenueGrowth = parseFloat(rowData[colIndex]);
            
            if (!isNaN(revenueGrowth)) {
              processedData.push({
                quarter: currentQuarter,
                company,
                revenueGrowth: revenueGrowth / 100,
                ebitdaMargin: null,
                hasBothQuarters: false
              });
            }
          });
        }
        
        currentRowIndex++;
      }
      
      // Process EBITDA margin data
      currentRowIndex = ebitdaStartIndex + 1;
      
      // Debug log for EBITDA section
      console.log('=== EBITDA Section ===');
      console.log('EBITDA start index:', ebitdaStartIndex);
      console.log('Next 5 rows after EBITDA Margin row:');
      for (let i = ebitdaStartIndex; i < ebitdaStartIndex + 6; i++) {
        console.log(`Row ${i}:`, jsonData[i]);
      }
      
      currentQuarter = jsonData[currentRowIndex]?.[0];
      if (currentQuarter) {
        currentQuarter = String(currentQuarter).trim().replace(/\s+/g, '');
      }
      
      while (currentRowIndex < jsonData.length) {
        const rowData = jsonData[currentRowIndex];
        if (!rowData || !Array.isArray(rowData)) {
          console.warn(`Invalid row data at index ${currentRowIndex}`);
          currentRowIndex++;
          currentQuarter = jsonData[currentRowIndex]?.[0];
          if (currentQuarter) {
            currentQuarter = String(currentQuarter).trim().replace(/\s+/g, '');
          }
          continue;
        }
        
        currentQuarter = String(rowData[0] || '').trim().replace(/\s+/g, '');
        if (isValidQuarter(currentQuarter)) {
          console.log(`Processing EBITDA data for quarter: ${currentQuarter}`);
          
          // Update EBITDA margin for existing data points
          headers.forEach((company, j) => {
            if (!company) return;
            
            const colIndex = j + 1;
            const ebitdaMargin = parseFloat(rowData[colIndex]);
            
            if (!isNaN(ebitdaMargin)) {
              const existingDataPoint = processedData.find(
                d => d.quarter === currentQuarter && d.company === company
              );
              
              if (existingDataPoint) {
                console.log(`Updating EBITDA for ${company} in ${currentQuarter}: ${ebitdaMargin}`);
                existingDataPoint.ebitdaMargin = ebitdaMargin / 100;
                existingDataPoint.hasBothQuarters = true;
              } else {
                console.log(`No revenue data found for ${company} in ${currentQuarter}, EBITDA: ${ebitdaMargin}`);
              }
            }
          });
        }
        
        currentRowIndex++;
      }
      
      // Filter out incomplete data points
      mergedData.value = processedData.filter(d => d.hasBothQuarters);

      // Sort quarters chronologically
      years.value = Array.from(quarters).sort((a, b) => {
        const [yearA, quarterA] = a.split("'");
        const [yearB, quarterB] = b.split("'");
        return parseInt(yearA) - parseInt(yearB) || 
               parseInt(quarterA.slice(1)) - parseInt(quarterB.slice(1));
      });

      const quarterOrderMap = years.value.reduce((acc, quarter, index) => {
        acc[quarter] = index;
        return acc;
      }, {});

      mergedData.value.sort((a, b) => {
        const orderA = quarterOrderMap[a.quarter] ?? Number.POSITIVE_INFINITY;
        const orderB = quarterOrderMap[b.quarter] ?? Number.POSITIVE_INFINITY;
        if (orderA !== orderB) {
          return orderA - orderB;
        }
        return a.company.localeCompare(b.company, 'en', { sensitivity: 'base' });
      });

      // We no longer need to set global ranges during data load
      // Each quarter will get its own range when first viewed

      console.log('=== Data Processing Debug ===')
      console.log('Total processed data points before filtering:', processedData.length);
      console.log('Sample of processed data before filtering:', processedData.slice(0, 5));
      console.log('Total merged data points after filtering:', mergedData.value.length);
      console.log('Sample of merged data after filtering:', mergedData.value.slice(0, 5));
      console.log('Quarters with data:', years.value);

      if (mergedData.value.length === 0) {
        throw new Error('No valid data points found after processing');
      }
      
      // Emit quarters loaded event
      emit('quarters-loaded', {
        quarters: years.value,
        currentIndex: currentYearIndex.value
      });
      
      // Initialize chart
      console.log('Initializing chart with:', {
        quarters: years.value,
        currentIndex: currentYearIndex.value,
        dataPoints: mergedData.value.length
      });
      
      initChart();
      update(currentYearIndex.value);  // Initial update
      
      // Hide loading indicator after chart is rendered
      isLoading.value = false;
      
    } catch (error) {
      console.error('Error processing Excel file:', error);
      console.error('Error stack:', error.stack);
      alert('处理数据时出错：' + error.message);
      isLoading.value = false;
    }
  };
  
  reader.onerror = (error) => {
    console.error('Error reading file:', error);
    console.error('Error stack:', error.stack);
    alert('读取文件时出错');
  };
  
  reader.readAsArrayBuffer(file);
};

// Add computed property for current quarter display
const currentQuarter = computed(() => {
  if (!years.value.length) return '';
  return years.value[currentYearIndex.value];
});

// Handle slider change
const handleSliderChange = (event) => {
  const newIndex = parseInt(event?.target?.value || event);
  if (isNaN(newIndex)) return;
  
  // Reset custom range flag when changing quarters
  currentQuarterHasCustomRange.value = false;
  currentYearIndex.value = newIndex;
  
  // Only update if component is visible
  if (update && isComponentVisible()) {
    update(currentYearIndex.value);
  } else if (!isComponentVisible()) {
    console.log('Component not visible, skipping slider update');
  }
};

// Add save chart function
const saveChart = async () => {
  try {
    const svgNode = document.querySelector('#additional-chart svg');
    const svgWidth = svgNode.viewBox.baseVal.width || 1200;
    const svgHeight = svgNode.viewBox.baseVal.height || 840;
    
    // First, load all images
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
    
    // Set ultra-high resolution scale
    const scale = 8;  // Increased from 4 to 8 for maximum quality
    canvas.width = svgWidth * scale;
    canvas.height = svgHeight * scale;
    
    // Enable maximum quality image rendering
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';
    
    // Set white background
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Set image source with proper SVG dimensions
    const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
    const svgUrl = URL.createObjectURL(svgBlob);
    
    return new Promise((resolve, reject) => {
      img.onload = () => {
        try {
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
          URL.revokeObjectURL(svgUrl);
          
          // Convert to PNG and download
          const link = document.createElement('a');
          link.download = `market_performance_${years.value[currentYearIndex.value]}.png`;
          link.href = canvas.toDataURL('image/png');
          link.click();
          resolve();
        } catch (error) {
          reject(error);
        }
      };
      img.onerror = () => {
        URL.revokeObjectURL(svgUrl);
        reject(new Error('Failed to load SVG'));
      };
      img.src = svgUrl;
    });
  } catch (error) {
    console.error('Error saving chart:', error);
    throw error;
  }
};

// Initialize the chart
const initChart = () => {
  const width = parseInt(chartDimensions.value.width);
  const height = parseInt(chartDimensions.value.height);
  console.log('Initializing chart with dimensions:', width, height);
  
  // Clear existing SVG
  d3.select('#additional-chart').selectAll("*").remove();
    
  // Create SVG with viewBox for better scaling
  const svg = d3.select('#additional-chart')
    .append("svg")
    .attr("width", "100%")
    .attr("height", "100%")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("preserveAspectRatio", "xMidYMid meet");
    
  // Add background
  svg.append("rect")
    .attr("width", "100%")
    .attr("height", "100%")
    .attr("fill", "white");
    
  // Create scales with default domains
  xScale = d3.scaleLinear()
      .domain(DEFAULT_X_DOMAIN)
    .range([margin.left, width - margin.right]);

  yScale = d3.scaleLinear()
      .domain(DEFAULT_Y_DOMAIN)
    .range([height - margin.bottom, margin.top]);

    // Add axes
  const xAxis = d3.axisBottom(xScale)
    .ticks(8)  // Increased number of ticks
    .tickFormat(d => (d * 100).toFixed(0) + "%");
    
  const yAxis = d3.axisLeft(yScale)
    .ticks(8)  // Increased number of ticks
    .tickFormat(d => (d * 100).toFixed(0) + "%");
    
  svg.append("g")
    .attr("transform", `translate(0,${height - margin.bottom})`)
    .attr("class", "x-axis")
    .call(xAxis);

  svg.append("g")
    .attr("transform", `translate(${margin.left},0)`)
    .attr("class", "y-axis")
    .call(yAxis);

  // Add labels
  svg.append("text")
    .attr("class", "x-label")
    .attr("text-anchor", "middle")
    .attr("x", width / 2)
    .attr("y", height - 10)
    .text("EBITDA Margin (%)");
    
  svg.append("text")
    .attr("class", "y-label")
    .attr("text-anchor", "middle")
    .attr("transform", "rotate(-90)")
    .attr("x", -height / 2)
    .attr("y", 15)
    .text("Revenue Growth YoY (%)");
    
    /* Remove quarter display
  const quarterDisplay = svg.append("text")
    .attr("class", "quarter-display")
    .attr("x", width - margin.right)
    .attr("y", margin.top)
    .attr("text-anchor", "end")
    .attr("font-size", "24px")
    .attr("font-weight", "bold");
    */
    
  // Add tooltip
  const tooltip = d3.select(chartRef.value)
    .append("div")
    .attr("class", "tooltip");

    // Define update function
    update = (quarterIndex) => {
      // Check if component is visible before any D3 operations
      if (!isComponentVisible()) {
        console.log('AnimatedBubbleChart not visible, skipping update');
        return;
      }
      
      console.log('=== Update Function Start ===');
      console.log('Updating chart for quarter:', years.value[quarterIndex]);
      console.log('Company filter state:', props.companyFilter);
      
      // Filter data for current quarter and company filter
      const currentData = mergedData.value.filter(d => {
        const isSelectedQuarter = d.quarter === years.value[quarterIndex];
        // Apply company filter - if filter is empty or not set, show all; otherwise check filter
        const isCompanyFiltered = Object.keys(props.companyFilter).length === 0 || 
                                   props.companyFilter[d.company] === true;
        
        // Debug log for each company
        if (isSelectedQuarter) {
          console.log(`Company ${d.company}: filtered=${isCompanyFiltered}, will show=${isSelectedQuarter && isCompanyFiltered}`);
        }
        
        return isSelectedQuarter && isCompanyFiltered;
      });
      
      console.log(`Filtered data for rendering: ${currentData.length} companies out of ${mergedData.value.filter(d => d.quarter === years.value[quarterIndex]).length} total in this quarter`);
      
      // Calculate current quarter data range
      const currentQuarter = years.value[quarterIndex];
      console.log(`Updating chart for quarter: ${currentQuarter}`);
      
      // Always update axes, even when no data (to reset to proper ranges)
      let shouldUpdateAxes = true;
      
      if (currentData.length > 0) {
        // Check if user has manually set ranges for this quarter
        if (currentQuarterHasCustomRange.value && quarterRanges.value[currentQuarter]) {
          const customRange = quarterRanges.value[currentQuarter];
          console.log(`Using custom ranges for ${currentQuarter}:`, {
            xDomain: customRange.xDomain.map(v => (v*100).toFixed(1) + '%'),
            yDomain: customRange.yDomain.map(v => (v*100).toFixed(1) + '%')
          });
          
          // Use the custom ranges for this quarter
          xScale.domain(customRange.xDomain);
          yScale.domain(customRange.yDomain);
          
          // Update UI input values to match the custom range
          xAxisRange.value.min = (customRange.xDomain[0] * 100).toFixed(0);
          xAxisRange.value.max = (customRange.xDomain[1] * 100).toFixed(0);
          yAxisRange.value.min = (customRange.yDomain[0] * 100).toFixed(0);
          yAxisRange.value.max = (customRange.yDomain[1] * 100).toFixed(0);
        }
        // Check if we already calculated optimal range for this quarter
        else if (quarterRanges.value[currentQuarter]) {
          const savedRange = quarterRanges.value[currentQuarter];
          
          // 验证保存的范围是否能容纳所有当前数据点
          const ebitdaValues = currentData
            .map(d => d.ebitdaMargin)
            .filter(v => Number.isFinite(v));
          const revenueValues = currentData
            .map(d => d.revenueGrowth)
            .filter(v => Number.isFinite(v));
          
          const minEbitda = Math.min(...ebitdaValues);
          const maxEbitda = Math.max(...ebitdaValues);
          const minRevenue = Math.min(...revenueValues);
          const maxRevenue = Math.max(...revenueValues);
          
          const rangeNeedsUpdate = 
            minEbitda < savedRange.xDomain[0] || 
            maxEbitda > savedRange.xDomain[1] ||
            minRevenue < savedRange.yDomain[0] ||
            maxRevenue > savedRange.yDomain[1];
          
          if (rangeNeedsUpdate) {
            console.log(`Saved range for ${currentQuarter} cannot contain all data points, recalculating...`);
            console.log('Current data range:', {
              ebitda: `${(minEbitda * 100).toFixed(1)}% to ${(maxEbitda * 100).toFixed(1)}%`,
              revenue: `${(minRevenue * 100).toFixed(1)}% to ${(maxRevenue * 100).toFixed(1)}%`
            });
            console.log('Saved range:', {
              ebitda: `${(savedRange.xDomain[0] * 100).toFixed(1)}% to ${(savedRange.xDomain[1] * 100).toFixed(1)}%`,
              revenue: `${(savedRange.yDomain[0] * 100).toFixed(1)}% to ${(savedRange.yDomain[1] * 100).toFixed(1)}%`
            });
            
            // 重新计算范围（使用新的 outlier 检测逻辑）
            const computeTrimmedDomain = (values, defaultDomain, label, dataPoints) => {
              if (!values.length) {
                return defaultDomain;
              }
              const sorted = [...values].sort((a, b) => a - b);
              const wegoDataPoint = dataPoints.find(d => d.company === 'Wego');
              const wegoValue = label === 'EBITDA' ? wegoDataPoint?.ebitdaMargin : wegoDataPoint?.revenueGrowth;
              const outliers = new Set();
              
              for (let i = 0; i < Math.min(3, sorted.length - 1); i++) {
                const current = sorted[i];
                const next = sorted[i + 1];
                const max = sorted[sorted.length - 1];
                const gap = next - current;
                const rangeToMax = max - next;
                if (gap > rangeToMax / 2 && current !== wegoValue) {
                  outliers.add(current);
                } else {
                  break;
                }
              }
              
              for (let i = sorted.length - 1; i > Math.max(sorted.length - 4, 0); i--) {
                const current = sorted[i];
                const prev = sorted[i - 1];
                const min = sorted[0];
                const gap = current - prev;
                const rangeFromMin = prev - min;
                if (gap > rangeFromMin / 2 && current !== wegoValue) {
                  outliers.add(current);
                } else {
                  break;
                }
              }
              
              const filtered = sorted.filter(v => !outliers.has(v));
              if (filtered.length === 0) return defaultDomain;
              
              const trimmedMin = filtered[0];
              const trimmedMax = filtered[filtered.length - 1];
              const range = trimmedMax - trimmedMin;
              const margin = Math.max(0.05, range * 0.1);
              
              return [trimmedMin - margin, trimmedMax + margin];
            };
            
            const currentXDomain = computeTrimmedDomain(ebitdaValues, DEFAULT_X_DOMAIN, 'EBITDA', currentData);
            const currentYDomain = computeTrimmedDomain(revenueValues, DEFAULT_Y_DOMAIN, 'Revenue Growth', currentData);
            
            // 更新保存的范围
            quarterRanges.value[currentQuarter] = {
              xDomain: currentXDomain,
              yDomain: currentYDomain
            };
            
            xScale.domain(currentXDomain);
            yScale.domain(currentYDomain);
            
            xAxisRange.value.min = (currentXDomain[0] * 100).toFixed(0);
            xAxisRange.value.max = (currentXDomain[1] * 100).toFixed(0);
            yAxisRange.value.min = (currentYDomain[0] * 100).toFixed(0);
            yAxisRange.value.max = (currentYDomain[1] * 100).toFixed(0);
          } else {
            console.log(`Using saved optimal ranges for ${currentQuarter}:`, {
              xDomain: savedRange.xDomain.map(v => (v*100).toFixed(1) + '%'),
              yDomain: savedRange.yDomain.map(v => (v*100).toFixed(1) + '%')
            });
            
            // Use the saved ranges
            xScale.domain(savedRange.xDomain);
            yScale.domain(savedRange.yDomain);
            
            // Update UI input values to match
            xAxisRange.value.min = (savedRange.xDomain[0] * 100).toFixed(0);
            xAxisRange.value.max = (savedRange.xDomain[1] * 100).toFixed(0);
            yAxisRange.value.min = (savedRange.yDomain[0] * 100).toFixed(0);
            yAxisRange.value.max = (savedRange.yDomain[1] * 100).toFixed(0);
          }
        }
        // Otherwise calculate optimal range for this quarter
        else {
          // Extract value ranges for current quarter data
          const ebitdaValues = currentData
            .map(d => d.ebitdaMargin)
            .filter(v => Number.isFinite(v));
          const revenueValues = currentData
            .map(d => d.revenueGrowth)
            .filter(v => Number.isFinite(v));

          const computeTrimmedDomain = (values, defaultDomain, label, dataPoints) => {
            if (!values.length) {
              console.warn(`No ${label} values found for domain calculation, using default range`);
              return defaultDomain;
            }

            const sorted = [...values].sort((a, b) => a - b);
            
            // 获取 Wego 的数据值（必须始终显示）
            const wegoDataPoint = dataPoints.find(d => d.company === 'Wego');
            const wegoValue = label === 'EBITDA' ? wegoDataPoint?.ebitdaMargin : wegoDataPoint?.revenueGrowth;
            
            // 识别 outliers：检查每个极端点是否离其相邻点很远
            const outliers = new Set();
            
            // 检查下端（最小值方向），最多检查 3 个
            for (let i = 0; i < Math.min(3, sorted.length - 1); i++) {
              const current = sorted[i];
              const next = sorted[i + 1];
              const max = sorted[sorted.length - 1];
              
              const gap = next - current;
              const rangeToMax = max - next;
              
              // 如果当前点与下一个点的距离 > (最大值 - 下一个点) / 2，则是 outlier
              if (gap > rangeToMax / 2) {
                // Wego 数据点必须始终显示，不能标记为 outlier
                if (current !== wegoValue) {
                  outliers.add(current);
                  console.log(`${label} outlier detected (lower): ${(current * 100).toFixed(1)}% (gap: ${(gap * 100).toFixed(1)}%, threshold: ${(rangeToMax / 2 * 100).toFixed(1)}%)`);
                } else {
                  console.log(`${label} ${(current * 100).toFixed(1)}% is Wego, must be included even though it appears to be an outlier`);
                }
              } else {
                break; // 如果不是 outlier，停止检查
              }
            }
            
            // 检查上端（最大值方向），最多检查 3 个
            for (let i = sorted.length - 1; i > Math.max(sorted.length - 4, 0); i--) {
              const current = sorted[i];
              const prev = sorted[i - 1];
              const min = sorted[0];
              
              const gap = current - prev;
              const rangeFromMin = prev - min;
              
              if (gap > rangeFromMin / 2) {
                if (current !== wegoValue) {
                  outliers.add(current);
                  console.log(`${label} outlier detected (upper): ${(current * 100).toFixed(1)}% (gap: ${(gap * 100).toFixed(1)}%, threshold: ${(rangeFromMin / 2 * 100).toFixed(1)}%)`);
                } else {
                  console.log(`${label} ${(current * 100).toFixed(1)}% is Wego, must be included even though it appears to be an outlier`);
                }
              } else {
                break;
              }
            }

            // 过滤掉 outliers
            const filtered = sorted.filter(v => !outliers.has(v));
            
            if (filtered.length === 0) {
              console.warn(`All ${label} values were outliers, using full range`);
              return defaultDomain;
            }
            
            const trimmedMin = filtered[0];
            const trimmedMax = filtered[filtered.length - 1];

            if (outliers.size > 0) {
              console.log(`${label} excluded ${outliers.size} outlier(s):`, {
                outliers: Array.from(outliers).map(v => (v * 100).toFixed(1) + '%'),
                includedRange: `${(trimmedMin * 100).toFixed(1)}% to ${(trimmedMax * 100).toFixed(1)}%`,
                totalDataPoints: sorted.length,
                includedDataPoints: filtered.length
              });
            }

            const range = trimmedMax - trimmedMin;
            const margin = Math.max(0.05, range * 0.1);

            const calculatedDomain = [trimmedMin - margin, trimmedMax + margin];
            
            console.log(`Calculated ${label} domain:`, {
              domainMin: (calculatedDomain[0] * 100).toFixed(1) + '%',
              domainMax: (calculatedDomain[1] * 100).toFixed(1) + '%',
              dataPoints: filtered.length
            });

            return calculatedDomain;
          };
 
          // Check if current quarter data exceeds default range
          const defaultXDomain = DEFAULT_X_DOMAIN;
          const defaultYDomain = DEFAULT_Y_DOMAIN;
          
          const currentXDomain = computeTrimmedDomain(ebitdaValues, defaultXDomain, 'EBITDA', currentData);
          const currentYDomain = computeTrimmedDomain(revenueValues, defaultYDomain, 'Revenue Growth', currentData);

          // Save this calculated range for future reference
          quarterRanges.value[currentQuarter] = {
            xDomain: currentXDomain,
            yDomain: currentYDomain
          };
          
          // Update scales
          xScale.domain(currentXDomain);
          yScale.domain(currentYDomain);
          
          // Update UI range values
          xAxisRange.value.min = (currentXDomain[0] * 100).toFixed(0);
          xAxisRange.value.max = (currentXDomain[1] * 100).toFixed(0);
          yAxisRange.value.min = (currentYDomain[0] * 100).toFixed(0);
          yAxisRange.value.max = (currentYDomain[1] * 100).toFixed(0);
          
          console.log(`Calculated optimal ranges for ${currentQuarter}:`, {
            xDomain: currentXDomain.map(v => (v*100).toFixed(1) + '%'),
            yDomain: currentYDomain.map(v => (v*100).toFixed(1) + '%')
          });
        }
      } else {
        // No data for current quarter - use saved range or default range
        console.log(`No data available for ${currentQuarter}`);
        
        if (quarterRanges.value[currentQuarter]) {
          // Use saved range if available
          const savedRange = quarterRanges.value[currentQuarter];
          xScale.domain(savedRange.xDomain);
          yScale.domain(savedRange.yDomain);
          
          xAxisRange.value.min = (savedRange.xDomain[0] * 100).toFixed(0);
          xAxisRange.value.max = (savedRange.xDomain[1] * 100).toFixed(0);
          yAxisRange.value.min = (savedRange.yDomain[0] * 100).toFixed(0);
          yAxisRange.value.max = (savedRange.yDomain[1] * 100).toFixed(0);
          
          console.log(`Using saved range for empty quarter ${currentQuarter}`);
        } else {
          // Use default range
          xScale.domain(DEFAULT_X_DOMAIN);
          yScale.domain(DEFAULT_Y_DOMAIN);
          
          xAxisRange.value.min = (DEFAULT_X_DOMAIN[0] * 100).toFixed(0);
          xAxisRange.value.max = (DEFAULT_X_DOMAIN[1] * 100).toFixed(0);
          yAxisRange.value.min = (DEFAULT_Y_DOMAIN[0] * 100).toFixed(0);
          yAxisRange.value.max = (DEFAULT_Y_DOMAIN[1] * 100).toFixed(0);
          
          console.log(`Using default range for empty quarter ${currentQuarter}`);
        }
      }
      
      // Always update axes (moved outside the data check)
      if (shouldUpdateAxes) {
        svg.select(".x-axis").transition().duration(750).call(
          d3.axisBottom(xScale).ticks(8).tickFormat(d => (d * 100).toFixed(0) + "%")
        );
        svg.select(".y-axis").transition().duration(750).call(
          d3.axisLeft(yScale).ticks(8).tickFormat(d => (d * 100).toFixed(0) + "%")
        );
      }
      
      // Emit the current data
      emit('data-update', currentData);
    
    // Log data points that fall outside the axis range (but will still be rendered)
    const currentXDomain = xScale.domain();
    const currentYDomain = yScale.domain();
    const outOfRangePoints = currentData.filter(d => 
      d.ebitdaMargin < currentXDomain[0] || 
      d.ebitdaMargin > currentXDomain[1] ||
      d.revenueGrowth < currentYDomain[0] || 
      d.revenueGrowth > currentYDomain[1]
    );
    
    if (outOfRangePoints.length > 0) {
      console.log(`${outOfRangePoints.length} data point(s) outside axis range (will be clipped):`, 
        outOfRangePoints.map(d => ({
          company: d.company,
          ebitda: (d.ebitdaMargin * 100).toFixed(1) + '%',
          revenue: (d.revenueGrowth * 100).toFixed(1) + '%'
        }))
      );
    }
    
    // Update bubbles - render ALL data points (outliers will naturally fall outside the visible canvas)
    // When users manually adjust axis ranges, outliers can become visible
    const bubbles = svg.selectAll(".bubble")
      .data(currentData, d => d.company);
        
      console.log('Existing bubbles count:', bubbles.size());
      console.log('Entering bubbles count:', bubbles.enter().size());
      console.log('Exiting bubbles count:', bubbles.exit().size());
      
    // Remove old bubbles
    bubbles.exit().remove();
    
    // Add new bubbles
    const bubblesEnter = bubbles.enter()
      .append("g")
      .attr("class", "bubble")
      .attr("transform", d => `translate(${xScale(d.ebitdaMargin)},${yScale(d.revenueGrowth)})`)
      .style("cursor", "pointer");

    // Update bubble and logo sizes
    bubblesEnter.append("circle")
        .attr("r", 6)
        .attr("fill", d => getCompanyColor(d.company))
        .attr("stroke", "white")
        .attr("stroke-width", "2px")
        .attr("opacity", 0.8);

      // Create a group for the logo to make dragging more stable
      const logoGroups = bubblesEnter.append("g")
        .attr("class", "logo-group")
        .style("cursor", "move");

      // Add the logo image
      const logoSize = 96;
      logoGroups.append("image")
        .attr("class", "logo")
        .attr("xlink:href", d => getCompanyLogo(d.company) || "")
        .attr("x", -logoSize/2)
        .attr("y", -logoSize/2 - 25)
        .attr("width", logoSize)
        .attr("height", logoSize)
        .style("pointer-events", "auto");

      // Add invisible background rect to make dragging easier
      logoGroups.insert("rect", "image")
        .attr("class", "logo-hit-area")
        .attr("x", -logoSize/2)
        .attr("y", -logoSize/2 - 20)
        .attr("width", logoSize)
        .attr("height", logoSize)
        .attr("fill", "transparent");

      // Apply drag behavior to the logo groups
      logoGroups.call(d3.drag()
        .on("start", function() {
          d3.select(this).raise();
        })
        .on("drag", function(event) {
          const dx = event.dx;
          const dy = event.dy;
          
          // Update both rect and image positions
          const currentX = parseFloat(d3.select(this).select('image').attr('x'));
          const currentY = parseFloat(d3.select(this).select('image').attr('y'));
          
          d3.select(this).select('rect')
            .attr('x', currentX + dx)
            .attr('y', currentY + dy);
            
          d3.select(this).select('image')
            .attr('x', currentX + dx)
            .attr('y', currentY + dy);
        }));
      
    // Merge enter and update selections
    const allBubbles = bubblesEnter.merge(bubbles);
    
    // Bind click event to all bubbles (new and existing)
    allBubbles.on("click", (event, d) => {
      console.log('Bubble clicked:', d);
      emit('company-select', d);
    });
    
    // Update all bubbles position with transition
    allBubbles.transition()
      .duration(1000)
      .attr("transform", d => `translate(${xScale(d.ebitdaMargin)},${yScale(d.revenueGrowth)})`);
      
    // Add zero lines (only if 0 is within the axis range)
    const xDomain = xScale.domain();
    const yDomain = yScale.domain();
    const zeroLinesData = [];
    
    // Add vertical zero line if 0 is within X axis range
    if (xDomain[0] <= 0 && xDomain[1] >= 0) {
      zeroLinesData.push({ 
        x1: xScale(0), 
        y1: margin.top, 
        x2: xScale(0), 
        y2: height - margin.bottom,
        axis: 'x'
      });
    }
    
    // Add horizontal zero line if 0 is within Y axis range
    if (yDomain[0] <= 0 && yDomain[1] >= 0) {
      zeroLinesData.push({ 
        x1: margin.left, 
        y1: yScale(0), 
        x2: width - margin.right, 
        y2: yScale(0),
        axis: 'y'
      });
    }
    
    const zeroLines = svg.selectAll(".zero-line").data(zeroLinesData, d => d.axis);
    
    // Remove zero lines that are no longer needed
    zeroLines.exit().remove();
    
    // Add or update zero lines
    zeroLines.enter()
      .append("line")
      .attr("class", "zero-line")
      .merge(zeroLines)
      .attr("x1", d => d.x1)
      .attr("y1", d => d.y1)
      .attr("x2", d => d.x2)
      .attr("y2", d => d.y2)
      .attr("stroke", "#4e843d")
      .attr("stroke-dasharray", "4,4")
      .attr("opacity", 0.5);

      console.log('=== Update Function End ===');
  };

    // Initial update
    if (years.value.length > 0) {
      console.log('Performing initial update with index:', currentYearIndex.value);
      update(currentYearIndex.value);
    } else {
      console.warn('No years data available for initial update');
    }
};

// Note: Company selection UI and logic moved to App.vue as global component

// Expose methods
defineExpose({
  processExcelData,
  saveChart,
  currentYearIndex,
  stopAllTransitions,
  handleSliderChange: () => {
    // Simple synchronous call - visibility check inside update()
    if (update && isComponentVisible()) {
      update(currentYearIndex.value);
    }
  }
});
</script> 