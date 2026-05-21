import { onMounted, ref } from 'vue';
import * as d3 from 'd3';
import * as XLSX from 'xlsx';
import { getCompanyColor, getCompanyLogo } from '../data/companyMeta';

let chartData = ref([]);
const isLoading = ref(false);

// Fixed domains for consistent scaling
const globalXDomain = [-0.15, 0.60];  // EBITDA margin range
const globalYDomain = [-0.15, 0.85];  // Revenue growth range

const showLabels = ref(false);

const toggleDataDisplay = () => {
  showLabels.value = !showLabels.value;
  initChart();
};

// Same Google Sheet as App.vue / AnimatedBubbleChart — gid 1144102204 contains
// both the quarterly sections AND the TTM sections in one published CSV.
const GOOGLE_SHEET_URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQYwQTSYwig7AZ0fjPniLVfUUJnLz3PP4f4fBtqkBNPYqrkKtQyZDaB99kHk2eCzuCh5i8oxTPCHeQ9/pub?gid=1144102204&output=csv';

// All known section-header strings so we can detect where one section ends.
const SECTION_HEADERS = new Set([
  'Rev Growth YoY', 'Revenue YoY', 'Revenue growth TTM',
  'EBITDA Margin % Annual', 'EBITDA Margin % Quarterly', 'EBITDA Margin TTM',
  "Rule of 40' TTM",
]);

// Parse the published Google Sheet CSV and extract the most recent row from
// the 'Revenue growth TTM' and 'EBITDA Margin TTM' sections.
const parseCsvData = (csvText) => {
  // Simple split — same approach as App.vue. Multi-line quoted cells in the
  // founding-year row create extra lines, but all section headers and data
  // rows are single-line, so findIndex by content is unaffected.
  const rows = csvText.split('\n').map(row =>
    row.split(',').map(cell => {
      const cleaned = cell.trim().replace(/^["']|["']$/g, '');
      const num = parseFloat(cleaned);
      return isNaN(num) ? cleaned : num;
    })
  );

  const headers = rows[0]; // company names, index 0 is blank label column
  console.log('CSV headers:', headers);

  const revenueGrowthTTMIndex = rows.findIndex(row =>
    row && String(row[0]).trim() === 'Revenue growth TTM'
  );
  const ebitdaMarginTTMIndex = rows.findIndex(row =>
    row && String(row[0]).trim() === 'EBITDA Margin TTM'
  );

  if (revenueGrowthTTMIndex === -1) throw new Error('Revenue growth TTM section not found in sheet');
  if (ebitdaMarginTTMIndex === -1) throw new Error('EBITDA Margin TTM section not found in sheet');

  console.log(`Revenue growth TTM at row ${revenueGrowthTTMIndex}`);
  console.log(`EBITDA Margin TTM at row ${ebitdaMarginTTMIndex}`);

  // Find where a section ends: the next row whose first cell is a known header.
  const nextSectionAfter = (startIndex) => {
    for (let i = startIndex + 1; i < rows.length; i++) {
      if (SECTION_HEADERS.has(String(rows[i]?.[0]).trim())) return i;
    }
    return rows.length;
  };

  // Return the last row inside [startIndex+1, endIndex) that has numeric data.
  const getLastDataRow = (startIndex, endIndex) => {
    let lastRow = null;
    for (let i = startIndex + 1; i < endIndex; i++) {
      const row = rows[i];
      if (!row || !row[0]) continue;
      const hasNumeric = row.slice(1).some(v => typeof v === 'number' && !isNaN(v));
      if (hasNumeric) lastRow = row;
    }
    return lastRow;
  };

  const revenueRow = getLastDataRow(revenueGrowthTTMIndex, nextSectionAfter(revenueGrowthTTMIndex));
  const ebitdaRow  = getLastDataRow(ebitdaMarginTTMIndex,  nextSectionAfter(ebitdaMarginTTMIndex));

  if (!revenueRow) throw new Error('No data rows found in Revenue growth TTM section');
  if (!ebitdaRow)  throw new Error('No data rows found in EBITDA Margin TTM section');

  console.log(`Using revenue row labelled: "${revenueRow[0]}"`);
  console.log(`Using EBITDA row labelled:  "${ebitdaRow[0]}"`);

  const processedData = [];

  headers.forEach((company, j) => {
    if (!company || j === 0) return;
    const companyStr = String(company).trim();
    if (!companyStr) return;

    const revenueGrowth = typeof revenueRow[j] === 'number' ? revenueRow[j] : parseFloat(revenueRow[j]);
    const ebitdaMargin  = typeof ebitdaRow[j]  === 'number' ? ebitdaRow[j]  : parseFloat(ebitdaRow[j]);

    console.log(`${companyStr}: revenue=${revenueGrowth}, ebitda=${ebitdaMargin}`);

    if (!isNaN(revenueGrowth) && !isNaN(ebitdaMargin)) {
      processedData.push({
        company: companyStr,
        ebitdaMargin: ebitdaMargin / 100,
        revenueGrowth: revenueGrowth / 100,
      });
    }
  });

  console.log(`Parsed ${processedData.length} valid data points`);
  return processedData;
};

const fetchDataFromUrl = async () => {
  console.log('Fetching data from Google Sheet...');
  isLoading.value = true;
  try {
    const response = await fetch(GOOGLE_SHEET_URL);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

    const csvText = await response.text();
    const processedData = parseCsvData(csvText);

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

// Manual file upload — reads the original Google Sheet Excel export.
// Searches every sheet for the TTM section headers.
const processExcelData = (file) => {
  console.log('Processing uploaded Excel file:', file.name);
  const reader = new FileReader();

  reader.onload = (e) => {
    try {
      const workbook = XLSX.read(new Uint8Array(e.target.result), { type: 'array' });
      console.log('Available sheets:', workbook.SheetNames);

      // Try every sheet until we find one that has both TTM sections.
      let processedData = [];
      for (const sheetName of workbook.SheetNames) {
        try {
          const sheet = workbook.Sheets[sheetName];
          const csvText = XLSX.utils.sheet_to_csv(sheet);
          processedData = parseCsvData(csvText);
          if (processedData.length > 0) {
            console.log(`Found TTM data in sheet: "${sheetName}"`);
            break;
          }
        } catch (_) {
          // This sheet doesn't have the headers — try the next one.
        }
      }

      if (processedData.length === 0) throw new Error('No TTM data found in any sheet');

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
