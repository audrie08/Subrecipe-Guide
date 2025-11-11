import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="Subrecipe Guide",
    layout="wide"
)

# Custom CSS with modern UI design
st.markdown("""
    <style>
    /* Container styling */
    .block-container {
        max-width: 1450px;
        padding-left: 5rem;
        padding-right: 5rem;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #fbbf24 0%, #fcd34d 100%);
        padding: 2rem 2.5rem;
        border-radius: 25px;
        border-bottom: 3px solid #f59e0b;
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        color: #2d2d2d;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .main-header p {
        color: #5a5a5a;
        font-size: 0.95rem;
        margin: 0;
    }
    
    /* Metric cards styling */
    div[data-testid="stMetric"] {
        background: white;
        padding: 1.8rem 1.5rem;
        border-radius: 23px;
        border: 2px solid #374151;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        position: relative;
        overflow: hidden;
    }
    
    div[data-testid="stMetric"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background: linear-gradient(90deg, #1f2937 0%, #374151 100%);
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(31, 41, 55, 0.15);
        border-color: #374151;
        transition: all 0.3s ease;
    }
    
    div[data-testid="stMetric"] label {
        font-size: 0.8rem !important;
        color: #6a6a6a !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #2d2d2d !important;
    }
    
    /* Input styling */
    .stSelectbox > div > div, .stNumberInput > div > div > input {
        border: 2px solid #e0e0e0 !important;
        border-radius: 17px !important;
        transition: all 0.3s ease !important;
    }
    
    .stSelectbox > div > div:focus-within, .stNumberInput > div > div:focus-within {
        border-color: #fbbf24 !important;
        box-shadow: 0 0 0 3px rgba(251, 191, 36, 0.1) !important;
    }
    
    css/* Button styling - MORE SPECIFIC */
    div.stButton > button,
    button[kind="primary"],
    button[kind="secondary"] {
        background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%) !important;
        color: #2d2d2d !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 25px !important;
        font-weight: 900 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(245, 158, 11, 0.5) !important;
        background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0px);
    }

    /* Subheader styling */
    h3 {
        color: #2d2d2d;
        font-weight: 600;
    }
    
    /* Table styling */
    .ingredients-table-container, .wps-table-container {
        border-radius: 15px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        margin: 20px 0;
        overflow: hidden;
    }
    
    .ingredients-table, .wps-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
        background: white;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
        margin: 0;
    }
    
    .ingredients-table thead, .wps-table thead {
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
    }
    
    .ingredients-table th, .wps-table th {
        color: #ffffff;
        font-weight: 600;
        padding: 1rem;
        text-align: left;
        border: none;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .wps-table th {
        padding: 0.75rem 0.5rem;
        font-size: 0.85rem;
    }
    
    .ingredients-table td, .wps-table td {
        padding: 1rem;
        color: #4a4a4a;
        border-top: 1px solid #e8e8e8;
        vertical-align: middle;
        text-align: left;
    }
    
    .wps-table td {
        padding: 0.75rem 0.5rem;
        font-size: 0.85rem;
    }
    
    .ingredients-table tbody tr, .wps-table tbody tr {
        background: white;
        transition: background 0.2s ease;
    }
    
    .ingredients-table tbody tr:nth-child(even), .wps-table tbody tr:nth-child(even) {
        background: #fafafa;
    }
    
    .ingredients-table tbody tr:hover, .wps-table tbody tr:hover {
        background: #fff9e6;
    }
    
    .ingredients-table tr:last-child td, .wps-table tr:last-child td {
        border-bottom: none;
    }
    
    .ingredients-table td:nth-child(1),
    .ingredients-table td:nth-child(3) {
        font-weight: 700;
    }
    
    .wps-table td:first-child {
        font-weight: 700;
    }
    
    .total-weight-box {
        background: linear-gradient(135deg, #2d2d2d 0%, #4a4a4a 100%);
        color: white;
        padding: 1.2rem 1.5rem;
        border-radius: 15px;
        display: block;
        margin-top: 1rem;
        transition: all 0.3s ease;
        width: 100%:
    }
    
    .total-weight-box:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(31, 41, 55, 0.3);
        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
    }
    
    .total-weight-box .weight-label {
        font-weight: 700;
        color: #fbbf24;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="main-header">
        <h1>Commissary Subrecipe Guide</h1>
    </div>
    """, unsafe_allow_html=True)

# Navigation buttons under header
col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 1])

with col_nav1:
    if st.button("Subrecipe Guide", use_container_width=True, key="nav_subrecipe"):
        st.session_state.page = "subrecipe"

with col_nav2:
    if st.button("Weekly Inventory", use_container_width=True, key="nav_wps"):
        st.session_state.page = "Weekly Inventory"

with col_nav3:
    if st.button("Daily Inventory", use_container_width=True, key="nav_daily"):
        st.session_state.page = "daily_inventory"

# Initialize page state
if 'page' not in st.session_state:
    st.session_state.page = "subrecipe"

# --- CREDENTIALS HANDLING ---
@st.cache_resource
def load_credentials():
    """Load Google credentials from Streamlit secrets"""
    try:
        if "google_credentials2" not in st.secrets:
            st.error("Google credentials not found in secrets")
            return None

        credentials_dict = {
            "type": st.secrets["google_credentials2"]["type"],
            "project_id": st.secrets["google_credentials2"]["project_id"],
            "private_key_id": st.secrets["google_credentials2"]["private_key_id"],
            "private_key": st.secrets["google_credentials2"]["private_key"].replace('\\n', '\n'),
            "client_email": st.secrets["google_credentials2"]["client_email"],
            "client_id": st.secrets["google_credentials2"]["client_id"],
            "auth_uri": st.secrets["google_credentials2"]["auth_uri"],
            "token_uri": st.secrets["google_credentials2"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["google_credentials2"]["auth_provider_x509_cert_url"],
            "client_x509_cert_url": st.secrets["google_credentials2"]["client_x509_cert_url"]
        }

        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        credentials = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
        return credentials

    except Exception as e:
        st.error(f"Error loading credentials: {str(e)}")
        return None

# --- LOAD SUBRECIPE OPTIONS ---
@st.cache_data(ttl=300)
def load_subrecipe_data():
    """Load subrecipe data from sheet index 1"""
    credentials = load_credentials()
    if not credentials:
        return pd.DataFrame()

    try:
        gc = gspread.authorize(credentials)
        spreadsheet_id = "1K7PTd9Y3X5j-5N_knPyZm8yxDEgxXFkVZOwnfQf98hQ"
        sh = gc.open_by_key(spreadsheet_id)

        # Get sheet index 1 (second sheet)
        worksheet = sh.get_worksheet(1)
        data = worksheet.get_all_values()
        
        if len(data) < 2:
            st.warning("Not enough data in sheet index 1")
            return pd.DataFrame()

        # Create DataFrame with headers from first row
        df = pd.DataFrame(data[1:], columns=data[0])
        
        # Clean the data
        df = df.replace('', pd.NA)
        
        # Add normalized column for case-insensitive matching
        if len(df.columns) > 0:
            df['_normalized_name'] = df.iloc[:, 0].str.strip().str.lower()
        
        return df

    except Exception as e:
        st.error(f"Error loading subrecipe data: {str(e)}")
        return pd.DataFrame()

# --- LOAD BATCH DATA ---
@st.cache_data(ttl=300)
def load_batch_data():
    """Load batch data from sheet index 4"""
    credentials = load_credentials()
    if not credentials:
        return pd.DataFrame()

    try:
        gc = gspread.authorize(credentials)
        spreadsheet_id = "1K7PTd9Y3X5j-5N_knPyZm8yxDEgxXFkVZOwnfQf98hQ"
        sh = gc.open_by_key(spreadsheet_id)

        # Get sheet index 4 (fifth sheet)
        worksheet = sh.get_worksheet(4)
        data = worksheet.get_all_values()
        
        if len(data) < 2:
            st.warning("Not enough data in sheet index 4")
            return pd.DataFrame()

        # Create DataFrame with headers from first row
        df = pd.DataFrame(data[1:], columns=data[0])
        
        # Clean the data
        df = df.replace('', pd.NA)
        
        # Add normalized column for case-insensitive matching
        if len(df.columns) > 0:
            df['_normalized_name'] = df.iloc[:, 0].str.strip().str.lower()
        
        return df

    except Exception as e:
        st.error(f"Error loading batch data: {str(e)}")
        return pd.DataFrame()

# --- LOAD INGREDIENTS DATA ---
@st.cache_data(ttl=300)
def load_ingredients_data():
    """Load ingredients data from sheet index 4 (5th sheet)"""
    credentials = load_credentials()
    if not credentials:
        return pd.DataFrame()

    try:
        gc = gspread.authorize(credentials)
        spreadsheet_id = "1K7PTd9Y3X5j-5N_knPyZm8yxDEgxXFkVZOwnfQf98hQ"
        sh = gc.open_by_key(spreadsheet_id)

        # Get sheet index 4 (fifth sheet)
        worksheet = sh.get_worksheet(4)
        data = worksheet.get_all_values()
        
        if len(data) < 2:
            st.warning("Not enough data in sheet index 4 for ingredients")
            return pd.DataFrame()

        # Create DataFrame with headers from first row
        df = pd.DataFrame(data[1:], columns=data[0])
        
        # Clean the data
        df = df.replace('', pd.NA)
        
        # Add normalized column for case-insensitive matching
        if len(df.columns) > 0:
            df['_normalized_subrecipe'] = df.iloc[:, 0].str.strip().str.lower()
            df['_normalized_ingredient'] = df.iloc[:, 1].str.strip().str.lower()
        
        return df

    except Exception as e:
        st.error(f"Error loading ingredients data: {str(e)}")
        return pd.DataFrame()

# --- LOAD WPS DATA ---
@st.cache_data(ttl=300)
def load_wps_data():
    """Load WPS data from sheet index 5 (6th sheet)"""
    credentials = load_credentials()
    if not credentials:
        return pd.DataFrame()

    try:
        gc = gspread.authorize(credentials)
        spreadsheet_id = "1K7PTd9Y3X5j-5N_knPyZm8yxDEgxXFkVZOwnfQf98hQ"
        sh = gc.open_by_key(spreadsheet_id)

        # Get sheet index 5 (6th sheet)
        worksheet = sh.get_worksheet(5)
        data = worksheet.get_all_values()
        
        if len(data) < 11:
            st.warning("Not enough data in sheet index 5")
            return pd.DataFrame()

        # Header starts at row 10 (index 9), data starts at row 11 (index 10)
        headers = data[9]
        data_rows = data[10:]
        
        # Handle duplicate column names by adding suffixes
        seen = {}
        unique_headers = []
        for header in headers:
            if header == '' or header in seen:
                # For empty or duplicate headers, create unique names
                count = seen.get(header, 0)
                seen[header] = count + 1
                if header == '':
                    unique_headers.append(f'Column_{len(unique_headers)}')
                else:
                    unique_headers.append(f'{header}_{count}')
            else:
                unique_headers.append(header)
                seen[header] = 1
        
        # Create DataFrame with unique headers
        df = pd.DataFrame(data_rows, columns=unique_headers)
        
        # Clean the data
        df = df.replace('', pd.NA)
        
        return df

    except Exception as e:
        st.error(f"Error loading WPS data: {str(e)}")
        return pd.DataFrame()

# --- LOAD BEGINNING INVENTORY DATA ---
@st.cache_data(ttl=300)
def load_beginning_inventory_data():
    """Load beginning inventory data from sheet index 6 (7th sheet)"""
    credentials = load_credentials()
    if not credentials:
        return pd.DataFrame()

    try:
        gc = gspread.authorize(credentials)
        spreadsheet_id = "1K7PTd9Y3X5j-5N_knPyZm8yxDEgxXFkVZOwnfQf98hQ"
        sh = gc.open_by_key(spreadsheet_id)

        # Get sheet index 6 (7th sheet)
        worksheet = sh.get_worksheet(6)
        data = worksheet.get_all_values()
        
        if len(data) < 3:
            st.warning("Not enough data in sheet index 6 for beginning inventory")
            return pd.DataFrame()

        # Header is at row 2 (index 1), data starts at row 3 (index 2)
        headers = data[1]
        data_rows = data[2:182]  # Rows 3 to 182 (indices 2 to 181)
        
        # Create DataFrame
        df = pd.DataFrame(data_rows, columns=headers)
        
        # Clean the data
        df = df.replace('', pd.NA)
        
        # Add normalized column for ingredient names (Column C, index 2) for matching with recipes
        if len(df.columns) > 2:
            df['_normalized_raw_material'] = df.iloc[:, 2].astype(str).str.strip().str.lower()
        
        return df

    except Exception as e:
        st.error(f"Error loading beginning inventory data: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def get_beginning_inventory_row1():
    """Get Row 1 data from beginning inventory sheet (the actual first row, not headers)"""
    credentials = load_credentials()
    if not credentials:
        return []

    try:
        gc = gspread.authorize(credentials)
        spreadsheet_id = "1K7PTd9Y3X5j-5N_knPyZm8yxDEgxXFkVZOwnfQf98hQ"
        sh = gc.open_by_key(spreadsheet_id)

        # Get sheet index 6 (7th sheet)
        worksheet = sh.get_worksheet(6)
        data = worksheet.get_all_values()
        
        if len(data) > 0:
            return data[0]  # Return Row 1 (index 0)
        return []

    except Exception as e:
        st.error(f"Error loading Row 1: {str(e)}")
        return []

def load_pack_size_data():
    """Load pack size data from sheet index 9 (10th sheet)"""
    credentials = load_credentials()
    if not credentials:
        return pd.DataFrame()

    try:
        gc = gspread.authorize(credentials)
        spreadsheet_id = "1K7PTd9Y3X5j-5N_knPyZm8yxDEgxXFkVZOwnfQf98hQ"
        sh = gc.open_by_key(spreadsheet_id)

        # Get sheet index 9 (10th sheet)
        worksheet = sh.get_worksheet(7)
        data = worksheet.get_all_values()
        
        if len(data) < 5:
            st.warning("Not enough data in sheet index 9 for pack size")
            return pd.DataFrame()

        # Header is at row 5 (index 4), data starts at row 6 (index 5)
        headers = data[4]
        data_rows = data[5:]
        
        # Create DataFrame
        df = pd.DataFrame(data_rows, columns=headers)
        
        # Clean the data
        df = df.replace('', pd.NA)
        
        # Add normalized column for raw material names (Column A, index 0)
        if len(df.columns) > 0:
            df['_normalized_raw_material'] = df.iloc[:, 0].astype(str).str.strip().str.lower()
        
        return df

    except Exception as e:
        st.error(f"Error loading pack size data: {str(e)}")
        return pd.DataFrame()

# Load data
subrecipe_df = load_subrecipe_data()
batch_df = load_batch_data()
ingredients_df = load_ingredients_data()
wps_df = load_wps_data()
beginning_inventory_df = load_beginning_inventory_data()
beginning_inventory_row1 = get_beginning_inventory_row1()
pack_size_df = load_pack_size_data()

# Page routing
if st.session_state.page == "subrecipe":
    # SUBRECIPE GUIDE PAGE
    if subrecipe_df.empty:
        st.error("Unable to load subrecipe data. Please check your Google Sheets connection.")
        st.stop()

    # Get subrecipe options from column A and deduplicate case-insensitively
    subrecipe_options = []
    if len(subrecipe_df.columns) > 0:
        # Get the first column (A) and remove empty values
        col_a_data = subrecipe_df.iloc[:, 0].dropna()
        
        # Create a dict to track unique normalized names and keep first occurrence
        seen_normalized = {}
        for item in col_a_data:
            item_str = str(item).strip()
            if item_str:
                normalized = item_str.lower()
                if normalized not in seen_normalized:
                    seen_normalized[normalized] = item_str
        
        subrecipe_options = list(seen_normalized.values())

    if not subrecipe_options:
        st.error("No subrecipe options found in column A of sheet index 1")
        st.stop()

    # Controls
    col1, col2 = st.columns([2, 1])

    with col1:
        st.write("**Select Sub-Recipe:**")
        selected_recipe = st.selectbox(
            "Choose a subrecipe",
            options=subrecipe_options,
            key="recipe_selector",
            label_visibility="collapsed"
        )

    with col2:
        st.write("**Batch Input:**")
        batch_input = st.number_input(
            "Batch quantity",
            min_value=1,
            max_value=1000,
            value=1,
            step=1,
            key="batch_input",
            label_visibility="collapsed"
        )

    # Calculate values based on selection
    if selected_recipe:
        # Normalize the selected recipe for matching
        selected_normalized = selected_recipe.strip().lower()
        
        # Find the row for selected recipe (case-insensitive)
        recipe_row = subrecipe_df[subrecipe_df['_normalized_name'] == selected_normalized]
        
        if not recipe_row.empty:
            recipe_data = recipe_row.iloc[0]
            
            # Extract values from specific columns
            try:
                # Pack Size (col G = index 6)
                pack_size = 0
                if len(recipe_data) > 6 and pd.notna(recipe_data.iloc[6]):
                    pack_size = float(recipe_data.iloc[6])
                
                # Shelf Life (col H = index 7)
                shelf_life = 0
                if len(recipe_data) > 7 and pd.notna(recipe_data.iloc[7]):
                    shelf_life = int(float(recipe_data.iloc[7]))
                
                # Storage Condition (col I = index 8)
                storage_condition = "Not specified"
                if len(recipe_data) > 8 and pd.notna(recipe_data.iloc[8]):
                    storage_condition = str(recipe_data.iloc[8])
                
            except (ValueError, IndexError) as e:
                st.warning(f"Error parsing recipe data: {e}")
                pack_size = 0
                shelf_life = 0
                storage_condition = "Not specified"
            
            # Get Batch Output from sheet index 4, column C (case-insensitive match)
            batch_output = 0
            if not batch_df.empty:
                # Find matching recipe in batch data using normalized names
                batch_row = batch_df[batch_df['_normalized_name'] == selected_normalized]
                if not batch_row.empty and len(batch_row.iloc[0]) > 2:
                    try:
                        batch_output = float(batch_row.iloc[0].iloc[2])  # Column C = index 2
                    except (ValueError, IndexError):
                        batch_output = 0
            
            # Calculate derived values
            total_expected_output = batch_output * batch_input
            expected_packs = 0
            if pack_size > 0:
                expected_packs = int(total_expected_output / pack_size)
            
            # Display results
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Batch Output (KG)", f"{batch_output:.2f}")
                st.metric("Total Expected Output (KG)", f"{total_expected_output:.2f}")
            
            with col2:
                st.metric("Pack Size (KG)", f"{pack_size:.2f}")
                st.metric("Expected Total No. of Packs", expected_packs)
            
            with col3:
                st.metric("Shelf Life (days)", shelf_life)
                st.metric("Storage Condition", storage_condition)
            
            # Display Ingredients Table
            if not ingredients_df.empty:
                # Filter ingredients for selected recipe (case-insensitive)
                recipe_ingredients = ingredients_df[ingredients_df['_normalized_subrecipe'] == selected_normalized].copy()
                
                if not recipe_ingredients.empty:
                    # Remove duplicates based on subrecipe + ingredient combination
                    recipe_ingredients = recipe_ingredients.drop_duplicates(
                        subset=['_normalized_subrecipe', '_normalized_ingredient'],
                        keep='first'
                    )
                    
                    # Prepare display data
                    ingredients_display = []
                    for idx, row in recipe_ingredients.iterrows():
                        ingredient_name = row.iloc[1] if pd.notna(row.iloc[1]) else "N/A"  # Column B
                        qty_conversion = 0
                        
                        # Get quantity conversion from Column D (index 3)
                        if len(row) > 3 and pd.notna(row.iloc[3]):
                            try:
                                qty_conversion = float(row.iloc[3])
                            except (ValueError, TypeError):
                                qty_conversion = 0
                        
                        # Calculate total quantity (multiply by batch input)
                        total_qty = qty_conversion * batch_input
                        
                        # Find pack size for this ingredient
                        pack_size_value = ""
                        if not pack_size_df.empty:
                            # Normalize the ingredient name for matching
                            name_normalized = ingredient_name.strip().lower()
                            
                            # Find matching row in pack size data
                            pack_row = pack_size_df[
                                pack_size_df['_normalized_raw_material'] == name_normalized
                            ]
                            
                            if not pack_row.empty:
                                # Get value from column B (index 1)
                                if len(pack_row.iloc[0]) > 1:
                                    pack_value = pack_row.iloc[0].iloc[1]
                                    if pd.notna(pack_value) and pack_value != '':
                                        pack_size_value = str(pack_value)
                        
                        # Only add if qty_conversion is not 0
                        if qty_conversion != 0:
                            ingredients_display.append({
                                "Ingredient": ingredient_name,
                                "Pack Size": pack_size_value,
                                "Qty per Batch (KG)": f"{qty_conversion:,.2f}",
                                "Total Qty (KG)": f"{total_qty:,.2f}",
                                "UOM": "KG"
                            })
                    
                    if ingredients_display:
                        # Convert to DataFrame
                        df_display = pd.DataFrame(ingredients_display)
                        
                        # Convert DataFrame to HTML
                        html_table = df_display.to_html(
                            escape=False,
                            index=False,
                            classes='ingredients-table',
                            table_id='ingredients-table'
                        )
                        
                        # Wrap table in container
                        table_html = f"""
                        <div class="ingredients-table-container">
                            {html_table}
                        </div>
                        """
                        
                        st.markdown(table_html, unsafe_allow_html=True)
                        
                        # Calculate total weight and display in two columns
                        total_weight = sum([float(item["Total Qty (KG)"]) for item in ingredients_display])
                        
                        col_left, col_right = st.columns([3, 1])
                        
                        with col_right:
                            st.markdown(f"""
                                <div class="total-weight-box">
                                    <span class="weight-label">Total Volume:</span> {total_weight:,.2f} KG
                                </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning("No valid ingredient data found for this recipe")
                else:
                    st.warning(f"No ingredients found for '{selected_recipe}'")
            else:
                st.error("Unable to load ingredients data")
        
        else:
            st.error(f"Recipe '{selected_recipe}' not found in the data")

    else:
        st.info("Please select a subrecipe to see the analytics")

elif st.session_state.page == "Weekly Inventory":
    # WPS PAGE
    if wps_df.empty:
        st.error("Unable to load WPS data. Please check your Google Sheets connection.")
    else:
        if len(wps_df.columns) > 21:
            # Get the actual headers
            credentials = load_credentials()
            if credentials:
                try:
                    gc = gspread.authorize(credentials)
                    spreadsheet_id = "1K7PTd9Y3X5j-5N_knPyZm8yxDEgxXFkVZOwnfQf98hQ"
                    sh = gc.open_by_key(spreadsheet_id)
                    worksheet = sh.get_worksheet(5)
                    header_row = worksheet.get_all_values()[9]
                    batch_headers = [header_row[i] if i < len(header_row) else f'Batch {i-14}' for i in range(15, 22)]
                except:
                    batch_headers = [f'Batch {i}' for i in range(1, 8)]
            else:
                batch_headers = [f'Batch {i}' for i in range(1, 8)]
            
            # Select columns A and P-V
            display_df = wps_df.iloc[:, [0] + list(range(15, 22))].copy()
            column_names = ['Subrecipe'] + batch_headers
            display_df.columns = column_names
            
            # Remove empty rows
            display_df = display_df[display_df.iloc[:, 0].notna()]
            display_df = display_df[display_df.iloc[:, 0] != '']
            
            # Normalize and filter
            display_df['_normalized'] = display_df['Subrecipe'].str.strip().str.lower()
            
            exclude_terms = [
                'hot kitchen', 'hot kitchen sauce', 'hot kitchen savory', 
                'cold sauce', 'fabrication poultry', 'fabrication meats', 'pastry'
            ]
            
            for term in exclude_terms:
                display_df = display_df[display_df['_normalized'] != term]
            
            # Filter invalid batches
            batch_cols = display_df.columns[1:-1]
            
            def has_valid_batch(row):
                for col in batch_cols:
                    val = str(row[col]).strip()
                    if val and val != '':
                        invalid_values = ['0', '0.0', '.0', '0.00', '.00', '-.0', '-0', '-0.0', '- .0']
                        if val in invalid_values:
                            continue
                        try:
                            num_val = float(val.replace(' ', ''))
                            if num_val > 0:
                                return True
                        except (ValueError, TypeError):
                            return True
                return False
            
            display_df = display_df[display_df.apply(has_valid_batch, axis=1)]
            
            # Calculate total batches per subrecipe
            display_df['Total_Batches'] = 0
            for col in batch_cols:
                display_df['Total_Batches'] += pd.to_numeric(display_df[col], errors='coerce').fillna(0)
            
            display_df = display_df.drop(columns=['_normalized'])
            
            if not display_df.empty:
                # Get all unique types of raw materials for filter
                all_rm_types = set()
                if not ingredients_df.empty:
                    for name in display_df['Subrecipe']:
                        subrecipe_normalized = name.strip().lower()
                        recipe_ingredients = ingredients_df[
                            ingredients_df['_normalized_subrecipe'] == subrecipe_normalized
                        ].copy()
                        
                        if not recipe_ingredients.empty:
                            for _, ing_row in recipe_ingredients.iterrows():
                                # Get type from Column H (index 7) by matching Column G (index 6)
                                if len(ing_row) > 7:
                                    rm_type = ing_row.iloc[7] if pd.notna(ing_row.iloc[7]) else "N/A"
                                    if rm_type != "N/A":
                                        all_rm_types.add(rm_type)
                
                # Add "Frozen Meat" to filter options and sort
                all_rm_types.add("FROZEN MEAT")
                rm_type_options = ["All"] + sorted(list(all_rm_types))
                
                # Add filter dropdown
                st.markdown("### Filter by Type of Raw Material")
                selected_rm_type = st.selectbox("Select Type", options=rm_type_options, key="wps_rm_type_filter")
                
                st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
                
                # Aggregate ingredients maintaining subrecipe order FIRST
                all_ingredients = {}
                ingredient_order = []  # Track order of first appearance
                
                for idx, row in display_df.iterrows():
                    subrecipe_name = row['Subrecipe']
                    total_batches = row['Total_Batches']
                    
                    # Find ingredients for this subrecipe
                    subrecipe_normalized = subrecipe_name.strip().lower()
                    recipe_ingredients = ingredients_df[
                        ingredients_df['_normalized_subrecipe'] == subrecipe_normalized
                    ].copy()
                    
                    if not recipe_ingredients.empty:
                        # Remove duplicates
                        recipe_ingredients = recipe_ingredients.drop_duplicates(
                            subset=['_normalized_subrecipe', '_normalized_ingredient'],
                            keep='first'
                        )
                        
                        for _, ing_row in recipe_ingredients.iterrows():
                            ingredient_name = ing_row.iloc[1] if pd.notna(ing_row.iloc[1]) else "N/A"
                            qty_conversion = 0
                            
                            if len(ing_row) > 3 and pd.notna(ing_row.iloc[3]):
                                try:
                                    qty_conversion = float(ing_row.iloc[3])
                                except (ValueError, TypeError):
                                    qty_conversion = 0
                            
                            if qty_conversion > 0:
                                total_qty = qty_conversion * total_batches
                                
                                if ingredient_name not in all_ingredients:
                                    ingredient_order.append(ingredient_name)
                                    all_ingredients[ingredient_name] = total_qty
                                else:
                                    all_ingredients[ingredient_name] += total_qty
                
                # Calculate totals for display
                total_materials = sum(all_ingredients.values()) if all_ingredients else 0
                
                # Calculate total price
                total_price_sum = 0
                if all_ingredients:
                    for name in ingredient_order:
                        total_qty = all_ingredients[name]
                        
                        # Find price and qty conversion
                        price = 0
                        qty_conv = 1
                        
                        if not ingredients_df.empty:
                            name_normalized = name.strip().lower()
                            price_row = ingredients_df[
                                ingredients_df['_normalized_ingredient'] == name_normalized
                            ]
                            
                            if not price_row.empty:
                                if len(price_row.iloc[0]) > 4:
                                    try:
                                        price_value = price_row.iloc[0].iloc[4]
                                        if pd.notna(price_value) and price_value != '':
                                            price_str = str(price_value).replace('₱', '').replace(',', '').strip()
                                            price = float(price_str)
                                    except (ValueError, TypeError, IndexError):
                                        price = 0
                                
                                if len(price_row.iloc[0]) > 3:
                                    try:
                                        qty_conv_value = price_row.iloc[0].iloc[3]
                                        if pd.notna(qty_conv_value) and qty_conv_value != '':
                                            qty_conv = float(qty_conv_value)
                                            if qty_conv == 0:
                                                qty_conv = 1
                                    except (ValueError, TypeError, IndexError):
                                        qty_conv = 1
                        
                        total_price = (total_qty / qty_conv) * price
                        total_price_sum += total_price
                
                # Create two columns layout with adjusted widths
                col_left, col_right = st.columns([2, 3])
                
                with col_left:
                    st.markdown("### SKU Weekly Batches")
                    
                    # Placeholder for total - will be calculated after filtering
                    total_materials_placeholder = st.empty()
                    
                    # Display batch table (without Total_Batches column)
                    batch_display = display_df.drop(columns=['Total_Batches'])
                    
                    html_table = batch_display.to_html(
                        escape=False,
                        index=False,
                        classes='wps-table',
                        table_id='wps-table'
                    )
                    
                    table_html = f"""
                    <div class="wps-table-container">
                        {html_table}
                    </div>
                    """
                    
                    st.markdown(table_html, unsafe_allow_html=True)
                    st.info(f"Total subrecipes: {len(display_df)}")
                
                with col_right:
                    st.markdown("### Raw Materials")
                    
                    # Placeholder for total price - will be calculated after filtering
                    total_price_placeholder = st.empty()
                    
                    # Display aggregated ingredients in order of appearance with Beginning Inventory
                    if all_ingredients:
                        ingredients_list = []
                        filtered_total_materials = 0
                        filtered_total_price = 0
                        
                        for name in ingredient_order:
                            total_qty = all_ingredients[name]
                            
                            # Get Type and Price from ingredients sheet (index 4)
                            rm_type = "N/A"
                            rm_price = 0
                            qty_conv = 1
                            
                            if not ingredients_df.empty:
                                name_normalized = name.strip().lower()
                                
                                # Match against Column G (index 6) for Type in Column H (index 7)
                                type_row = ingredients_df[
                                    ingredients_df.iloc[:, 6].astype(str).str.strip().str.lower() == name_normalized
                                ]
                                
                                if not type_row.empty and len(type_row.iloc[0]) > 7:
                                    rm_type_value = type_row.iloc[0].iloc[7]
                                    if pd.notna(rm_type_value) and rm_type_value != '':
                                        rm_type = str(rm_type_value)
                                
                                # Match against Column B (index 1) for Price in Column E (index 4) and Qty Conv in Column D (index 3)
                                price_row = ingredients_df[
                                    ingredients_df['_normalized_ingredient'] == name_normalized
                                ]
                                
                                if not price_row.empty:
                                    if len(price_row.iloc[0]) > 4:
                                        try:
                                            price_value = price_row.iloc[0].iloc[4]
                                            if pd.notna(price_value) and price_value != '':
                                                price_str = str(price_value).replace('₱', '').replace(',', '').strip()
                                                rm_price = float(price_str)
                                        except (ValueError, TypeError, IndexError):
                                            rm_price = 0
                                    
                                    if len(price_row.iloc[0]) > 3:
                                        try:
                                            qty_conv_value = price_row.iloc[0].iloc[3]
                                            if pd.notna(qty_conv_value) and qty_conv_value != '':
                                                qty_conv = float(qty_conv_value)
                                                if qty_conv == 0:
                                                    qty_conv = 1
                                        except (ValueError, TypeError, IndexError):
                                            qty_conv = 1
                            
                            # Apply filter
                            if selected_rm_type != "All" and rm_type != selected_rm_type:
                                continue
                            
                            # Add to filtered totals
                            filtered_total_materials += total_qty
                            item_price = (total_qty / qty_conv) * rm_price
                            filtered_total_price += item_price
                            
                            # Find beginning inventory for this ingredient
                            beginning_inv = 0
                            if not beginning_inventory_df.empty:
                                # Normalize the ingredient name for matching
                                name_normalized = name.strip().lower()
                                
                                # Find matching row in beginning inventory
                                inv_row = beginning_inventory_df[
                                    beginning_inventory_df['_normalized_raw_material'] == name_normalized
                                ]
                                
                                if not inv_row.empty:
                                    # Get beginning inventory value from Column A (index 0)
                                    try:
                                        if len(inv_row.iloc[0]) > 0:
                                            inv_value = inv_row.iloc[0].iloc[0]
                                            if pd.notna(inv_value) and inv_value != '':
                                                beginning_inv = float(inv_value)
                                    except (ValueError, TypeError, IndexError):
                                        beginning_inv = 0
                            
                            # Calculate difference
                            difference = total_qty - beginning_inv
                            
                            ingredients_list.append({
                                "Raw Material": name,
                                "Type": rm_type,
                                "Price": f"₱{rm_price:,.2f}",
                                "Total Qty (KG)": f"{total_qty:,.2f}",
                                "Beginning (KG)": f"{beginning_inv:,.2f}",
                                "Difference (KG)": f"<b>{difference:,.2f}</b>"
                            })
                        
                        # Display totals in their respective positions
                        with total_materials_placeholder:
                            st.markdown(f"""
                                <div class="total-weight-box" style="margin-bottom: 1.5rem; margin-top: 0.5rem;">
                                    <span class="weight-label">Total Raw Materials:</span> {filtered_total_materials:,.2f} KG
                                </div>
                            """, unsafe_allow_html=True)
                        
                        with total_price_placeholder:
                            st.markdown(f"""
                                <div class="total-weight-box" style="margin-bottom: 1.5rem; margin-top: 0.5rem;">
                                    <span class="weight-label">Total Price:</span> ₱{filtered_total_price:,.2f}
                                </div>
                            """, unsafe_allow_html=True)
                        
                        if ingredients_list:
                            ingredients_display_df = pd.DataFrame(ingredients_list)
                            
                            html_table = ingredients_display_df.to_html(
                                escape=False,
                                index=False,
                                classes='wps-table',
                                table_id='ingredients-explosion'
                            )
                            
                            table_html = f"""
                            <div class="wps-table-container">
                                {html_table}
                            </div>
                            """
                            
                            st.markdown(table_html, unsafe_allow_html=True)
                        else:
                            st.warning(f"No ingredients found for filter: {selected_rm_type}")
                    else:
                        st.warning("No ingredients data found for selected subrecipes")
            else:
                st.warning("No valid WPS data found after filtering")
        else:
            st.error(f"Not enough columns in WPS data. Found {len(wps_df.columns)} columns, need at least 22.")

elif st.session_state.page == "daily_inventory":
    # DAILY INVENTORY PAGE
    if wps_df.empty:
        st.error("Unable to load WPS data. Please check your Google Sheets connection.")
    else:
        if len(wps_df.columns) > 21:
            # Get the actual headers
            credentials = load_credentials()
            if credentials:
                try:
                    gc = gspread.authorize(credentials)
                    spreadsheet_id = "1K7PTd9Y3X5j-5N_knPyZm8yxDEgxXFkVZOwnfQf98hQ"
                    sh = gc.open_by_key(spreadsheet_id)
                    worksheet = sh.get_worksheet(5)
                    header_row = worksheet.get_all_values()[9]
                    batch_headers = [header_row[i] if i < len(header_row) else f'Batch {i-14}' for i in range(15, 22)]
                except:
                    batch_headers = [f'Batch {i}' for i in range(1, 8)]
            else:
                batch_headers = [f'Batch {i}' for i in range(1, 8)]
            
            # Select columns A and P-V
            display_df = wps_df.iloc[:, [0] + list(range(15, 22))].copy()
            column_names = ['Subrecipe'] + batch_headers
            display_df.columns = column_names
            
            # Remove empty rows
            display_df = display_df[display_df.iloc[:, 0].notna()]
            display_df = display_df[display_df.iloc[:, 0] != '']
            
            # Normalize and filter
            display_df['_normalized'] = display_df['Subrecipe'].str.strip().str.lower()
            
            exclude_terms = [
                'hot kitchen', 'hot kitchen sauce', 'hot kitchen savory', 
                'cold sauce', 'fabrication poultry', 'fabrication meats', 'pastry'
            ]
            
            for term in exclude_terms:
                display_df = display_df[display_df['_normalized'] != term]
            
            # Filter invalid batches
            batch_cols = display_df.columns[1:-1]
            
            def has_valid_batch(row):
                for col in batch_cols:
                    val = str(row[col]).strip()
                    if val and val != '':
                        invalid_values = ['0', '0.0', '.0', '0.00', '.00', '-.0', '-0', '-0.0', '- .0']
                        if val in invalid_values:
                            continue
                        try:
                            num_val = float(val.replace(' ', ''))
                            if num_val > 0:
                                return True
                        except (ValueError, TypeError):
                            return True
                return False
            
            display_df = display_df[display_df.apply(has_valid_batch, axis=1)]
            display_df = display_df.drop(columns=['_normalized'])
            
            if not display_df.empty:
                # Filters in same row
                st.markdown("### Filters")
                filter_col1, filter_col2 = st.columns(2)
                
                with filter_col1:
                    day_options = batch_headers
                    selected_day = st.selectbox("Choose a day", options=day_options, key="day_filter")
                
                with filter_col2:
                    # Get all unique types of raw materials for filter
                    all_rm_types = set()
                    if not ingredients_df.empty:
                        for name in display_df['Subrecipe']:
                            subrecipe_normalized = name.strip().lower()
                            recipe_ingredients = ingredients_df[
                                ingredients_df['_normalized_subrecipe'] == subrecipe_normalized
                            ].copy()
                            
                            if not recipe_ingredients.empty:
                                for _, ing_row in recipe_ingredients.iterrows():
                                    # Get type from Column H (index 7) by matching Column G (index 6)
                                    if len(ing_row) > 7:
                                        rm_type = ing_row.iloc[7] if pd.notna(ing_row.iloc[7]) else "N/A"
                                        if rm_type != "N/A":
                                            all_rm_types.add(rm_type)
                    
                    # Add "Frozen Meat" to filter options and sort
                    all_rm_types.add("Frozen Meat")
                    rm_type_options = ["All"] + sorted(list(all_rm_types))
                    selected_rm_type = st.selectbox("Select Type of RM", options=rm_type_options, key="daily_rm_type_filter")
                
                st.markdown("<div style='margin: 2rem 0;'></div>", unsafe_allow_html=True)
                
                # Get the column index for selected day
                selected_day_index = batch_headers.index(selected_day) + 1  # +1 because column 0 is Subrecipe
                
                # Filter display_df to only show subrecipes with batches on selected day
                filtered_display_df = display_df[
                    pd.to_numeric(display_df.iloc[:, selected_day_index], errors='coerce').fillna(0) > 0
                ].copy()
                
                if not filtered_display_df.empty:
                    # Aggregate ingredients for selected day only
                    all_ingredients = {}
                    ingredient_order = []
                    
                    for idx, row in filtered_display_df.iterrows():
                        subrecipe_name = row['Subrecipe']
                        day_batches = pd.to_numeric(row.iloc[selected_day_index], errors='coerce')
                        if pd.isna(day_batches):
                            day_batches = 0
                        
                        # Find ingredients for this subrecipe
                        subrecipe_normalized = subrecipe_name.strip().lower()
                        recipe_ingredients = ingredients_df[
                            ingredients_df['_normalized_subrecipe'] == subrecipe_normalized
                        ].copy()
                        
                        if not recipe_ingredients.empty:
                            recipe_ingredients = recipe_ingredients.drop_duplicates(
                                subset=['_normalized_subrecipe', '_normalized_ingredient'],
                                keep='first'
                            )
                            
                            for _, ing_row in recipe_ingredients.iterrows():
                                ingredient_name = ing_row.iloc[1] if pd.notna(ing_row.iloc[1]) else "N/A"
                                qty_conversion = 0
                                
                                if len(ing_row) > 3 and pd.notna(ing_row.iloc[3]):
                                    try:
                                        qty_conversion = float(ing_row.iloc[3])
                                    except (ValueError, TypeError):
                                        qty_conversion = 0
                                
                                if qty_conversion > 0:
                                    total_qty = qty_conversion * day_batches
                                    
                                    if ingredient_name not in all_ingredients:
                                        ingredient_order.append(ingredient_name)
                                        all_ingredients[ingredient_name] = total_qty
                                    else:
                                        all_ingredients[ingredient_name] += total_qty
                    
                    # Calculate totals
                    total_materials = sum(all_ingredients.values()) if all_ingredients else 0
                    
                    # Calculate total price
                    total_price_sum = 0
                    if all_ingredients:
                        for name in ingredient_order:
                            total_qty = all_ingredients[name]
                            
                            # Find price and qty conversion
                            price = 0
                            qty_conv = 1
                            
                            if not ingredients_df.empty:
                                name_normalized = name.strip().lower()
                                price_row = ingredients_df[
                                    ingredients_df['_normalized_ingredient'] == name_normalized
                                ]
                                
                                if not price_row.empty:
                                    if len(price_row.iloc[0]) > 4:
                                        try:
                                            price_value = price_row.iloc[0].iloc[4]
                                            if pd.notna(price_value) and price_value != '':
                                                price_str = str(price_value).replace('₱', '').replace(',', '').strip()
                                                price = float(price_str)
                                        except (ValueError, TypeError, IndexError):
                                            price = 0
                                    
                                    if len(price_row.iloc[0]) > 3:
                                        try:
                                            qty_conv_value = price_row.iloc[0].iloc[3]
                                            if pd.notna(qty_conv_value) and qty_conv_value != '':
                                                qty_conv = float(qty_conv_value)
                                                if qty_conv == 0:
                                                    qty_conv = 1
                                        except (ValueError, TypeError, IndexError):
                                            qty_conv = 1
                            
                            total_price = (total_qty / qty_conv) * price
                            total_price_sum += total_price
                    
                    # Create two columns layout
                    col_left, col_right = st.columns([2, 3])
                    
                    with col_left:
                        st.markdown("### SKU Weekly Batches")
                        
                        # Placeholder for total - will be calculated after filtering
                        total_inventory_placeholder = st.empty()
                        
                        # Display batch table for selected day only
                        batch_display = filtered_display_df[['Subrecipe', display_df.columns[selected_day_index]]]
                        batch_display.columns = ['Subrecipe', selected_day]
                        
                        html_table = batch_display.to_html(
                            escape=False,
                            index=False,
                            classes='wps-table',
                            table_id='wps-table-daily'
                        )
                        
                        table_html = f"""
                        <div class="wps-table-container">
                            {html_table}
                        </div>
                        """
                        
                        st.markdown(table_html, unsafe_allow_html=True)
                        st.info(f"Total subrecipes: {len(filtered_display_df)}")
                    
                    with col_right:
                        st.markdown("### Raw Materials")
                        
                        # Placeholder for total price - will be calculated after filtering
                        total_price_placeholder = st.empty()
                        
                        # Display aggregated ingredients
                        if all_ingredients:
                            ingredients_list = []
                            filtered_total_inventory = 0
                            filtered_total_price = 0
                            
                            # Get date from Column B, Row 1 of beginning inventory sheet
                            date_in_col_b = None
                            matched = False
                            
                            if not beginning_inventory_df.empty and credentials:
                                try:
                                    gc = gspread.authorize(credentials)
                                    spreadsheet_id = "1K7PTd9Y3X5j-5N_knPyZm8yxDEgxXFkVZOwnfQf98hQ"
                                    sh = gc.open_by_key(spreadsheet_id)
                                    inv_worksheet = sh.get_worksheet(6)
                                    
                                    # Get only Column B, Row 1
                                    date_in_col_b = inv_worksheet.cell(1, 2).value  # Row 1, Column B (col index 2)
                                    if date_in_col_b:
                                        date_in_col_b = date_in_col_b.strip()
                                except:
                                    pass
                            
                            # Convert selected_day to date format (e.g., "3NOV" -> "Nov 3")
                            try:
                                # Parse the day format (e.g., "3NOV", "4NOV")
                                day_num = ''.join(filter(str.isdigit, selected_day))
                                month_abbr = ''.join(filter(str.isalpha, selected_day))
                                
                                # Convert to "Nov 3" format
                                month_map = {
                                    'JAN': 'Jan', 'FEB': 'Feb', 'MAR': 'Mar', 'APR': 'Apr',
                                    'MAY': 'May', 'JUN': 'Jun', 'JUL': 'Jul', 'AUG': 'Aug',
                                    'SEP': 'Sep', 'OCT': 'Oct', 'NOV': 'Nov', 'DEC': 'Dec'
                                }
                                
                                formatted_date = f"{month_map.get(month_abbr.upper(), month_abbr)} {day_num}"
                                
                                # Check if dates match
                                if date_in_col_b and date_in_col_b == formatted_date:
                                    matched = True
                                    
                            except:
                                pass
                            
                            for name in ingredient_order:
                                # Get Type and Price from ingredients sheet
                                rm_type = "N/A"
                                rm_price = 0
                                qty_conv = 1
                                
                                if not ingredients_df.empty:
                                    name_normalized = name.strip().lower()
                                    
                                    # Match against Column G (index 6) for Type in Column H (index 7)
                                    type_row = ingredients_df[
                                        ingredients_df.iloc[:, 6].astype(str).str.strip().str.lower() == name_normalized
                                    ]
                                    
                                    if not type_row.empty and len(type_row.iloc[0]) > 7:
                                        rm_type_value = type_row.iloc[0].iloc[7]
                                        if pd.notna(rm_type_value) and rm_type_value != '':
                                            rm_type = str(rm_type_value)
                                    
                                    # Match against Column B (index 1) for Price in Column E (index 4) and Qty Conv
                                    price_row = ingredients_df[
                                        ingredients_df['_normalized_ingredient'] == name_normalized
                                    ]
                                    
                                    if not price_row.empty:
                                        if len(price_row.iloc[0]) > 4:
                                            try:
                                                price_value = price_row.iloc[0].iloc[4]
                                                if pd.notna(price_value) and price_value != '':
                                                    price_str = str(price_value).replace('₱', '').replace(',', '').strip()
                                                    rm_price = float(price_str)
                                            except (ValueError, TypeError, IndexError):
                                                rm_price = 0
                                        
                                        if len(price_row.iloc[0]) > 3:
                                            try:
                                                qty_conv_value = price_row.iloc[0].iloc[3]
                                                if pd.notna(qty_conv_value) and qty_conv_value != '':
                                                    qty_conv = float(qty_conv_value)
                                                    if qty_conv == 0:
                                                        qty_conv = 1
                                            except (ValueError, TypeError, IndexError):
                                                qty_conv = 1
                                
                                # Apply filter
                                if selected_rm_type != "All" and rm_type != selected_rm_type:
                                    continue
                                
                                # Find beginning inventory for this ingredient
                                beginning_inv = 0
                                if not beginning_inventory_df.empty and matched:
                                    # Only get beginning inventory if date matched
                                    name_normalized = name.strip().lower()
                                    
                                    inv_row = beginning_inventory_df[
                                        beginning_inventory_df['_normalized_raw_material'] == name_normalized
                                    ]
                                    
                                    if not inv_row.empty:
                                        # Get beginning inventory value from Column B (index 1)
                                        try:
                                            if len(inv_row.iloc[0]) > 1:
                                                inv_value = inv_row.iloc[0].iloc[1]
                                                if pd.notna(inv_value) and inv_value != '':
                                                    beginning_inv = float(inv_value)
                                        except (ValueError, TypeError, IndexError):
                                            beginning_inv = 0
                                
                                # Add to filtered totals
                                filtered_total_inventory += beginning_inv
                                if beginning_inv > 0:
                                    item_price = (beginning_inv / qty_conv) * rm_price
                                    filtered_total_price += item_price
                                
                                ingredients_list.append({
                                    "Raw Material": name,
                                    "Type": rm_type,
                                    "Price": f"₱{rm_price:,.2f}",
                                    "Inventory on Hand (KG)": f"{beginning_inv:,.2f}"
                                })
                            
                            # After loop completes, display filtered totals
                            with total_price_placeholder:
                                st.markdown(f"""
                                    <div class="total-weight-box" style="margin-bottom: 1.5rem; margin-top: 0.5rem;">
                                        <span class="weight-label">Daily Total Price ({selected_day}):</span> ₱{filtered_total_price:,.2f}
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            with total_inventory_placeholder:
                                st.markdown(f"""
                                    <div class="total-weight-box" style="margin-bottom: 1.5rem; margin-top: 0.5rem;">
                                        <span class="weight-label">Daily Total Inventory ({selected_day}):</span> {filtered_total_inventory:,.2f} KG
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            if ingredients_list:
                                ingredients_display_df = pd.DataFrame(ingredients_list)
                                
                                html_table = ingredients_display_df.to_html(
                                    escape=False,
                                    index=False,
                                    classes='wps-table',
                                    table_id='ingredients-explosion-daily'
                                )
                                
                                table_html = f"""
                                <div class="wps-table-container">
                                    {html_table}
                                </div>
                                """
                                
                                st.markdown(table_html, unsafe_allow_html=True)
                            else:
                                st.warning(f"No ingredients found for filter: {selected_rm_type}")
                        else:
                            st.warning("No ingredients data found for selected day")
                else:
                    st.warning(f"No subrecipes scheduled for {selected_day}")
            else:
                st.warning("No valid WPS data found after filtering")
        else:
            st.error(f"Not enough columns in WPS data. Found {len(wps_df.columns)} columns, need at least 22.")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #6a6a6a; font-size: 0.9rem; padding: 2rem 0 1rem 0;">
        Subrecipe Guide 2025
    </div>
    """, unsafe_allow_html=True)
