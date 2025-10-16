import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import warnings
warnings.filterwarnings('ignore')

# Set page configuration
st.set_page_config(
    page_title="BOM Explosion",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 BOM Explosion")
st.markdown("Bill of Materials - Production Planning")

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
        
        return df

    except Exception as e:
        st.error(f"Error loading batch data: {str(e)}")
        return pd.DataFrame()

# Load data
subrecipe_df = load_subrecipe_data()
batch_df = load_batch_data()

if subrecipe_df.empty:
    st.error("Unable to load subrecipe data. Please check your Google Sheets connection.")
    st.stop()

# Get subrecipe options from column A
subrecipe_options = []
if len(subrecipe_df.columns) > 0:
    # Get the first column (A) and remove empty values
    col_a_data = subrecipe_df.iloc[:, 0].dropna()
    subrecipe_options = [item for item in col_a_data if str(item).strip()]

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
    # Find the row for selected recipe
    recipe_row = subrecipe_df[subrecipe_df.iloc[:, 0] == selected_recipe]
    
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
        
        # Get Batch Output from sheet index 4, column C
        batch_output = 0
        if not batch_df.empty:
            # Find matching recipe in batch data
            batch_row = batch_df[batch_df.iloc[:, 0] == selected_recipe]  # Assuming recipe name is in column A of batch sheet
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
        st.markdown("---")
        st.subheader("📊 Batch Analytics")
        
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
        
        # Debug information
        if st.checkbox("Show Debug Info"):
            st.markdown("---")
            st.subheader("Debug Information")
            
            st.write(f"**Selected Recipe:** {selected_recipe}")
            st.write(f"**Batch Input:** {batch_input}")
            
            st.write("**Subrecipe Data Shape:**", subrecipe_df.shape)
            st.write("**Batch Data Shape:**", batch_df.shape)
            
            if not recipe_row.empty:
                st.write("**Recipe Row Data:**")
                st.dataframe(recipe_row)
            
            if not batch_df.empty:
                st.write("**Batch Data Sample:**")
                st.dataframe(batch_df.head())
            
            st.write("**Available Subrecipes:**")
            st.write(subrecipe_options[:10])  # Show first 10 options
    
    else:
        st.error(f"Recipe '{selected_recipe}' not found in the data")

else:
    st.info("Please select a subrecipe to see the analytics")

# Refresh button
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()
