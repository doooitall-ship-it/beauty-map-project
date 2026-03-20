import streamlit as st
import pandas as pd
import os
import unicodedata
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation
import base64

# --- Layout Configuration ---
st.set_page_config(page_title="Sample Store App", layout="wide", initial_sidebar_state="expanded")

# --- Directory Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
IMG_DIR = os.path.join(BASE_DIR, '..', 'images')

# --- Custom CSS (Apple Minimalism & Glassmorphism) ---
def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
        
        /* Font and App Background */
        html, body, [class*="css"] {
            font-family: 'Pretendard', sans-serif;
            background-color: #f5f5f7;
            color: #1d1d1f;
        }

        /* Sidebar Styling (Glassmorphism) */
        [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.6) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.4);
        }

        /* Main Welcome Card */
        .welcome-card {
            background: rgba(255, 255, 255, 0.65);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.5);
            border-radius: 15px;
            padding: 4rem 3rem;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.05);
            margin: 10vh auto;
            max-width: 700px;
        }

        .welcome-text {
            font-size: 1.6rem;
            font-weight: 500;
            line-height: 1.5;
            color: #1d1d1f;
        }

        /* Common Elements: Buttons, Input */
        div[data-testid="stButton"] button {
            border-radius: 15px !important;
            border: 1px solid rgba(0,0,0,0.1) !important;
            background: rgba(255, 255, 255, 0.8) !important;
            font-weight: 500 !important;
            transition: all 0.2s ease !important;
        }
        
        div[data-testid="stButton"] button:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
        }

        /* Product Card Styles */
        .product-card {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.4);
            border-radius: 15px;
            padding: 1rem;
            margin-bottom: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03);
            transition: transform 0.2s ease;
        }

        .product-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
        }

        .product-img {
            width: 100%;
            aspect-ratio: 1 / 1;
            object-fit: cover;
            border-radius: 15px; /* image card rounded corner 15px */
            margin-bottom: 0.8rem;
        }

        .product-title {
            font-size: 0.95rem;
            font-weight: 600;
            margin: 0.2rem 0;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            color: #1d1d1f;
        }

        .product-price {
            font-size: 0.85rem;
            font-weight: 500;
            color: #86868b;
        }
        
        /* Headers */
        h1, h2, h3 {
            font-weight: 600 !important;
            color: #1d1d1f !important;
        }
        
        /* Sidebar Radio Buttons Left Alignment */
        [data-testid="stSidebar"] [data-baseweb="radio"] {
            justify-content: flex-start !important;
        }
        [data-testid="stSidebar"] .stRadio label {
            width: 100% !important;
            justify-content: flex-start !important;
        }
        [data-testid="stSidebar"] .stRadio label p {
            text-align: left !important;
            width: 100% !important;
        }
        
        /* Custom Geolocation wrapper */
        .geo-container {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }
        .geo-label {
            font-weight: 600;
            color: #1d1d1f;
            margin-left: 10px;
            font-size: 1.1rem;
        }
        
        /* Map Iframe Styling */
        iframe {
            border-radius: 15px !important;
            border: none !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
        }
        
        /* Metric/Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
        }
        .stTabs [data-baseweb="tab"] {
            height: 3rem;
            white-space: pre;
            background-color: transparent !important;
            border-radius: 15px;
            padding: 0px 20px;
        }
        .stTabs [aria-selected="true"] {
            background: rgba(0,0,0,0.05) !important;
            font-weight: 600 !important;
        }
        </style>
    """, unsafe_allow_html=True)

# Helper function to find images
def find_image_path(product_name, brand_folder):
    target_dir = os.path.join(IMG_DIR, brand_folder)
    if not os.path.exists(target_dir):
        return None
        
    product_name_norm = unicodedata.normalize('NFC', str(product_name).strip()).replace(' ', '')
    
    for f in os.listdir(target_dir):
        f_norm = unicodedata.normalize('NFC', f)
        if product_name_norm in f_norm.replace(' ', ''):
            return os.path.join(target_dir, f)
            
    return None

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def render_product_card(product_row, brand_folder):
    name = product_row['상품명']
    price = product_row['가격']
    link = product_row.get('링크', '#')
    
    img_path = find_image_path(name, brand_folder)
    
    if img_path and os.path.exists(img_path):
        img_b64 = get_base64_of_bin_file(img_path)
        img_html = f'<img src="data:image/jpeg;base64,{img_b64}" class="product-img">'
    else:
        # Placeholder if no image
        img_html = f'<div class="product-img" style="background:#e5e5ea; display:flex; align-items:center; justify-content:center; color:#86868b; font-size:0.8rem;">No Image</div>'

    html = f"""
    <a href="{link}" target="_blank" style="text-decoration:none; color:inherit;">
        <div class="product-card">
            {img_html}
            <div class="product-title" title="{name}">{name}</div>
            <div class="product-price">{price:,}원</div>
        </div>
    </a>
    """
    st.markdown(html, unsafe_allow_html=True)

def main():
    inject_custom_css()
    
    # Sidebar Navigation
    menu_options = ["BEST ITEM", "FINDING THE STORE", "TOURIST ATTRACTION"]
    
    with st.sidebar:
        st.markdown("<h3 style='text-align:center; padding:1rem;'>Menu</h3>", unsafe_allow_html=True)
        selected_menu = st.radio("Navigation", ["Home"] + menu_options, label_visibility="collapsed")
        
    # Main Content Area
    if selected_menu == "Home":
        st.markdown("""
            <div class="welcome-card">
                <div class="welcome-text">
                    Hey guys, glad you're here!<br><br>
                    <span style='font-size:1.2rem; color:#86868b;'>Just click on any menu in the left sidebar to get started.</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    elif selected_menu == "BEST ITEM":
        st.markdown("<h2 style='margin-bottom:2rem;'>BEST ITEM</h2>", unsafe_allow_html=True)
        
        tab_oy, tab_daiso = st.tabs(["OLIVE YOUNG", "DAISO"])
        
        # OLIVE YOUNG
        with tab_oy:
            df_oy = pd.read_csv(os.path.join(DATA_DIR, 'oliveyoung_best_10.csv'))
            cols = st.columns(5)
            for idx, row in df_oy.iterrows():
                with cols[idx % 5]:
                    render_product_card(row, 'oliveyoung_best')
                    
        # DAISO
        with tab_daiso:
            df_daiso = pd.read_csv(os.path.join(DATA_DIR, 'daiso_best_10.csv'))
            cols = st.columns(5)
            for idx, row in df_daiso.iterrows():
                with cols[idx % 5]:
                    render_product_card(row, 'daiso_best')

    elif selected_menu == "FINDING THE STORE":
        st.markdown("<h2 style='margin-bottom:1rem;'>FINDING THE STORE</h2>", unsafe_allow_html=True)
        st.markdown("🔴 **다이소(Daiso)** &nbsp;&nbsp;&nbsp; 🟢 **올리브영(Olive Young)**", unsafe_allow_html=True)
        
        # Get location layout with adjacent text
        col1, col2 = st.columns([1, 10])
        with col1:
            location = streamlit_geolocation()
        with col2:
            st.markdown("<div style='margin-top:0.8rem; font-weight:600;'>MY LOCATION</div>", unsafe_allow_html=True)
        
        if location and location.get('latitude') and location.get('longitude'):
            user_lat = location['latitude']
            user_lon = location['longitude']
        else:
            user_lat = 37.5665
            user_lon = 126.9780
            
        m = folium.Map(location=[user_lat, user_lon], zoom_start=14, tiles="CartoDB positron")
        
        # User marker
        folium.Marker(
            [user_lat, user_lon],
            popup="You are here",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)
        
        # Olive Young markers (Green #A6C302)
        try:
            df_oyshop = pd.read_csv(os.path.join(DATA_DIR, 'oliveyoung_shop.csv'))
            for _, row in df_oyshop.iterrows():
                if pd.notna(row['위도']) and pd.notna(row['경도']):
                    popup_html = f"""<div style="white-space: nowrap; font-family: Pretendard, sans-serif;"><b>[올리브영] {row['매장명']}</b><br>주소: {row['주소']}</div>"""
                    folium.CircleMarker(
                        location=[row['위도'], row['경도']],
                        radius=8,
                        popup=folium.Popup(popup_html, max_width=400),
                        color="#A6C302",
                        fill=True,
                        fill_color="#A6C302",
                        fill_opacity=0.9
                    ).add_to(m)
        except Exception as e:
            st.error(f"Error loading olive young shops: {e}")
            
        # Daiso markers (Red #E11937)
        try:
            df_daisoshop = pd.read_csv(os.path.join(DATA_DIR, 'daiso_shop.csv'))
            for _, row in df_daisoshop.iterrows():
                if pd.notna(row['위도']) and pd.notna(row['경도']):
                    popup_html = f"""<div style="white-space: nowrap; font-family: Pretendard, sans-serif;"><b>[다이소] {row['매장명']}</b><br>주소: {row['주소']}</div>"""
                    folium.CircleMarker(
                        location=[row['위도'], row['경도']],
                        radius=8,
                        popup=folium.Popup(popup_html, max_width=400),
                        color="#E11937",
                        fill=True,
                        fill_color="#E11937",
                        fill_opacity=0.9
                    ).add_to(m)
        except Exception as e:
            st.error(f"Error loading daiso shops: {e}")
            
        st_folium(m, center=[user_lat, user_lon], zoom=14, width=800, height=500, returned_objects=[])

    elif selected_menu == "TOURIST ATTRACTION":
        st.markdown("<h2 style='margin-bottom:1rem;'>TOURIST ATTRACTION</h2>", unsafe_allow_html=True)
        
        # Get location layout with adjacent text
        col1, col2 = st.columns([1, 10])
        with col1:
            location = streamlit_geolocation()
        with col2:
            st.markdown("<div style='margin-top:0.8rem; font-weight:600;'>MY LOCATION</div>", unsafe_allow_html=True)
        
        if location and location.get('latitude') and location.get('longitude'):
            user_lat = location['latitude']
            user_lon = location['longitude']
        else:
            user_lat = 37.5665
            user_lon = 126.9780
            
        m2 = folium.Map(location=[user_lat, user_lon], zoom_start=14, tiles="CartoDB positron")
        
        # User marker
        folium.Marker(
            [user_lat, user_lon],
            popup="You are here",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m2)
        
        # Tourist spots
        try:
            df_tour = pd.read_csv(os.path.join(DATA_DIR, 'tourist_spots.csv'))
            for _, row in df_tour.iterrows():
                if pd.notna(row['위도']) and pd.notna(row['경도']):
                    popup_html = f"""<div style="white-space: nowrap; font-family: Pretendard, sans-serif;"><b>[관광지] {row['장소명']}</b><br>주소: {row['주소']}<br>특징: {row.get('특징', '')}</div>"""
                    folium.Marker(
                        location=[row['위도'], row['경도']],
                        popup=folium.Popup(popup_html, max_width=500),
                        icon=folium.Icon(color="orange", icon="star")
                    ).add_to(m2)
        except Exception as e:
            st.error(f"Error loading tourist spots: {e}")
            
        st_folium(m2, center=[user_lat, user_lon], zoom=14, width=800, height=500, returned_objects=[])

if __name__ == "__main__":
    main()
