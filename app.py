import streamlit as st
from PIL import Image
from config import get_nav_from_toml, hide_pages
import toml
from pathlib import Path


# Giao diện trang chính
st.set_page_config(layout="wide", page_title="Trang Chính - Table")

# Hide Streamlit's default pages navigation (the auto-generated multipage list)
st.markdown(
    """
    <style>
  
    /* Thu gọn spacing */
    .stMarkdown {
        margin-bottom: 0.25rem !important;
    }
    
    /* Thu gọn spacing của header */
    h3, h4 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Thu gọn spacing của divider */
    hr {
        margin: 0.5rem 0 !important;
    }
    
    /* Thu gọn button */
    .stButton > button {
        padding: 0.5rem 1rem !important;
        font-size: 0.875rem !important;
    }
    
    /* Thu gọn input */
    .stTextInput > div > div > input {
        padding: 0.5rem 0.75rem !important;
        font-size: 0.875rem !important;
    }
    
    /* Căn giữa nút View theo chiều cao */
    .stButton > button[data-testid="baseButton-secondary"] {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 100% !important;
    }
    
    /* Màu xanh nhạt cho nút Upload */
    .stButton > button[data-testid="baseButton-primary"] {
        background-color: #90EE90 !important;
        color: #000 !important;
        border: 1px solid #32CD32 !important;
    }
    
    .stButton > button[data-testid="baseButton-primary"]:hover {
        background-color: #98FB98 !important;
        border-color: #228B22 !important;
    }
    
    /* Breadcrumb styling */
    .breadcrumb-container {
        padding: 15px 0;
        border-bottom: 1px solid #e0e0e0;
        background-color: #f8f9fa;
        margin: 20px 0;
        border-radius: 5px;
    }
    
    .breadcrumb-item {
        color: #007bff;
        font-weight: 500;
        cursor: pointer;
        transition: color 0.2s ease;
        margin-left: 10px;
    }
    
    .breadcrumb-item:hover {
        color: #0056b3;
        text-decoration: underline;
    }
    
    .breadcrumb-separator {
        margin: 0 10px;
        color: #ccc;
    }
    
    .breadcrumb-current {
        color: #333;
        font-weight: 500;
    }
    
    [data-testid="stNavSectionHeader"] {
        padding: 1px 8px;
    }
    
    [data-testid="stSidebarNavItems"] li:nth-child(2),
    [data-testid="stSidebarNavItems"] li:nth-child(3)  {
        padding: 0px 14px;
    }
   

    </style>
     """,
    unsafe_allow_html=True,
)

# --- Navbar with logo -------------------------------------------------
try:
    logo_path = "data/logo-toa-an-nhan-dan-toi-cao.png"
    logo_img = Image.open(logo_path)
except Exception:
    logo_img = None

nav_col1, nav_col2 = st.columns([1, 10])
with nav_col1:
    if logo_img:
        st.image(logo_img, width=72)
with nav_col2:
    st.markdown("<h2 style='margin:0'>PHẦN MỀM KHO LƯU TRỮ TÀI LIỆU SỐ HÓA</h2>", unsafe_allow_html=True)

# Thêm breadcrumb navigation
def get_page_mapping(toml_path: str = "page_section.toml") -> tuple[dict[str, str], str]:
    """Parses the toml file to create a mapping from url_path to name."""
    try:
        raw_pages = toml.loads(Path(toml_path).read_text(encoding="utf-8"))["pages"]
    except (FileNotFoundError, toml.decoder.TomlDecodeError, KeyError):
        return {}, ""

    url_to_name = {}
    default_page_name = ""
    is_first_page = True

    for page in raw_pages:
        if not page.get("is_section"):
            url_path = page.get("url_path")
            name = page.get("name")
            if url_path and name:
                url_to_name[url_path] = name
                if is_first_page:
                    default_page_name = name
                    is_first_page = False
    return url_to_name, default_page_name

url_map, default_name = get_page_mapping()
query_params = st.query_params.to_dict()
current_url_path = st.context.url.split("localhost:8501/")

current_page_title = default_name
if len(current_url_path) > 1 and current_url_path[1] in url_map:
    current_page_title = url_map[current_url_path[1]]

if current_page_title:

    breadcrumb_html = f"""
    <div class="breadcrumb-container">
        <span class="breadcrumb-item"> Trang chủ</span>
        <span class="breadcrumb-separator">/</span>
        <span class="breadcrumb-current">{current_page_title.strip()}</span>
    </div>
    """
    st.markdown(breadcrumb_html, unsafe_allow_html=True)

# print(st.session_state.get('selected_id', None))
# if not st.session_state.get('selected_id', None):
#     hide_pages(["Chi tiết OCR"])

# params = st.context.url
# if "detail" not in params:
#     st.session_state['selected_id'] = None
    
page = st.navigation(get_nav_from_toml())

page.run()