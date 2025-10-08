#!/usr/bin/env python
import os
import argparse
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from PIL import Image
from PIL import ImageChops
import io
import plotly.express as px
import plotly.io as pio
from tqdm import tqdm
import warnings
import base64
import webbrowser
from pathlib import Path
warnings.filterwarnings('ignore')

# Add argument parser
parser = argparse.ArgumentParser(description='Generate airline revenue visualization using Plotly')
parser.add_argument('--output', type=str, default='output/airline_revenue_plotly.html', 
                    help='Output HTML file path')
parser.add_argument('--frames-per-year', type=int, default=4, 
                    help='Number of frames to generate per year (default: 4 for quarterly)')
parser.add_argument('--height', type=int, default=800, 
                    help='Height of the visualization in pixels (default: 800)')
parser.add_argument('--width', type=int, default=1600, 
                    help='Width of the visualization in pixels (default: 1600)')
parser.add_argument('--max-airlines', type=int, default=15, 
                    help='Maximum number of airlines to display (default: 15)')
# to change the overall duration, search for "const quarterDuration" instead -- set to 200 for a quick test
parser.add_argument('--transition-duration', type=int, default=500, 
                    help='Transition duration between frames in ms (default: 500)')
args = parser.parse_args()

# Create required directories
output_dir = os.path.dirname(args.output)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created directory: {output_dir}")

# Create a color mapping for regions
region_colors = {
    'North America': '#40E0D0',  # Turquoise
    'Europe': '#4169E1',         # Royal Blue
    'Asia Pacific': '#FF4B4B',   # Red
    'Latin America': '#32CD32',  # Lime Green
    'China': '#FF4B4B',          # Red (same as Asia Pacific)
    'Middle East': '#DEB887',    # Burlywood
    'Russia': '#FF4B4B',         # Red (same as Asia Pacific)
    'Turkey': '#DEB887'          # Burlywood (same as Middle East)
}


def get_logo_path(airline, year, iata_code, month=6):
    """Get the appropriate logo path based on airline name, year and month"""
    # Manually set the start year to 1997 for all airlines.
    # It's just to cover the whole history. Usually the viz will start from 2000.

    # Visit https://logos-world.net/ to find the logos
    # Manually adjust to the same height if you need
    logo_mapping = {
        "easyJet": [
            {"start_year": 1997, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/EasyJet-Logo-History-700x310.jpg"}],
        "Emirates": [
            {"start_year": 1997, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Emirates-Logo-History-700x302.jpg"}],
        "Air France-KLM": [
            {"start_year": 1997, "end_year": 2004, "file": "../99.utility/airline-bar-video/logos/KLM-Logo-1991-500x281.png", "iata": "KL"},
            {"start_year": 2004, "end_year": 2009, "file": "../99.utility/airline-bar-video/logos/Air-France-KLM-Logo-2004-2009-500x281.png", "iata": "AF"},
            {"start_year": 2009, "end_year": 2019, "file": "../99.utility/airline-bar-video/logos/Air-France-KLM-Logo-2009-2019-500x281.png", "iata": "AF"},
            {"start_year": 2019, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Air-France-KLM-Logo-2019-present-500x281.jpg", "iata": "AF"} # have both KLM & Air France-KLM logos here
        ],
        # and also KLM & Air France-KLM separately
        "KLM Royal Dutch": [
            {"start_year": 1997, "end_year": 2011, "file": "../99.utility/airline-bar-video/logos/KLM-Logo-1991-500x281.png"},
            {"start_year": 2011, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/KLM-Logo-2011-500x281.jpg"}
        ],
        "Air France": [
            {"start_year": 1997, "end_year": 2009, "file": "../99.utility/airline-bar-video/logos/Air-France-Logo-1998-2009-700x394.jpg"},
            {"start_year": 2009, "end_year": 2016, "file": "../99.utility/airline-bar-video/logos/Air-France-Logo-2009-2016-700x394.jpg"},
            {"start_year": 2016, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Air-France-Logo-2016-present-700x394.jpg"}
        ],
        "ANA Holdings": [
            {"start_year": 1986, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/All-Nippon-Airways-Logo.jpg"}
        ],
        "Japan Airlines": [
            {"start_year": 1989, "end_year": 2002, "file": "../99.utility/airline-bar-video/logos/Japan-Airlines-Logo-1989-500x281.png"},
            {"start_year": 2002, "end_year": 2011, "file": "../99.utility/airline-bar-video/logos/Japan-Airlines-Logo-2002-500x281.png"},
            {"start_year": 2011, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Japan-Airlines-Logo-500x281.jpg"}
        ],
        "Korean Air": [
            {"start_year": 1984, "end_year": 2025, "file": "../99.utility/airline-bar-video/logos/Korean-Air-Logo-1984-500x281.png"},
            {"start_year": 2025, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Korean-Air-Logo-500x281.jpg"}
        ],
        "American Airlines": [
            {"start_year": 1997, "end_year": 2013, "file": "../99.utility/airline-bar-video/logos/American-Airlines-Logo-1967-2013-700x394.png"},
            {"start_year": 2013, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/American-Airlines-Logo-2013-present-700x394.jpg"}
        ],
        "British Airways": [
            {"start_year": 1997, "end_year": 2008, "file": "../99.utility/airline-bar-video/logos/British-Airways-Logo-1997-500x281.png"},
            {"start_year": 2008, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/British-Airways-Logo-500x281.jpg"}
        ],
        "United Airlines": [
            {"start_year": 1997, "end_year": 2010, "file": "../99.utility/airline-bar-video/logos/United-Airlines-Logo-1998-2010-700x394.png"},
            {"start_year": 2010, "end_year": 2019, "file": "../99.utility/airline-bar-video/logos/United-Airlines-Logo-2010-2019-700x394.png"},
            {"start_year": 2019, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/United-Airlines-Logo-2019-present-700x394.jpg"}
        ],
        "Delta Air Lines": [
            {"start_year": 1997, "end_year": 2007, "file": "../99.utility/airline-bar-video/logos/Delta-Air-Lines-Second-era-Logo-2000-2004-700x394.png"},
            {"start_year": 2004, "end_year": 2007, "file": "../99.utility/airline-bar-video/logos/Delta-Air-Lines-Second-era-Logo-2004-2007-700x394.png"},
            {"start_year": 2007, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Delta-Air-Lines-Second-era-Logo-2007-present-700x394.png"}
        ],
        "Southwest Airlines": [
            {"start_year": 1989, "end_year": 2014, "file": "../99.utility/airline-bar-video/logos/Southwest-Airlines-Logo-1998-2014-700x394.png"},
            {"start_year": 2014, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Southwest-Airlines-Logo-2014-present-700x394.jpg"}
        ],
        "Lufthansa": [
            {"start_year": 1997, "end_year": 2018, "file": "../99.utility/airline-bar-video/logos/Lufthansa-Logo-1963-2018-700x394.png"},
            {"start_year": 2018, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Lufthansa-Logo-2018-present-700x394.jpg"}
        ],
        "Deutsche Lufthansa": [
            {"start_year": 1997, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/deutsche luft hansa.png"}
        ],
        "Air China": [
            {"start_year": 1997, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Air-China-Logo-500x281.jpg"}],
        "China Southern": [
            {"start_year": 1997, "end_year": 2004, "file": "../99.utility/airline-bar-video/logos/China-Southern-Logo-1988-500x281.png"},
            {"start_year": 2004, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/China-Southern-Logo-2004-500x281.png"},
            {"start_year": 2007, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/China-Southern-Logo-2007-500x281.png"}
        ],
        "China Eastern": [
            {"start_year": 1997, "end_year": 2014, "file": "../99.utility/airline-bar-video/logos/China-Eastern-Airlines-Logo-1988-500x281.png"},
            {"start_year": 2014, "end_year": 2018, "file": "../99.utility/airline-bar-video/logos/China-Eastern-Airlines-Logo-2014-500x281.png"},
            {"start_year": 2018, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/China-Eastern-Airlines-Logo-500x281.jpg"}
        ],
        "Singapore Airlines": [
            {"start_year": 1997, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Singapore-Airlines-Logo-500x281.png"}],
        "LATAM Airlines": [
            {"start_year": 1997, "end_year": 2012, "file": "../99.utility/airline-bar-video/logos/LAN-Chile-Logo-1998-500x281.png"},
            {"start_year": 2012, "end_year": 2016, "file": "../99.utility/airline-bar-video/logos/LATAM-Airlines-Group-Logo-2012-500x281.png"},
            {"start_year": 2016, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/LATAM-Airlines-Logo-2016-500x281.jpg"}
        ],
        "Hainan Airlines": [
            {"start_year": 1997, "end_year": 2004, "file": "../99.utility/airline-bar-video/logos/Hainan-Airlines-Logo-1993-500x281.png"},
            {"start_year": 2004, "end_year": 2013, "file": "../99.utility/airline-bar-video/logos/Hainan-Airlines-Logo-2004-500x281.png"},
            {"start_year": 2013, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Hainan-Airlines-Logo-2013-500x281.jpg"}
        ],
        "Qatar Airways": [
            {"start_year": 1997, "end_year": 2006, "file": "../99.utility/airline-bar-video/logos/Qatar-Airways-Logo-1997-2006-700x394.png"},
            {"start_year": 2006, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Qatar-Airways-Logo-2006-present-700x394.jpg"}
        ],
        "Turkish Airlines": [
            {"start_year": 1997, "end_year": 2008, "file": "../99.utility/airline-bar-video/logos/Turkish-Airlines-Logo-1990-2008-700x394.png"},
            {"start_year": 2008, "end_year": 2010, "file": "../99.utility/airline-bar-video/logos/Turkish-Airlines-Logo-2008-2010-700x394.jpg"},
            {"start_year": 2010, "end_year": 2018, "file": "../99.utility/airline-bar-video/logos/Turkish-Airlines-Logo-2010-2017-700x394.png"},
            {"start_year": 2018, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Turkish-Airlines-Logo-2018-present-700x394.jpg"}
        ],
        "JetBlue": [
            {"start_year": 1997, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/JetBlue-Logo-500x281.jpg"}],
        "SkyWest": [
            {"start_year": 1972, "end_year": 2001, "file": "../99.utility/airline-bar-video/logos/SkyWest-Logo-1972-500x281.png"},
            {"start_year": 2001, "end_year": 2018, "file": "../99.utility/airline-bar-video/logos/SkyWest-Logo-2001-500x281.png"},
            {"start_year": 2018, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/SkyWest-Logo-2018-500x281.jpg"}
        ],
        "Northwest Airlines": [
            {"start_year": 1997, "end_year": 2003, "file": "../99.utility/airline-bar-video/logos/Northwest-Airlines-Logo-1989-500x281.png"},
            {"start_year": 2003, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Northwest-Airlines-Logo-2003-500x281.jpg"}
        ],
        "TWA": [
            {"start_year": 1997, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Trans_World_Airlines.png"}],
        "Air Canada": [
            {"start_year": 1995, "end_year": 2005, "file": "../99.utility/airline-bar-video/logos/Air-Canada-Logo-1994-2005-700x394.png"},
            {"start_year": 2005, "end_year": 2017, "file": "../99.utility/airline-bar-video/logos/Air-Canada-Logo-2005-2017-700x394.png"},
            {"start_year": 2017, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Air-Canada-Logo-2017-present-700x394.png"}
        ],
        "IAG": [
            {"start_year": 1997, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/International-Airlines-Group-Logo-500x281.jpg"}],
        "Ryanair": [
            {"start_year": 1997, "end_year": 2001, "file": "../99.utility/airline-bar-video/logos/Ryanair-Logo-1987-2001-700x394.png"},
            {"start_year": 2001, "end_year": 2013, "file": "../99.utility/airline-bar-video/logos/Ryanair-Logo-2001-2013-700x394.png"},
            {"start_year": 2013, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Ryanair-Logo-2013-present-700x394.jpg"}
        ],
        "Aeroflot": [
            {"start_year": 1997, "end_year": 2000, "file": "../99.utility/airline-bar-video/logos/Aeroflot-Logo-1997-500x281.png"},
            {"start_year": 2000, "end_year": 2003, "file": "../99.utility/airline-bar-video/logos/Aeroflot-Logo-2000-500x281.png"},
            {"start_year": 2003, "end_year": 2005, "file": "../99.utility/airline-bar-video/logos/Aeroflot-Logo-2003-500x281.png"},
            {"start_year": 2005, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Aeroflot-Logo-500x281.jpg"}
        ],
        "Cathay Pacific": [
            {"start_year": 1997, "end_year": 2014, "file": "../99.utility/airline-bar-video/logos/Cathay-Pacific-Logo-1994-500x281.png"},
            {"start_year": 2014, "end_year": 2023, "file": "../99.utility/airline-bar-video/logos/Cathay-Pacific-Logo-2014-500x281.png"}, 
            {"start_year": 2023, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Cathay-Pacific-Logo-2023-500x281.jpg"}
        ],
        "Qantas Airways": [
            {"start_year": 1997, "end_year": 2007, "file": "../99.utility/airline-bar-video/logos/Qantas-Logo-1984-500x281.png"},
            {"start_year": 2007, "end_year": 2016, "file": "../99.utility/airline-bar-video/logos/Qantas-Logo-2007-500x281.png"}, 
            {"start_year": 2016, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Qantas-Logo-500x281.jpg"}
        ],
        "Finnair": [
            {"start_year": 1997, "end_year": 2000, "file": "../99.utility/airline-bar-video/logos/Finnair-Logo-1968-500x281.png"},
            {"start_year": 2000, "end_year": 2010, "file": "../99.utility/airline-bar-video/logos/Finnair-Logo-2000-500x281.png"},
            {"start_year": 2010, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Finnair-Logo-2010-500x281.jpg"}
        ],
        "Alaska Air": [
            {"start_year": 1972, "end_year": 2014, "file": "../99.utility/airline-bar-video/logos/Alaska-Airlines-Logo-1990-2014-700x394.png"},
            {"start_year": 2014, "end_year": 2016, "file": "../99.utility/airline-bar-video/logos/Alaska-Airlines-Logo-2014-2016-700x394.png"},
            {"start_year": 2016, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Alaska-Airlines-Logo-2016-present-700x394.jpg"}
        ],
        "Norwegian": [
            {"start_year": 1997, "end_year": 9999, "file": "../99.utility/airline-bar-video/logos/Norwegian-Logo-New-500x281.png"}]
    }
    
    # Handle Norwegian special case
    if iata_code == "DY":
        norwegian_logo = "../99.utility/airline-bar-video/logos/Norwegian-Logo-New-500x281.png"
        return norwegian_logo if os.path.exists(norwegian_logo) else None
        
    if airline not in logo_mapping:
        print(f"Company {airline} not found in logo mapping keys")
        return None
        
    logo_versions = logo_mapping[airline]
    
    # Handle Air France-KLM special case
    if airline == "Air France-KLM":
        if year < 2004 or (year == 2004 and month < 5):
            # Use KLM logo before May 2004
            for version in logo_versions:
                if version["iata"] == "KL":
                    logo_path = version["file"]
                    return logo_path if os.path.exists(logo_path) else None
        else:
            # Use Air France-KLM logo after May 2004
            for version in logo_versions:
                if version["iata"] == "AF":
                    logo_path = version["file"]
                    return logo_path if os.path.exists(logo_path) else None
    
    # Standard processing
    for version in logo_versions:
        if version["start_year"] <= year <= version["end_year"]:
            logo_path = version["file"]
            if os.path.exists(logo_path):
                return logo_path
            else:
                print(f"Logo file not found: {logo_path} in {year} {month}")
                return None
    
    return None

def parse_quarter(quarter_str):
    """Parse quarter string into (year, quarter)"""
    year, quarter = quarter_str.split("'")
    year = int(year)  # Year is already in 4-digit format
    quarter = int(quarter[1])  # Extract quarter number
    return year, quarter

def format_revenue(value):
    """Format revenue values with B for billions and M for millions"""
    if value >= 1000:
        return f'${value/1000:.1f}B'
    return f'${value:.0f}M'

def interpolate_quarterly_data(revenue_data):
    """
    Detect if quarterly data within the same year is identical, and perform interpolation if so.
    This allows data to smoothly transition from previous year Q4 to current year Q4.
    """
    # Get all quarters
    quarters = revenue_data.index.tolist()
    
    # Group by year
    years_data = {}
    for quarter in quarters:
        year, q = parse_quarter(quarter)
        if year not in years_data:
            years_data[year] = []
        years_data[year].append((quarter, q))
    
    # Sort quarters within each year
    for year in years_data:
        years_data[year].sort(key=lambda x: x[1])
    
    # Detect years that need interpolation
    interpolated_data = revenue_data.copy()
    interpolation_count = 0
    
    for year in sorted(years_data.keys()):
        quarters_in_year = years_data[year]
        
        # Check if there are complete 4 quarters
        if len(quarters_in_year) == 4:
            # Check if all 4 quarters have identical data
            q1_data = interpolated_data.loc[quarters_in_year[0][0]]
            q2_data = interpolated_data.loc[quarters_in_year[1][0]]
            q3_data = interpolated_data.loc[quarters_in_year[2][0]]
            q4_data = interpolated_data.loc[quarters_in_year[3][0]]
            
            # Check if all airlines have identical data across quarters
            all_same = True
            for airline in interpolated_data.columns:
                if not (q1_data[airline] == q2_data[airline] == q3_data[airline] == q4_data[airline]):
                    all_same = False
                    break
            
            if all_same:
                # print(f"Detected identical quarterly data for {year}, starting interpolation...")
                interpolation_count += 1
                
                # Get previous year Q4 data (if exists)
                prev_year = year - 1
                prev_q4_quarter = f"{prev_year}'Q4"
                
                if prev_q4_quarter in interpolated_data.index:
                    prev_q4_data = interpolated_data.loc[prev_q4_quarter]
                    
                    # Perform interpolation for each airline
                    for airline in interpolated_data.columns:
                        prev_value = prev_q4_data[airline]
                        current_value = q4_data[airline]
                        
                        # Calculate interpolation
                        q1_interpolated = prev_value + (current_value - prev_value) * 0.25
                        q2_interpolated = prev_value + (current_value - prev_value) * 0.5
                        q3_interpolated = prev_value + (current_value - prev_value) * 0.75
                        
                        # Update data
                        interpolated_data.loc[quarters_in_year[0][0], airline] = q1_interpolated
                        interpolated_data.loc[quarters_in_year[1][0], airline] = q2_interpolated
                        interpolated_data.loc[quarters_in_year[2][0], airline] = q3_interpolated
                        # Keep Q4 original value
                        interpolated_data.loc[quarters_in_year[3][0], airline] = current_value
                    
    return interpolated_data


def get_encoded_image(logo_path, airline_name=None):
    """Load image, trim whitespace, resize to fixed height, and return base64 data URL.

    This ensures logos在可视化中高度一致，宽度按比例缩放。
    """
    # 特别处理Emirates的logo高度
    if airline_name == "Emirates":
        TARGET_HEIGHT_PX = 150  # Emirates特殊高度
    else:
        TARGET_HEIGHT_PX = 40  # 其他航空公司统一高度

    def trim_whitespace(img: Image.Image) -> Image.Image:
        # 将非透明背景/白色边缘裁剪掉
        if img.mode in ("RGBA", "LA"):
            # 依据alpha生成mask做裁剪
            alpha = img.split()[-1]
            bbox = alpha.getbbox()
            if bbox:
                return img.crop(bbox)
            return img
        # 非透明图：用白色背景做差分裁剪
        bg = Image.new(img.mode, img.size, img.getpixel((0, 0)))
        diff = ImageChops.difference(img, bg)
        bbox = diff.getbbox()
        if bbox:
            return img.crop(bbox)
        return img

    try:
        if not logo_path or not os.path.exists(logo_path):
            return None

        img = Image.open(logo_path).convert("RGBA")
        img = trim_whitespace(img)

        # 等比例缩放到固定高度
        w, h = img.size
        if h <= 0:
            return None
        scale = TARGET_HEIGHT_PX / float(h)
        new_w = max(1, int(round(w * scale)))
        img = img.resize((new_w, TARGET_HEIGHT_PX), Image.LANCZOS)
        aspect_ratio = new_w / float(TARGET_HEIGHT_PX)

        # 输出为PNG字节并base64
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        encoded_string = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{encoded_string}", aspect_ratio
    except Exception as e:
        print(f"Error processing image {logo_path}: {e}")
        return None


def create_visualization():
    """Create interactive Plotly visualization for airline revenue data"""
    # Load the data from CSV
    df = pd.read_csv('../99.utility/airline-bar-video/airlines_final.csv')
    
    # Process metadata
    metadata = df.iloc[:7].copy()
    
    # Find EBITDA row to separate revenue data from EBITDA data
    EBITDA_row = None
    for i in range(7, len(df)):
        if str(df.iloc[i, 0]).strip() == 'EBITDA':
            EBITDA_row = i
            break
    
    # Extract only revenue data (from row 7 to EBITDA row)
    if EBITDA_row is not None:
        revenue_data = df.iloc[7:EBITDA_row].copy()
    else:
        revenue_data = df.iloc[7:].copy()
    
    metadata.set_index(metadata.columns[0], inplace=True)

    # print("before\n", revenue_data)
    
    # Convert revenue columns
    for col in revenue_data.columns[1:]:
        revenue_data[col] = pd.to_numeric(revenue_data[col].str.replace(r'[,\s"$ ]', '', regex=True), errors='coerce')
    
    # Remove empty rows from the end (excluding the quarter indicator column)
    # Check from the last row backwards until we find a row with data
    quarter_col = revenue_data.columns[0]  # First column is the quarter indicator
    data_cols = revenue_data.columns[1:]   # All other columns are data columns
    
    # Start from the last row and work backwards
    for i in range(len(revenue_data) - 1, -1, -1):
        # Check if all data columns (excluding quarter column) are NaN or empty
        row_data = revenue_data.iloc[i][data_cols]
        if row_data.isna().all() or (row_data == 0).all():
            # This row has no data, remove it
            revenue_data = revenue_data.drop(revenue_data.index[i])
        else:
            # Found a row with data, stop removing rows
            break
    
    revenue_data.set_index(revenue_data.columns[0], inplace=True)
    revenue_data.fillna(0,inplace=True)
    
    # Apply interpolation processing
    revenue_data = interpolate_quarterly_data(revenue_data)
    
    # Convert quarterly data to annual revenue (rolling 4-quarter sum)
    # This means each quarter shows the sum of current quarter + previous 3 quarters
    annual_revenue_data = revenue_data.copy()
    
    # Calculate rolling 4-quarter sum for each airline
    for airline in revenue_data.columns:
        annual_revenue_data[airline] = revenue_data[airline].rolling(window=4, min_periods=4).sum()
    
    # Remove rows where we don't have 4 quarters of data (i.e., 1997 and early 1998)
    # Keep only rows where all airlines have valid annual data
    annual_revenue_data = annual_revenue_data.dropna()
    
    # print("after\n", annual_revenue_data)
    annual_revenue_data.to_csv("output/revenue_data.csv", index=True)
    quarters = annual_revenue_data.index.tolist()
    
    # Prepare all quarterly data
    all_quarters_data = []
    
    # Process each quarter
    for quarter in tqdm(quarters, desc="Processing data"):
        if quarter is np.nan:
            continue
        
        year, q = parse_quarter(quarter)
        month = q * 3
        
        quarter_data = annual_revenue_data.loc[quarter].dropna()
        top_airlines = quarter_data.sort_values(ascending=False).head(args.max_airlines)
        # print(quarter, quarter_data, top_airlines)
        
        airlines = []
        revenues = []
        colors = []
        hover_texts = []
        logos = []
        logo_aspect_ratios = []
        y_positions = []  # Add numerical y positions
        
        # Create lists for each airline's data
        for i, (airline, revenue) in enumerate(top_airlines.items()):
            if pd.notna(revenue) and revenue > 0:
                region = metadata.loc['Region', airline]
                color = region_colors.get(region, '#808080')
                iata_code = metadata.loc['IATA Code', airline]
                
                # Special handling for Air France-KLM labels
                if airline == "Air France-KLM":
                    if year < 2004 or (year == 2004 and month < 5):
                        label = "KL"  # Use KL before May 2004
                    else:
                        label = iata_code if pd.notna(iata_code) else airline[:3]
                else:
                    label = iata_code if pd.notna(iata_code) else airline[:3]
                
                # Get logo path and encode it
                logo_path = get_logo_path(airline, year, iata_code, month)
                encoded_logo = None
                aspect_ratio = None
                if logo_path:
                    result = get_encoded_image(logo_path, airline)
                    if isinstance(result, tuple):
                        encoded_logo, aspect_ratio = result
                    else:
                        encoded_logo = result
                
                airlines.append(label)
                revenues.append(revenue)
                colors.append(color)
                logos.append(encoded_logo)
                logo_aspect_ratios.append(aspect_ratio)
                y_positions.append(i)  # Use numerical position
                
                hover_text = f"<b>{airline}</b><br>"
                hover_text += f"Revenue: {format_revenue(revenue)}<br>"
                hover_text += f"Region: {region}<br>"
                hover_text += f"IATA Code: {iata_code}"
                hover_texts.append(hover_text)
        
        # Store data (already sorted by revenue due to top_airlines being sorted)
        quarter_info = {
            'quarter': quarter,
            'airlines': airlines,
            'revenues': revenues,
            'colors': colors,
            'hover_texts': hover_texts,
            'formatted_revenues': [format_revenue(rev) for rev in revenues],
            'logos': logos,
            'logo_aspect_ratios': logo_aspect_ratios,
            'y_positions': y_positions  # Add y_positions to the data
        }
        all_quarters_data.append(quarter_info)
    
    # Get initial data
    initial_data = all_quarters_data[0]
    
    # Create initial chart
    fig = go.Figure()
    
    # Add traces - Note: Using numerical y positions
    fig.add_trace(
            go.Bar(
                x=initial_data['revenues'],
                y=initial_data['y_positions'],
                orientation='h',
                marker=dict(color=initial_data['colors'][::-1],
                            line=dict(width=0, color='rgba(0,0,0,0)')),
                hoverinfo='none',
                width=0.8,
                showlegend=False
            )
    )
    
    # Add text layer with transparent bars - Add vertical offset
    fig.add_trace(
            go.Bar(
                x=initial_data['revenues'][::-1],
                y=[y - 0.05 for y in initial_data['y_positions'][::-1]],  # Add small offset for text
                orientation='h',
                marker=dict(color='rgba(0,0,0,0)',
                            line=dict(width=0, color='rgba(0,0,0,0)')),
                text=initial_data['formatted_revenues'][::-1],
                textposition='outside',
                textfont=dict(
                    family='Monda',
                    size=14,
                    color='black'
                ),
                cliponaxis=False,
                textangle=0,
                constraintext='none',
                hoverinfo='none',
                width=0.8,
                showlegend=False
            )
    )
    
    # Add region colors to legend using scatter points
    for region, color in region_colors.items():
        fig.add_trace(
            go.Scatter(
                x=[None],
                y=[None],
                mode='markers',
                marker=dict(size=20, color=color),
                name=region,
                showlegend=True
            )
        )

    # Add logos with consistent size and proper alignment
    max_revenue = annual_revenue_data.max().max()
    global_x_offset = max_revenue * 1.05
    fixed_logo_width = max_revenue * 0.2
    
    for i, (airline, revenue, logo, aspect_ratio) in enumerate(zip(initial_data['airlines'], initial_data['revenues'], initial_data['logos'], initial_data['logo_aspect_ratios'])):
        if logo:
            # Calculate dynamic sizey based on airline
            if airline == "EK":  # Emirates IATA code
                logo_sizey = 1.2  # Larger for Emirates
            else:
                logo_sizey = 0.6  # Smaller for others
                
            fig.add_layout_image(
                dict(
                    source=logo,
                    xref="x",
                    yref="y",
                    x=global_x_offset,
                    y=i - 0.05,  # Add small offset for logo
                    sizex=fixed_logo_width,
                    sizey=logo_sizey,
                    xanchor="left",
                    yanchor="middle",
                    sizing="contain",
                    opacity=0.95
                )
            )

    # Adjust x-axis to accommodate logos
    x_axis_range = [0, max_revenue * 1.5]  # Ensure chart has enough space for logos

    # Update layout with numerical yaxis
    fig.update_layout(
        title={
            'text': "Airline Revenue Visualization",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'family': 'Monda', 'size': 24}
        },
        width=args.width,
        height=args.height,
        xaxis=dict(
            title={
                'text': "Revenue",
                'font': {'family': 'Monda', 'size': 16}
            },
            tickformat="$,.0f",
            range=x_axis_range,
            showgrid=True,
            gridcolor='lightgrey',
            gridwidth=1,
            griddash='dot',
            tickfont={'family': 'Monda', 'size': 14}
        ),
        yaxis=dict(
            title={
                'text': "Airline",
                'font': {'family': 'Monda', 'size': 16}
            },
            tickmode='array',
            tickvals=initial_data['y_positions'],
            ticktext=initial_data['airlines'],
            tickfont={'family': 'Monda', 'size': 14},
            fixedrange=True,
            autorange='reversed'
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode="closest",
        font=dict(family="Monda", size=14),
        margin=dict(l=100, r=150, t=100, b=140),
        showlegend=True,
        legend=dict(
            itemsizing='constant',
            title=dict(text='Regions'),
            tracegroupgap=0,
            orientation="h",
            yanchor="top",
            y=-0.15,
            xanchor="center",
            x=0.5
        ),
        xaxis_range=x_axis_range,
        bargap=0.15,
        bargroupgap=0.1,
        uniformtext=dict(
            mode='hide',
            minsize=14
        )
    )
    
    # Convert to HTML
    html_content = pio.to_html(
        fig,
        include_plotlyjs=False,
        full_html=False,
        div_id='airline-chart'
    )
    
    # Convert data to JSON for JavaScript
    import json
    quarters_data_json = json.dumps(all_quarters_data)
    
    # Create custom HTML with updated JavaScript
    custom_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Airline Revenue Visualization</title>
    <style>
        body {{
            font-family: 'Monda', Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }}
        .control-panel {{
            text-align: center;
            margin-top: 20px;
            margin-bottom: 30px;
        }}
        .quarter-display {{
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .slider-container {{
            width: 80%;
            margin: 0 auto;
            margin-bottom: 15px;
        }}
        .button-container {{
            margin-top: 10px;
        }}
        button {{
            font-family: 'Monda', Arial, sans-serif;
            padding: 8px 20px;
            margin: 0 5px;
            cursor: pointer;
            background-color: #f0f0f0;
            border: 1px solid #ccc;
            border-radius: 4px;
        }}
        button:hover {{
            background-color: #e0e0e0;
        }}
        #quarter-slider {{
            width: 100%;
        }}
    </style>
    <script src="https://cdn.plot.ly/plotly-2.27.1.min.js" defer></script>
</head>
<body>
    {html_content}
    
    <div class="control-panel">
        <div class="quarter-display">
            <span id="current-quarter">{initial_quarter}</span>
        </div>
        <div class="slider-container">
            <input type="range" id="quarter-slider" min="0" max="{max_quarters}" step="1" value="0">
        </div>
        <div class="button-container">
            <button id="play-button">Play</button>
            <button id="pause-button">Pause</button>
            <button id="reset-button">Reset</button>
        </div>
    </div>
    
    <script>
        window.addEventListener('load', async function() {{
            while (!window.Plotly) {{
                await new Promise(resolve => setTimeout(resolve, 100));
            }}

            const allQuartersData = {quarters_data};
            let currentQuarterIndex = 0;
            const animationDuration = {animation_duration};
            let isPlaying = false;
            let playInterval = null;
            
            const chartDiv = document.getElementById('airline-chart');
            const currentQuarterDisplay = document.getElementById('current-quarter');
            const quarterSlider = document.getElementById('quarter-slider');
            const playButton = document.getElementById('play-button');
            const pauseButton = document.getElementById('pause-button');
            const resetButton = document.getElementById('reset-button');
            
            const initialData = allQuartersData[0];
            
            // Create traces array with the bar chart and region legends
            const traces = [
                {{
                    type: 'bar',
                    x: initialData.revenues,
                    y: initialData.y_positions,
                    orientation: 'h',
                    marker: {{
                        color: initialData.colors,
                        line: {{
                            width: 0,
                            color: 'rgba(0,0,0,0)'
                        }}
                    }},
                    hoverinfo: 'none',
                    width: 0.8,
                    showlegend: false
                }},
                {{
                    type: 'bar',
                    x: initialData.revenues,
                    y: initialData.y_positions,
                    orientation: 'h',
                    marker: {{
                        color: 'rgba(0,0,0,0)',
                        line: {{
                            width: 0,
                            color: 'rgba(0,0,0,0)'
                        }}
                    }},
                    text: initialData.formatted_revenues,
                    textposition: 'outside',
                    textfont: {{
                        family: 'Monda',
                        size: 14,
                        color: 'black'
                    }},
                    cliponaxis: false,
                    textangle: 0,
                    constraintext: 'none',
                    hoverinfo: 'none',
                    width: 0.8,
                    showlegend: false
                }}
            ];
            
            const regions = {{
                'North America': '#40E0D0',
                'Europe': '#4169E1',
                'Asia Pacific': '#FF4B4B',
                'Latin America': '#32CD32',
                'China': '#FF4B4B',
                'Middle East': '#DEB887',
                'Russia': '#FF4B4B',
                'Turkey': '#DEB887'
            }};
            
            Object.entries(regions).forEach(([region, color]) => {{
                traces.push({{
                    type: 'scatter',
                    x: [NaN],
                    y: [NaN],
                    mode: 'markers',
                    marker: {{
                        size: 20,
                        color: color
                    }},
                    name: region,
                    showlegend: true,
                    hoverinfo: 'skip',
                    visible: 'legendonly'
                }});
            }});
            
            const layout = {{
                title: {{
                    text: "Airline Revenue Visualization",
                    y: 0.95,
                    x: 0.5,
                    xanchor: 'center',
                    yanchor: 'top',
                    font: {{family: 'Monda', size: 24}}
                }},
                width: {width},
                height: {height},
                xaxis: {{
                    title: {{
                        text: "Revenue",
                        font: {{family: 'Monda', size: 16}}
                    }},
                    tickformat: "$,.0f",
                    range: [0, Math.max(...initialData.revenues) * 1.5],
                    showgrid: true,
                    gridcolor: 'lightgrey',
                    gridwidth: 1,
                    griddash: 'dot',
                    tickfont: {{family: 'Monda', size: 14}}
                }},
                yaxis: {{
                    title: {{
                        text: "Airline",
                        font: {{family: 'Monda', size: 16}}
                    }},
                    tickmode: 'array',
                    tickvals: initialData.y_positions,
                    ticktext: initialData.airlines,
                    tickfont: {{family: 'Monda', size: 14}},
                    autorange: 'reversed'
                }},
                plot_bgcolor: 'white',
                paper_bgcolor: 'white',
                hovermode: "closest",
                font: {{family: "Monda", size: 14}},
                margin: {{l: 100, r: 150, t: 100, b: 140}},
                showlegend: true,
                legend: {{
                    itemsizing: 'constant',
                    title: {{text: 'Regions'}},
                    tracegroupgap: 0,
                    orientation: "h",
                    yanchor: "top",
                    y: -0.15,
                    xanchor: "left",
                    x: 0.1
                }},
                images: (() => {{
                    const xAxisMax = Math.max(...initialData.revenues) * 1.5;
                    const baseLogoWidth = xAxisMax * 0.1; // base width proportional to axis range
                    return initialData.logos.map((logo, i) => {{
                        if (!logo) return null;
                        
                        // Calculate dynamic sizey based on airline
                        const logoSizey = initialData.airlines[i] === "EK" ? 1.2 : 0.6;
                        
                        return {{
                            source: logo,
                            xref: "x",
                            yref: "y",
                            x: initialData.revenues[i] + xAxisMax * 0.08,
                            y: i - 0.05,
                            sizex: baseLogoWidth * (initialData.logo_aspect_ratios && initialData.logo_aspect_ratios[i] ? initialData.logo_aspect_ratios[i] : 1.6),
                            sizey: logoSizey,
                            xanchor: "left",
                            yanchor: "middle",
                            sizing: "contain",
                            opacity: 0.95
                        }};
                    }}).filter(img => img !== null)
                }})()
            }};
            
            await Plotly.newPlot(chartDiv, traces, layout);
            
            let historicalMaxRevenue = Math.max(...initialData.revenues);
            
            async function playAnimation() {{
                if (isPlaying) return;
                isPlaying = true;
                
                let lastFrameTime = performance.now();
                const frameDuration = 16;
                const quarterDuration = 5000;
                let currentTime = 0;
                
                function animate() {{
                    if (!isPlaying) return;
                    
                    const now = performance.now();
                    const deltaTime = now - lastFrameTime;
                    lastFrameTime = now;
                    
                    currentTime += deltaTime;
                    const totalDuration = quarterDuration * (allQuartersData.length - 1);
                    const normalizedTime = (currentTime % totalDuration) / totalDuration;
                    
                    const exactIndex = normalizedTime * (allQuartersData.length - 1);
                    const currentIndex = Math.floor(exactIndex);
                    const nextIndex = (currentIndex + 1) % allQuartersData.length;
                    const progress = exactIndex - currentIndex;
                    
                    quarterSlider.value = currentIndex;
                    
                    const currentData = allQuartersData[currentIndex];
                    const nextData = allQuartersData[nextIndex];
                    
                    const interpolatedData = currentData.revenues.map((startVal, i) => ({{
                        airline: currentData.airlines[i],
                        revenue: startVal + (nextData.revenues[i] - startVal) * progress,
                        logo: currentData.logos[i],
                        aspectRatio: currentData.logo_aspect_ratios ? currentData.logo_aspect_ratios[i] : null,
                        color: currentData.colors[i],
                        formattedRevenue: formatRevenue(startVal + (nextData.revenues[i] - startVal) * progress),
                        y_position: i
                    }}));
                    
                    interpolatedData.sort((a, b) => b.revenue - a.revenue);
                    
                    const airlinesSorted = interpolatedData.map(d => d.airline);
                    const revenuesSorted = interpolatedData.map(d => d.revenue);
                    const logosSorted = interpolatedData.map(d => d.logo);
                    const colorsSorted = interpolatedData.map(d => d.color);
                    const formattedRevenuesSorted = interpolatedData.map(d => d.formattedRevenue);
                    const yPositionsSorted = interpolatedData.map((d, i) => i);
                    const aspectRatiosSorted = interpolatedData.map(d => d.aspectRatio);
                    
                    const currentMaxRevenue = Math.max(...revenuesSorted);
                    historicalMaxRevenue = Math.max(historicalMaxRevenue, currentMaxRevenue);
                    const xAxisMax = historicalMaxRevenue * 1.5;
                    
                    try {{
                        const globalXOffset = historicalMaxRevenue * 1.05;
                        const fixedLogoWidth = historicalMaxRevenue * 0.2;
                        
                        Plotly.update(chartDiv, {{
                            'x': [revenuesSorted, revenuesSorted],
                            'y': [yPositionsSorted, yPositionsSorted.map(y => y - 0.05)],  // Add offset for text
                            'marker.color': [colorsSorted, Array(colorsSorted.length).fill('rgba(0,0,0,0)')],
                            'text': [[], formattedRevenuesSorted],
                            'width': [0.8, 0.8]
                        }}, {{
                            'yaxis.ticktext': airlinesSorted,
                            'yaxis.tickvals': yPositionsSorted,
                            'yaxis.autorange': 'reversed',
                            'xaxis.range': [0, xAxisMax],
                            'images': logosSorted.map((logo, i) => {{
                                if (!logo) return null;
                                
                                // Calculate dynamic sizey based on airline
                                const logoSizey = airlinesSorted[i] === "EK" ? 1.2 : 0.6;
                                
                                return {{
                                    source: logo,
                                    xref: "x",
                                    yref: "y",
                                    x: revenuesSorted[i] + xAxisMax * 0.08,
                                    y: i - 0.05,  // Add offset for logo
                                    sizex: ((historicalMaxRevenue * 1.5) * 0.1) * (aspectRatiosSorted && aspectRatiosSorted[i] ? aspectRatiosSorted[i] : 1.6),
                                    sizey: logoSizey,
                                    xanchor: "left",
                                    yanchor: "middle",
                                    sizing: "contain",
                                    opacity: 0.95
                                }};
                            }}).filter(img => img !== null)
                        }});
                        
                        const quarterText = interpolateQuarters(currentData.quarter, nextData.quarter, progress);
                        currentQuarterDisplay.textContent = quarterText;
                        
                    }} catch (e) {{
                        console.error("Animation error:", e);
                    }}
                    
                    requestAnimationFrame(animate);
                }}
                
                requestAnimationFrame(animate);
            }}
            
            function formatRevenue(value) {{
                if (value >= 1000) {{
                    return '$' + (value/1000).toFixed(1) + 'B';
                }}
                return '$' + Math.round(value) + 'M';
            }}
            
            function interpolateQuarters(q1, q2, progress) {{
                const [year1, quarter1] = q1.split("'").map(x => parseInt(x.replace('Q', '')));
                let [year2, quarter2] = q2.split("'").map(x => parseInt(x.replace('Q', '')));
                
                if (year2 < year1) {{
                    year2 = year1;
                }}
                
                const yearDiff = year2 - year1;
                const quarterDiff = quarter2 - quarter1;
                const totalQuarters = yearDiff * 4 + quarterDiff;
                const interpolatedQuarters = quarter1 + totalQuarters * progress;
                
                const interpolatedYear = Math.floor(year1 + (interpolatedQuarters - 1) / 4);
                const interpolatedQuarter = Math.floor(((interpolatedQuarters - 1) % 4) + 1);
                
                return interpolatedYear + "'Q" + interpolatedQuarter;
            }}
            
            function pauseAnimation() {{
                isPlaying = false;
                if (playInterval) {{
                    clearTimeout(playInterval);
                    playInterval = null;
                }}
            }}
            
            async function resetAnimation() {{
                pauseAnimation();
                quarterSlider.value = 0;
                await updateChart(0);
            }}
            
            quarterSlider.addEventListener('input', async function() {{
                pauseAnimation();
                const newIndex = parseInt(this.value);
                if (newIndex !== currentQuarterIndex) {{
                    await updateChart(newIndex);
                }}
            }});
            
            playButton.addEventListener('click', playAnimation);
            pauseButton.addEventListener('click', pauseAnimation);
            resetButton.addEventListener('click', resetAnimation);
            
            setTimeout(playAnimation, 1000);
        }});
    </script>
</body>
</html>
    """.format(
        html_content=html_content,
        initial_quarter=initial_data['quarter'],
        max_quarters=len(quarters) - 1,
        quarters_data=quarters_data_json,
        animation_duration=args.transition_duration,
        width=args.width,
        height=args.height
    )

    
    # Save HTML file
    with open(args.output, 'w') as f:
        f.write(custom_html)
    webbrowser.open('file://' + str(Path(args.output).resolve()), new=2)
    print(f"Visualization saved successfully to {args.output}")
    
    return fig

if __name__ == "__main__":
    print("Starting Plotly Airline Revenue Visualization")
    fig = create_visualization()
    print("Visualization complete!") 