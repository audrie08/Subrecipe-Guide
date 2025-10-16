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
        max-width: 1400px;
        padding-left: 5rem;
        padding-right: 5rem;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #fbbf24 0%, #fcd34d 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
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
        border-radius: 16px;
        border: 1px solid #e8e8e8;
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
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
    }
    
    .stSelectbox > div > div:focus-within, .stNumberInput > div > div:focus-within {
        border-color: #fbbf24 !important;
        box-shadow: 0 0 0 3px rgba(251, 191, 36, 0.1) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #fbbf24 0%, #fcd34d 100%) !important;
        color: #2d2d2d !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(251, 191, 36, 0.4) !important;
    }
    
    /* Subheader styling */
    h3 {
        color: #2d2d2d;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="main-header">
        <h1>Commissary Subrecipe Guide</h1>
    </div>
    """, unsafe_allow_html=True)

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
@st.cache_data(ttl=60)
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
@st.cache_data(ttl=60)
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
@st.cache_data(ttl=60)
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

# Load data
subrecipe_df = load_subrecipe_data()
batch_df = load_batch_data()
ingredients_df = load_ingredients_data()

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
        key="recipe_selector"
    )

with col2:
    st.write("**Batch Input:**")
    batch_input = st.number_input(
        "Batch quantity",
        min_value=1,
        max_value=1000,
        value=1,
        step=1,
        key="batch_input"
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
                    
                    # Only add if qty_conversion is not 0
                    if qty_conversion != 0:
                        ingredients_display.append({
                            "Ingredient": ingredient_name,
                            "Qty per Batch (KG)": f"{qty_conversion:.3f}",
                            "Total Qty (KG)": f"{total_qty:.3f}",
                            "UOM": "KG"
                        })
                
                if ingredients_display:
                    # Convert to DataFrame
                    df_display = pd.DataFrame(ingredients_display)
                    
                    # Add CSS styling first
                    st.markdown("""
                    <style>
                    .ingredients-table-container {
                        border-radius: 12px;
                        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
                        margin: 20px 0;
                        overflow: hidden;
                    }
                    .ingredients-table {
                        width: 100%;
                        border-collapse: collapse;
                        font-size: 14px;
                        background: white;
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                        margin: 0;
                    }
                    .ingredients-table thead {
                        background: linear-gradient(135deg, #1f2937 0%, #374151 100%);
                    }
                    .ingredients-table th {
                        color: #ffffff;
                        font-weight: 600;
                        padding: 1rem;
                        text-align: left;
                        border: none;
                        font-size: 0.9rem;
                        text-transform: uppercase;
                        letter-spacing: 0.5px;
                    }
                    .ingredients-table td {
                        padding: 1rem;
                        color: #4a4a4a;
                        border-top: 1px solid #e8e8e8;
                        vertical-align: middle;
                        text-align: left;
                    }
                    .ingredients-table tbody tr {
                        background: white;
                        transition: background 0.2s ease;
                    }
                    .ingredients-table tbody tr:nth-child(even) {
                        background: #fafafa;
                    }
                    .ingredients-table tbody tr:hover {
                        background: #fff9e6;
                    }
                    .ingredients-table tr:last-child td {
                        border-bottom: none;
                    }
                    /* Bold the Ingredient and Total Qty columns */
                    .ingredients-table td:nth-child(1),
                    .ingredients-table td:nth-child(3) {
                        font-weight: 700;
                    }
                    .total-weight-box {
                        background: linear-gradient(135deg, #2d2d2d 0%, #4a4a4a 100%);
                        color: white;
                        padding: 0.8rem 1.5rem;
                        border-radius: 8px;
                        display: inline-block;
                        margin-top: 1rem;
                    }
                    .total-weight-box .weight-label {
                        font-weight: 700;
                        color: #fbbf24;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    
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
                                <span class="weight-label">Total Volume:</span> {total_weight:.3f} KG
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

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #6a6a6a; font-size: 0.9rem; padding: 2rem 0 1rem 0;">
        Subrecipe Guide 2025
    </div>
    """, unsafe_allow_html=True)
