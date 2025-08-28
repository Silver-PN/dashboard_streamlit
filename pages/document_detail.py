import streamlit as st
import pandas as pd
import os
from PIL import Image
import base64
from io import BytesIO
from streamlit_pdf_viewer import pdf_viewer
import fitz  # PyMuPDF để vẽ khung đỏ
import json
import pathlib

# Cấu hình trang
st.set_page_config(layout="wide", page_title="Thông tin tài liệu")

# Ẩn navigation mặc định
st.markdown(
    """
    <style>
    /* hide the top-left pages nav that appears when using multipage */
    
    /* hide the sidebar navigation links (app, document types, ocr detail) */
    div[data-testid="stSidebarNav"] {display: none !important;}
    
    /* hide specific navigation elements */
    .st-emotion-cache-1jv7wse {display: none !important;}

    /* Hide default Streamlit sidebar header */
    # .st-emotion-cache-10p9htt {display: none !important;}
    /* Ensure this element layers above others */
    .st-emotion-cache-10p9htt {
        position: relative;
        z-index: 9999;
    }
      div[data-testid="stSidebarHeader"] {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 10000 !important;
        background: transparent !important;
        pointer-events: none !important;
    }
    
    /* Cho phép click vào collapse button */
    div[data-testid="stSidebarCollapseButton"] {
        pointer-events: auto !important;
    }
    .st-emotion-cache-1echtaq {padding-top: 0 !important; }
    
    
    
    /* Thu gọn spacing của header */
    h3, h4 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Thu gọn spacing của divider */
    hr {
        margin: 0.5rem 0 !important;
    }
    
    /* Thu gọn input fields */
    .stTextInput > div > div > input {
        padding: 0.3rem 0.5rem !important;
        font-size: 0.8rem !important;
        margin-bottom: 0.3rem !important;
    }
    
    .stNumberInput > div > div > input {
        padding: 0.3rem 0.5rem !important;
        font-size: 0.8rem !important;
        margin-bottom: 0.3rem !important;
    }
    
    .stDateInput > div > div > input {
        padding: 0.3rem 0.5rem !important;
        font-size: 0.8rem !important;
        margin-bottom: 0.3rem !important;
    }
    
    .stTextArea > div > div > textarea {
        padding: 0.3rem 0.5rem !important;
        font-size: 0.8rem !important;
        margin-bottom: 0.3rem !important;
        min-height: 60px !important;
    }
    
    /* Thu gọn spacing của Streamlit widgets */
    .stTextInput, .stSelectbox, .stDateInput, .stTextArea, .stNumberInput {
        margin-bottom: 0.3rem !important;
    }
    
    .stTextInput > label, .stSelectbox > label, .stDateInput > label, .stTextArea > label {
        margin-bottom: 0.2rem !important;
        font-size: 0.85rem !important;
    }
    
    /* Thu gọn button */
    .stButton > button {
        padding: 0.5rem 1rem !important;
        font-size: 0.875rem !important;
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
    
    /* Form styling */
    .form-container {
        background-color: #f8f9fa;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
    }
    
    .form-field {
        margin-bottom: 8px;
    }
    
    .form-field label {
        font-weight: 600;
        color: #333;
        margin-bottom: 5px;
        display: block;
    }
    
    /* PDF viewer styling */
    .pdf-container {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        height: 100%;
    }
    
    /* Thu gọn spacing giữa các hàng */
    .row-widget.stHorizontal {
        gap: 0.3rem !important;
    }
    
    /* Thu gọn spacing của columns */
    [data-testid="column"] {
        padding: 0.2rem 0.4rem !important;
    }
    
    /* Thu gọn tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem !important;
    }
    
    /* Thu gọn markdown elements */
    .stMarkdown p {
        margin-bottom: 0.3rem !important;
    }
    
    
    .input-field-container:hover {
        background-color: #ffe6e6 !important;
        border: 2px solid #ff4444 !important;
        box-shadow: 0 0 10px rgba(255, 68, 68, 0.3) !important;
    }
    
    .field-label:hover {
        color: #ff4444 !important;
        font-weight: 700 !important;
    }
    
    /* Thêm CSS cho focus event */
    .stTextInput input:focus,
    .stSelectbox select:focus,
    .stDateInput input:focus,
    .stTextArea textarea:focus,
    </style>
    

    """,
    unsafe_allow_html=True,
)

# Header với logo
try:
    import pathlib
    current_dir = pathlib.Path(__file__).parent
except Exception:
    logo_img = None
st.markdown("<h2 style='margin:0'>DEMO SỐ HÓA TÀI LIỆU</h2>", unsafe_allow_html=True)

# Thêm breadcrumb navigation
st.markdown("""
<div class="breadcrumb-container">
    <span class="breadcrumb-item" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'app.py'}, '*')">Trang chủ</span>
    <span class="breadcrumb-separator">/</span>
    <span class="breadcrumb-item" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'app.py'}, '*')">Số hóa tài liệu</span>
    <span class="breadcrumb-separator">/</span>
    <span class="breadcrumb-current">Thông tin tài liệu</span>
</div>
""", unsafe_allow_html=True)

# Sidebar menu (2 cấp, đồng bộ với các trang khác)
st.sidebar.markdown("## Menu")
with st.sidebar.expander("SỐ HÓA HỒ SƠ TÀI LIỆU", expanded=True):
    # Hỗ trợ tương thích ngược các key cũ
    if 'menu_choice' in st.session_state:
        legacy = st.session_state['menu_choice']
        if legacy in ("Quản lý danh mục trường thông tin", "Quản lý loại văn bản"):
            st.session_state['main_menu'] = "Quản lý danh mục trường thông tin"
            st.session_state['manage_choice'] = (
                "Danh mục trường thông tin" if legacy == "Quản lý danh mục trường thông tin" else "Loại văn bản"
            )
        else:
            st.session_state['main_menu'] = "Số hóa tài liệu"
        del st.session_state['menu_choice']

    # Migrate giá trị cũ
    if st.session_state.get('main_menu') == 'Quản lý':
        st.session_state['main_menu'] = 'Quản lý danh mục trường thông tin'
    if st.session_state.get('manage_choice') == 'Quản lý danh mục trường thông tin':
        st.session_state['manage_choice'] = 'Danh mục trường thông tin'
    if st.session_state.get('manage_choice') == 'Quản lý loại văn bản':
        st.session_state['manage_choice'] = 'Loại văn bản'

    # Cấp 1
    main_default = 0 if st.session_state.get('main_menu', 'Số hóa tài liệu') == 'Số hóa tài liệu' else 1
    main_menu = st.radio(
        "Chọn chức năng",
        ["Số hóa tài liệu", "Quản lý danh mục trường thông tin"],
        index=main_default,
        key="main_menu",
        label_visibility="collapsed",
    )

    # Submenu cho "Số hóa tài liệu" trên trang chi tiết
    if main_menu == "Số hóa tài liệu":
        st.markdown("<div style='margin: 4px 0 6px 6px; color:#6c757d;'>— Số hóa tài liệu</div>", unsafe_allow_html=True)
        digitize_choice = st.radio(
            "Số hóa tài liệu",
            ["Danh sách hồ sơ", "Chi tiết hồ sơ"],
            index=1,  # đang ở trang chi tiết
            key="digitize_choice",
            label_visibility="collapsed",
        )
        if digitize_choice == "Danh sách hồ sơ":
            # quay về trang danh sách và dọn state
            try:
                st.query_params.clear()
            except:
                pass
            if 'selected_id' in st.session_state:
                del st.session_state['selected_id']
            if 'current_page' in st.session_state:
                del st.session_state['current_page']
            st.switch_page("app.py")

    # Cấp 2 cho quản lý
    manage_choice = None
    if main_menu == "Quản lý danh mục trường thông tin":
        st.markdown("<div style='margin: 4px 0 6px 6px; color:#6c757d;'>— Quản lý danh mục trường thông tin</div>", unsafe_allow_html=True)
        manage_default = 0 if st.session_state.get('manage_choice', 'Danh mục trường thông tin') == 'Danh mục trường thông tin' else 1
        manage_choice = st.radio(
            "Quản lý danh mục trường thông tin",
            ["Danh mục trường thông tin", "Loại văn bản"],
            index=manage_default,
            key="manage_choice",
            label_visibility="collapsed",
        )

    # Điều hướng khi ở mục quản lý
    if st.session_state.get('main_menu') == "Quản lý danh mục trường thông tin":
        if st.session_state.get('manage_choice') == "Danh mục trường thông tin":
            st.switch_page("pages/information_fields.py")
        elif st.session_state.get('manage_choice') == "Loại văn bản":
            st.switch_page("pages/document_types.py")

# Lấy ID từ session state hoặc query params
document_id = None

# Kiểm tra query params từ URL trước (để hỗ trợ F5 refresh)
try:
    query_params = st.query_params
    if 'id' in query_params:
        document_id = int(query_params['id'])
        # Lưu vào session state để duy trì khi navigate
        st.session_state['selected_id'] = document_id
    

except:
    pass

# Nếu chưa có từ URL, thử lấy từ session state
if not document_id and 'selected_id' in st.session_state:
    document_id = st.session_state['selected_id']
    # Cập nhật URL để sync với session state
    try:
        st.query_params['id'] = str(document_id)
    except:
        pass

if not document_id:
    st.error("Không tìm thấy ID tài liệu!")
    if st.button("← Quay về trang chính"):
        # Xóa query params khi quay về
        try:
            st.query_params.clear()
        except:
            pass
        # Xóa session state
        if 'selected_id' in st.session_state:
            del st.session_state['selected_id']
        st.switch_page("app.py")
    st.stop()

# Đường dẫn các file CSV
csv_file_path = current_dir.parent / "data" / "information_fields.csv"
records_csv_path = current_dir.parent / "data" / "records.csv"
document_types_csv_path = current_dir.parent / "data" / "document_types.csv"
records_api_data_path = current_dir.parent / "data" / "records_api_data.csv"
edits_csv_path = current_dir.parent / "data" / "records_edits.csv"


# Helpers to persist user edits per record
def load_edits():
    """Load saved edits from CSV. Returns DataFrame or empty DataFrame."""
    try:
        if os.path.exists(edits_csv_path):
            return pd.read_csv(edits_csv_path)
    except Exception:
        return pd.DataFrame()
    return pd.DataFrame()


def save_edits(record_id, edits_dict):
    """Save edits dict (as json string) for a given record_id into edits CSV.
    Overwrites existing row for record_id if present."""
    try:
        edits_df = load_edits()
        # Normalize values to be JSON serializable (e.g., date -> ISO string)
        serializable = {}
        try:
            from datetime import date, datetime
        except Exception:
            date = None
            datetime = None

        for k, v in edits_dict.items():
            if v is None:
                serializable[k] = None
            else:
                # datetime/date -> isoformat
                if (date and isinstance(v, date)) or (datetime and isinstance(v, datetime)):
                    try:
                        serializable[k] = v.isoformat()
                    except Exception:
                        serializable[k] = str(v)
                else:
                    serializable[k] = v

        row = {
            'record_id': int(record_id),
            'edited_fields': json.dumps(serializable, ensure_ascii=False)
        }

        if edits_df.empty:
            new_df = pd.DataFrame([row])
        else:
            # Remove existing row for this record_id if present
            edits_df = edits_df[edits_df['record_id'] != int(record_id)]
            new_df = pd.concat([edits_df, pd.DataFrame([row])], ignore_index=True)

        # Ensure folder exists
        edits_csv_path.parent.mkdir(parents=True, exist_ok=True)
        new_df.to_csv(edits_csv_path, index=False)
        return True
    except Exception as e:
        st.error(f"Lỗi khi lưu edits: {str(e)}")
        return False


def clear_edits(record_id):
    """Remove saved edits for a specific record_id."""
    try:
        edits_df = load_edits()
        if edits_df.empty:
            return True
        edits_df = edits_df[edits_df['record_id'] != int(record_id)]
        edits_csv_path.parent.mkdir(parents=True, exist_ok=True)
        edits_df.to_csv(edits_csv_path, index=False)
        return True
    except Exception as e:
        st.error(f"Lỗi khi xóa edits: {str(e)}")
        return False

# Hàm load dữ liệu
def load_information_fields():
    if os.path.exists(csv_file_path):
        try:
            return pd.read_csv(csv_file_path)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def load_records():
    if os.path.exists(records_csv_path):
        try:
            return pd.read_csv(records_csv_path)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def load_document_types():
    if os.path.exists(document_types_csv_path):
        try:
            return pd.read_csv(document_types_csv_path)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def load_api_data():
    """Load dữ liệu API từ CSV"""
    if os.path.exists(records_api_data_path):
        try:
            return pd.read_csv(records_api_data_path)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def get_api_data_for_record(record_id):
    """Lấy dữ liệu API cho một record cụ thể"""
    api_df = load_api_data()
    
    if api_df.empty:
        return None
    
    # Tìm record theo ID
    record_data = api_df[api_df['record_id'] == record_id]
    
    if record_data.empty:
        return None
    
    try:
        # Parse JSON string thành dict
        api_response_json = record_data.iloc[0]['api_response']
        api_data = json.loads(api_response_json)
        return api_data
    except Exception as e:
        st.error(f"Lỗi khi parse dữ liệu API: {str(e)}")
        return None

def extract_field_values(api_data):
    """Trích xuất các giá trị field từ extraction_results"""
    if not api_data:
        return {}
    
    try:
        # Lấy extraction_results từ API data
        extraction_results = api_data.get('data', {}).get('extraction_results', {})
        
        field_values = {}
        for field_name, field_data in extraction_results.items():
            if isinstance(field_data, dict):
                # Lấy giá trị từ trường 'value'
                value = field_data.get('value')
                if value is not None:
                    field_values[field_name] = value
        
        return field_values
    except Exception as e:
        st.error(f"Lỗi khi trích xuất field values: {str(e)}")
        return {}

# Load dữ liệu
information_fields_df = load_information_fields()
records_df = load_records()
document_types_df = load_document_types()

# Load dữ liệu API và trích xuất giá trị các field
api_data = get_api_data_for_record(document_id)
field_values = extract_field_values(api_data)

# Load saved edits for this record and overlay
saved_edits_df = load_edits()
saved_edits = {}
if not saved_edits_df.empty:
    try:
        row = saved_edits_df[saved_edits_df['record_id'] == int(document_id)]
        if not row.empty:
            saved_edits = json.loads(row.iloc[0]['edited_fields']) if row.iloc[0]['edited_fields'] else {}
    except Exception:
        saved_edits = {}

# Tìm thông tin hồ sơ theo ID
record_info = None
if not records_df.empty:
    record_info = records_df[records_df['STT'] == document_id]
    if not record_info.empty:
        record_info = record_info.iloc[0]

# Kiểm tra record_info có tồn tại không
if record_info is None or (hasattr(record_info, 'empty') and record_info.empty):
    st.error(f"Không tìm thấy hồ sơ với ID: {document_id}")
    if st.button("← Quay về trang chính"):
        # Xóa query params khi quay về
        try:
            st.query_params.clear()
        except:
            pass
        # Xóa session state
        if 'selected_id' in st.session_state:
            del st.session_state['selected_id']
        st.switch_page("app.py")
    st.stop()

# Lấy thông tin file PDF
try:
    pdf_file_name = record_info['Tên File']
    pdf_file_path = current_dir.parent / "data" / "pdf" / pdf_file_name
    document_type = record_info['LOẠI HỒ SƠ']
    document_type_code = record_info.get('MA_LOAI', '')  # Lấy mã loại nếu có
except (KeyError, TypeError) as e:
    st.error(f"Lỗi khi đọc thông tin tài liệu: {str(e)}")
    if st.button("← Quay về trang chính"):
        # Xóa query params khi quay về
        try:
            st.query_params.clear()
        except:
            pass
        # Xóa session state
        if 'selected_id' in st.session_state:
            del st.session_state['selected_id']
        st.switch_page("app.py")
    st.stop()

# Lọc trường thông tin theo loại văn bản
# Sử dụng document_type_code trực tiếp nếu có, nếu không thì tìm theo tên
ma_loai_van_ban = None
if document_type_code:  # Nếu có mã loại trực tiếp
    ma_loai_van_ban = document_type_code
elif not document_types_df.empty:  # Fallback: tìm theo tên
    try:
        matching_doc_type = document_types_df[document_types_df['ten_loai'] == document_type]
        if not matching_doc_type.empty:
            ma_loai_van_ban = matching_doc_type.iloc[0]['ma_loai']
    except Exception as e:
        st.warning(f"Lỗi khi tìm loại văn bản: {str(e)}")
        ma_loai_van_ban = None

# Lọc information fields theo ma_loai_van_ban
if ma_loai_van_ban:
    filtered_fields = information_fields_df[information_fields_df['ma_loai_van_ban'] == ma_loai_van_ban]
    if filtered_fields.empty:
        # Nếu không tìm thấy trường thông tin cho loại văn bản này, hiển thị tất cả
        st.warning(f"Không tìm thấy trường thông tin cho loại văn bản '{document_type}'. Hiển thị tất cả trường thông tin.")
        filtered_fields = information_fields_df
else:
    # Nếu không tìm thấy, hiển thị tất cả
    st.warning(f"Không tìm thấy loại văn bản '{document_type}' trong danh mục. Hiển thị tất cả trường thông tin.")
    filtered_fields = information_fields_df

# Sắp xếp theo thứ tự
if not filtered_fields.empty:
    filtered_fields = filtered_fields.sort_values('thu_tu')

# Hàm tạo input field theo kiểu dữ liệu (cho layout cũ)
def create_input_field(field_info):
    ma = field_info['ma']
    ten = field_info['ten']
    kieu_nhap = field_info['kieu_nhap']
    
    # Tạo key duy nhất cho mỗi field
    field_key = f"field_{ma}"
    
    if kieu_nhap == "Chữ":
        return st.text_input(f"{ten} (*)", key=field_key, placeholder=f"Nhập {ten.lower()}")
    elif kieu_nhap == "Ngày tháng tuỳ chọn":
        return st.date_input(f"{ten} (*)", key=field_key)
    elif kieu_nhap == "TextArea":
        return st.text_area(f"{ten} (*)", key=field_key, placeholder=f"Nhập {ten.lower()}")
    elif kieu_nhap == "Danh mục phông":
        # Tạo danh sách phông mẫu
        phong_options = ["-Mã phông-", "PHONG001", "PHONG002", "PHONG003"]
        return st.selectbox(f"{ten} (*)", phong_options, key=field_key)
    elif kieu_nhap == "Danh mục động":
        # Tạo danh sách động mẫu
        dong_options = ["-Chọn-", "Tùy chọn 1", "Tùy chọn 2", "Tùy chọn 3"]
        return st.selectbox(f"{ten} (*)", dong_options, key=field_key)
    else:
        return st.text_input(f"{ten} (*)", key=field_key, placeholder=f"Nhập {ten.lower()}")

# Hàm load vị trí các field từ API data
def load_field_positions():
    """Load vị trí các field từ API data nếu có, nếu không dùng default"""
    # Khởi tạo với các vị trí mặc định
    positions = {
        # Fields cho Văn bản hành chính (VBHC2) - Default positions
        "QD": [{"left": 120.1690368652344, "top": 80.88623046875, "width": 150, "height": 50}],          
        "SBAQD": [{"left": 850, "top": 350, "width": 200, "height": 30}],     
        "SBAQDLQ": [{"left": 100, "top": 400, "width": 200, "height": 10}],     
        "SBAQDHH": [{"left": 100, "top": 450, "width": 200, "height": 30}],    
        "QDBALH": [{"left": 100, "top": 500, "width": 300, "height": 30}],    
        "NGAYHH": [{"left": 750, "top": 300, "width": 200, "height": 30}],     
        "TRICHYEU": [{"left": 100, "top": 550, "width": 500, "height": 100}],   
        "TENCOQUAN": [{"left": 700, "top": 260, "width": 400, "height": 30}],  
        "TENNGUYENDON": [{"left": 100, "top": 700, "width": 300, "height": 30}], 
        "NAMSINHNGUYENDON": [{"left": 450, "top": 700, "width": 100, "height": 30}],
        "SOCHUNGMINH": [{"left": 600, "top": 700, "width": 200, "height": 30}], 
        
        # Fields cho Biên bản (BB)
        "BB": [{"left": 400, "top": 100, "width": 200, "height": 30}],         
        "TENVIEC": [{"left": 100, "top": 200, "width": 400, "height": 30}],   
        "NGAYLAP": [{"left": 600, "top": 200, "width": 200, "height": 30}],     
        "NOIDUNG": [{"left": 100, "top": 300, "width": 600, "height": 200}],    
        "NGUOILAP": [{"left": 100, "top": 600, "width": 200, "height": 30}],   
        "NGUOIKY": [{"left": 500, "top": 600, "width": 200, "height": 30}],   
        
        # Fallback positions for common field types
        "NGAY": [{"left": 750, "top": 300, "width": 200, "height": 30}],        
        "SO": [{"left": 850, "top": 350, "width": 200, "height": 30}],        
        "NOI_DUNG": [{"left": 100, "top": 300, "width": 600, "height": 200}],  
        "TEN": [{"left": 100, "top": 200, "width": 300, "height": 30}],        
        
        # Mapping mặc định
        "DEFAULT": [{"left": 100, "top": 100, "width": 200, "height": 30}]      # Vị trí mặc định góc trên trái
    }
    
    # Nếu có dữ liệu API, cập nhật positions từ bbox
    if api_data:
        try:
            extraction_results = api_data.get('data', {}).get('extraction_results', {})
            
            for field_name, field_data in extraction_results.items():
                if isinstance(field_data, dict):
                    bbox_list = field_data.get('bbox', [])
                    
                    if bbox_list and isinstance(bbox_list, list):
                        # Chuyển đổi từ bbox format sang format của field_positions
                        converted_positions = []
                        
                        for bbox in bbox_list:
                                    # Hỗ trợ bbox có thông tin page và các trường cần thiết
                                    if isinstance(bbox, dict) and all(key in bbox for key in ['left', 'top', 'width', 'height']):
                                        # Giữ lại page nếu có (API trả page bắt đầu từ 1)
                                        pos = {
                                            "left": bbox['left'],
                                            "top": bbox['top'],
                                            "width": bbox['width'],
                                            "height": bbox['height']
                                        }
                                        if 'page' in bbox:
                                            pos['page'] = int(bbox['page'])
                                        converted_positions.append(pos)
                        
                        if converted_positions:
                            positions[field_name] = converted_positions
                            
        except Exception as e:
            st.error(f"Lỗi khi load bbox từ API data: {str(e)}")
    
    return positions

def get_field_positions_from_api(field_name):
    """Lấy bbox positions cho field từ API data"""
    if not api_data:
        return []
    
    try:
        extraction_results = api_data.get('data', {}).get('extraction_results', {})
        field_data = extraction_results.get(field_name, {})
        
        if isinstance(field_data, dict):
            bbox_list = field_data.get('bbox', [])
            
            if bbox_list and isinstance(bbox_list, list):
                positions = []
                for bbox in bbox_list:
                    if isinstance(bbox, dict) and all(key in bbox for key in ['left', 'top', 'width', 'height']):
                        pos = {
                            "left": bbox['left'],
                            "top": bbox['top'],
                            "width": bbox['width'], 
                            "height": bbox['height']
                        }
                        if 'page' in bbox:
                            try:
                                pos['page'] = int(bbox['page'])
                            except Exception:
                                pos['page'] = bbox['page']
                        positions.append(pos)
                return positions
    except Exception as e:
        st.error(f"Lỗi khi lấy bbox cho field {field_name}: {str(e)}")
    
    return []

# Load vị trí các field
FIELD_POSITIONS = load_field_positions()

# Hàm lấy vị trí field theo mã field và loại văn bản
def get_field_position(field_code, document_type_code=None):
    """Lấy vị trí {left, top, width, height} của field trong PDF"""
    
    # Ưu tiên lấy từ API data trước
    api_positions = get_field_positions_from_api(field_code)
    if api_positions:
        return api_positions
    
    # Nếu không có trong API, thử tìm vị trí theo mã field trong FIELD_POSITIONS
    if field_code in FIELD_POSITIONS:
        return FIELD_POSITIONS[field_code]
    
    # Thử tìm theo loại văn bản + mã field
    if document_type_code:
        combined_key = f"{document_type_code}_{field_code}"
        if combined_key in FIELD_POSITIONS:
            return FIELD_POSITIONS[combined_key]
    
    # Fallback: sử dụng vị trí mặc định
    return FIELD_POSITIONS.get("DEFAULT", [{"left": 100, "top": 100, "width": 200, "height": 30}])

# Hàm tạo PDF với khung đỏ highlight
def create_highlighted_pdf(pdf_bytes, field_code, document_type_code=None):
    """Tạo PDF với khung đỏ highlight cho field được chọn"""
    try:
        # Mở PDF từ bytes
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        # Lấy vị trí của field (có thể chứa page index)
        positions = get_field_position(field_code, document_type_code)

        # Lấy page_dimensions từ api_data nếu có (dùng để scale coords API -> kích thước PDF thực tế)
        api_page_dims = None
        try:
            api_page_dims = api_data.get('data', {}).get('page_dimensions', {}) if api_data else None
        except Exception:
            api_page_dims = None

        if positions:
            # Vẽ khung đỏ cho từng vùng trên trang tương ứng
            for pos in positions:
                # Default page index = 1 (API sử dụng 1-based pages)
                page_index = int(pos.get('page', 1)) - 1
                if page_index < 0 or page_index >= len(doc):
                    # Nếu page không hợp lệ, fallback vẽ vào trang đầu
                    page_index = 0

                page = doc[page_index]

                # Lấy kích thước trang thực tế (fitz)
                page_rect = page.rect
                pdf_page_width = page_rect.width
                pdf_page_height = page_rect.height

                # Nếu API cung cấp kích thước nguồn, scale từ API coords -> PDF coords
                if api_page_dims and str(page_index+1) in api_page_dims:
                    try:
                        src = api_page_dims[str(page_index+1)]
                        src_w = float(src.get('width', pdf_page_width))
                        src_h = float(src.get('height', pdf_page_height))
                        src_dpi = float(src.get('dpi', 72))

                        # Convert API pixels -> PDF points (1 point = 1/72 inch)
                        px_to_pt = 72.0 / src_dpi if src_dpi else 1.0

                        left_pt = pos["left"] * px_to_pt
                        top_pt = pos["top"] * px_to_pt
                        width_pt = pos["width"] * px_to_pt
                        height_pt = pos["height"] * px_to_pt

                        # Source page dims in points
                        src_w_pt = src_w * px_to_pt
                        src_h_pt = src_h * px_to_pt

                        # Scale between PDF page points and source points
                        scale_x = pdf_page_width / src_w_pt if src_w_pt else 1.0
                        scale_y = pdf_page_height / src_h_pt if src_h_pt else 1.0

                        left = left_pt * scale_x
                        top = top_pt * scale_y
                        width = width_pt * scale_x
                        height = height_pt * scale_y
                    except Exception:
                        # Nếu lỗi khi scale, fallback giữ nguyên giá trị không scale
                        left = pos["left"]
                        top = pos["top"]
                        width = pos["width"]
                        height = pos["height"]
                else:
                    # Không có thông tin kích thước nguồn -> dùng nguyên giá trị từ API
                    left = pos["left"]
                    top = pos["top"]
                    width = pos["width"]
                    height = pos["height"]

                x1 = left
                y1 = top
                x2 = left + width
                y2 = top + height

                rect = fitz.Rect(x1, y1, x2, y2)

                # Vẽ khung đỏ với độ dày 3px
                try:
                    page.draw_rect(rect, color=(1, 0, 0), width=3, fill=None)
                    # Thêm highlight background nhẹ (nếu supported)
                    try:
                        page.draw_rect(rect, color=(1, 0, 0), fill=(1, 0, 0), fill_opacity=0.08)
                    except TypeError:
                        # Một số version PyMuPDF không hỗ trợ fill_opacity, ignore
                        page.draw_rect(rect, color=(1, 0, 0), fill=(1, 0, 0))
                except Exception:
                    # Nếu draw_rect thất bại, tiếp tục vẽ region khác
                    continue
        
        # Chuyển thành bytes
        modified_pdf_bytes = doc.write()
        doc.close()
        return modified_pdf_bytes
    except Exception as e:
        st.error(f"Lỗi khi tạo PDF highlight: {str(e)}")
        return pdf_bytes




# Giao diện chính
st.markdown(f"<h3>Thông tin tài liệu - ID: {document_id}</h3>", unsafe_allow_html=True)

# Debug panel (có thể ẩn/hiện)
with st.expander("🐛 Debug Panel - PDF & Bbox Info"):
    col_debug1, col_debug2 = st.columns(2)
    
    with col_debug1:
        st.markdown("**📄 PDF Information:**")
        try:
            if os.path.exists(pdf_file_path):
                with open(pdf_file_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()
                
                doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                if len(doc) > 0:
                    page = doc[0]
                    rect = page.rect
                    st.write(f"• **Pages:** {len(doc)}")
                    st.write(f"• **Width:** {rect.width:.1f}px")
                    st.write(f"• **Height:** {rect.height:.1f}px")
                    st.write(f"• **Bounds:** ({rect.x0:.1f}, {rect.y0:.1f}) to ({rect.x1:.1f}, {rect.y1:.1f})")
                doc.close()
        except Exception as e:
            st.error(f"Error reading PDF: {str(e)}")
    
    with col_debug2:
        st.markdown("**📍 Available Bbox Fields:**")
        if api_data:
            extraction_results = api_data.get('data', {}).get('extraction_results', {})
            bbox_fields = []
            
            for field_name, field_data in extraction_results.items():
                if isinstance(field_data, dict):
                    bbox_list = field_data.get('bbox', [])
                    if bbox_list and isinstance(bbox_list, list) and len(bbox_list) > 0:
                        bbox_fields.append(f"• **{field_name}:** {len(bbox_list)} vùng")
            
            if bbox_fields:
                for field_info in bbox_fields[:10]:  # Chỉ hiển thị 10 field đầu
                    st.write(field_info)
                if len(bbox_fields) > 10:
                    st.write(f"... và {len(bbox_fields) - 10} field khác")
            else:
                st.write("Không có field nào có bbox data")
        else:
            st.write("Không có API data")

# State để theo dõi field đang được hover
if 'highlighted_field' not in st.session_state:
    st.session_state.highlighted_field = None

# Hiển thị thông tin mapping nếu có (ẩn thông báo màu)
if ma_loai_van_ban:
    if document_type_code:
        pass  # Ẩn thông báo thành công
    else:
        pass  # Ẩn thông báo thành công
else:
    pass  # Ẩn thông báo cảnh báo

# Tạo 2 cột chính - tăng chiều rộng cho cột phải để hiển thị PDF full màn hình
col_left, col_right = st.columns([1, 2])

# Cột trái - Form thông tin
with col_left:
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    # Hiển thị các trường thông tin từ information_fields
    if not filtered_fields.empty:
        
        # Tính toán số lượng trường có thể hiển thị trong 40% màn hình
        # Giả sử mỗi trường input chiếm khoảng 80px (bao gồm label, input, spacing)
        # Và 40% màn hình = 0.4 * 1080 = 432px (giả sử màn hình 1080p)
        max_fields_per_page = 7  # Số trường tối đa hiển thị trên mỗi trang
        
        # Lấy tổng số trường
        total_fields = len(filtered_fields)
        
        # Tính số trang cần thiết
        total_pages = (total_fields + max_fields_per_page - 1) // max_fields_per_page
        
        # Lấy trang hiện tại từ session state hoặc mặc định là 1
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 1
        
        current_page = st.session_state.current_page
        
        # Hiển thị thông tin phân trang
        if total_pages > 1:
            st.markdown(f"**Trang {current_page}/{total_pages}**")
            
            # Nút điều hướng trang với select box ở giữa
            col_prev, col_select, col_next = st.columns([1, 1, 1])
            
            with col_prev:
                if st.button("← Trước", key="prev_page", disabled=(current_page <= 1)):
                    st.session_state.current_page = current_page - 1
                    st.rerun()
            
            with col_select:
                # Tạo danh sách các trang để select
                page_options = list(range(1, total_pages + 1))
                selected_page = st.selectbox(
                    "Chọn trang:",
                    options=page_options,
                    index=current_page - 1,  # index bắt đầu từ 0
                    key="page_selector",
                    label_visibility="collapsed"
                )
                
                # Xử lý khi người dùng chọn trang khác
                if selected_page != current_page:
                    st.session_state.current_page = selected_page
                    st.rerun()
            
            with col_next:
                if st.button("Sau →", key="next_page", disabled=(current_page >= total_pages)):
                    st.session_state.current_page = current_page + 1
                    st.rerun()
            
            st.markdown("---")
        
        # Tính toán trường bắt đầu và kết thúc cho trang hiện tại
        start_idx = (current_page - 1) * max_fields_per_page
        end_idx = min(start_idx + max_fields_per_page, total_fields)
        
        # Lấy các trường cho trang hiện tại
        current_page_fields = filtered_fields.iloc[start_idx:end_idx]
        
        # Tạo form với các trường thông tin của trang hiện tại
        form_data = {}
        
        for _, field in current_page_fields.iterrows():
            # Tạo container với hover effect
            field_container = st.container()
            
            with field_container:
                # Tạo 2 cột: label và input field
                col_label, col_input = st.columns([1, 2])
                
                with col_label:
                    # Hiển thị label với class CSS
                    st.markdown(f"<p class='field-label' style='margin-bottom:0.2rem; font-weight:600; font-size:0.85rem;'>{field['ten']} (*)</p>", unsafe_allow_html=True)
                
                with col_input:
                    # Wrap input trong container có class CSS  
                    st.markdown('<div class="input-field-container">', unsafe_allow_html=True)
                    
                    # Tạo input field và button trong cùng 1 hàng
                    input_col, btn_col = st.columns([5, 1])
                    
                    with input_col:
                        # Lấy giá trị từ saved edits -> API data -> default
                        api_value = ""
                        if field['ma'] in saved_edits and saved_edits.get(field['ma']) is not None:
                            api_value = saved_edits.get(field['ma'])
                        else:
                            api_value = field_values.get(field['ma'], '')
                        
                        # Tạo input field với giá trị từ API làm default
                        if field['kieu_nhap'] == "Chữ":
                            input_value = st.text_input(
                                f"{field['ten']}", 
                                value=api_value if api_value else "",
                                key=f"field_{field['ma']}", 
                                placeholder=f"Nhập {field['ten'].lower()}", 
                                label_visibility="collapsed"
                            )
                        elif field['kieu_nhap'] == "Ngày tháng tuỳ chọn":
                            # Xử lý date input - cần parse từ string nếu có
                            date_value = None
                            if api_value:
                                try:
                                    # Thử parse các format ngày thông dụng
                                    from datetime import datetime
                                    # Thử format "17 tháng 9 năm 2014"
                                    if "tháng" in str(api_value) and "năm" in str(api_value):
                                        import re
                                        match = re.search(r'(\d+)\s+tháng\s+(\d+)\s+năm\s+(\d+)', str(api_value))
                                        if match:
                                            day, month, year = match.groups()
                                            date_value = datetime(int(year), int(month), int(day)).date()
                                    else:
                                        # Thử parse format ISO hoặc các format khác
                                        date_value = datetime.strptime(str(api_value), "%Y-%m-%d").date()
                                except:
                                    date_value = None
                            
                            input_value = st.date_input(
                                f"{field['ten']}", 
                                value=date_value,
                                key=f"field_{field['ma']}", 
                                label_visibility="collapsed"
                            )
                        elif field['kieu_nhap'] == "TextArea":
                            input_value = st.text_area(
                                f"{field['ten']}", 
                                value=api_value if api_value else "",
                                key=f"field_{field['ma']}", 
                                placeholder=f"Nhập {field['ten'].lower()}", 
                                label_visibility="collapsed"
                            )
                        elif field['kieu_nhap'] == "Danh mục phông":
                            phong_options = ["-Mã phông-", "PHONG001", "PHONG002", "PHONG003"]
                            # Tìm index của giá trị API nếu có
                            default_index = 0
                            if api_value and api_value in phong_options:
                                default_index = phong_options.index(api_value)
                            
                            input_value = st.selectbox(
                                f"{field['ten']}", 
                                phong_options, 
                                index=default_index,
                                key=f"field_{field['ma']}", 
                                label_visibility="collapsed"
                            )
                        elif field['kieu_nhap'] == "Danh mục động":
                            dong_options = ["-Chọn-", "Tùy chọn 1", "Tùy chọn 2", "Tùy chọn 3"]
                            # Thêm giá trị API vào options nếu không có sẵn
                            if api_value and api_value not in dong_options:
                                dong_options.append(api_value)
                            
                            # Tìm index của giá trị API
                            default_index = 0
                            if api_value and api_value in dong_options:
                                default_index = dong_options.index(api_value)
                            
                            input_value = st.selectbox(
                                f"{field['ten']}", 
                                dong_options, 
                                index=default_index,
                                key=f"field_{field['ma']}", 
                                label_visibility="collapsed"
                            )
                        else:
                            input_value = st.text_input(
                                f"{field['ten']}", 
                                value=api_value if api_value else "",
                                key=f"field_{field['ma']}", 
                                placeholder=f"Nhập {field['ten'].lower()}", 
                                label_visibility="collapsed"
                            )
                    
                    with btn_col:
                        # Button để highlight field
                        if st.button("📍", key=f"highlight_{field['ma']}", help=f"Xem vị trí {field['ten']} trong PDF"):
                            st.session_state.highlighted_field = field['ma']
                            st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                        # Lưu giá trị vào form_data
                form_data[field['ma']] = input_value

        # Buttons for save/reset edits below the form
        st.markdown("---")
        btn_col1, btn_col2 = st.columns([1, 1])
        with btn_col1:
            if st.button("Lưu thay đổi", key=f"save_edits_{document_id}"):
                # Collect only non-empty inputs to save
                to_save = {k: v for k, v in form_data.items() if v not in (None, "", [])}
                ok = save_edits(document_id, to_save)
                if ok:
                    st.success("Đã lưu thay đổi.")
                    # update saved_edits in-memory
                    saved_edits.update(to_save)
        with btn_col2:
            if st.button("Xóa lưu thay đổi", key=f"reset_edits_{document_id}"):
                ok = clear_edits(document_id)
                if ok:
                    st.success("Đã xóa lưu thay đổi cho hồ sơ này.")
                    # clear session values for this page so inputs refresh
                    for k in list(st.session_state.keys()):
                        if k.startswith("field_"):
                            try:
                                del st.session_state[k]
                            except Exception:
                                pass
                    st.experimental_rerun()
      
    else:
        st.warning("Không tìm thấy trường thông tin nào cho loại văn bản này!")
        if st.button("← Quay về trang chính"):
            # Xóa query params khi quay về
            try:
                st.query_params.clear()
            except:
                pass
            # Xóa session state
            if 'selected_id' in st.session_state:
                del st.session_state['selected_id']
            if 'current_page' in st.session_state:
                del st.session_state['current_page']
            st.switch_page("app.py")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Cột phải - PDF Viewer
with col_right:
    st.markdown('<div class="pdf-container">', unsafe_allow_html=True)
    # Kiểm tra file PDF có tồn tại không
    if os.path.exists(pdf_file_path):
        try:
            # Tạo tabs cho PDF viewer
            tab1, tab2, tab3 = st.tabs(["PDF", "File đính kèm", "Chi tiết"])
            
            with tab3:
                st.markdown("**Thông tin chi tiết tài liệu:**")
                
                # Hiển thị thông tin cơ bản
                st.write(f"**ID:** {document_id}")
                st.write(f"**Loại hồ sơ:** {document_type}")
                st.write(f"**Tên file:** {pdf_file_name}")
                st.write(f"**Thời gian tải lên:** {record_info['THỜI GIAN TẢI LÊN']}")
                st.write(f"**Trạng thái:** {record_info['TRẠNG THÁI DỮ LIỆU']}")
                
                # Hiển thị thông tin kích thước PDF
                try:
                    with open(pdf_file_path, "rb") as pdf_file:
                        pdf_bytes = pdf_file.read()
                    
                    # Mở PDF để lấy thông tin kích thước
                    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                    
                    if len(doc) > 0:
                        page = doc[0]  # Trang đầu tiên
                        rect = page.rect
                        
                        st.markdown("**📄 Thông tin PDF:**")
                        st.write(f"**Số trang:** {len(doc)}")
                        st.write(f"**Kích thước trang 1:**")
                        st.write(f"  - **Width (Chiều rộng):** {rect.width:.1f} pixels")
                        st.write(f"  - **Height (Chiều cao):** {rect.height:.1f} pixels")
                        st.write(f"  - **Left:** {rect.x0:.1f}")
                        st.write(f"  - **Top:** {rect.y0:.1f}")
                        st.write(f"  - **Right:** {rect.x1:.1f}")
                        st.write(f"  - **Bottom:** {rect.y1:.1f}")
                    
                    doc.close()
                    
                except Exception as e:
                    st.error(f"Lỗi khi đọc thông tin PDF: {str(e)}")
                
                st.markdown("---")
                
                # Hiển thị thông tin từ form_data nếu có (chỉ những field đã được chỉnh sửa)
                if 'form_data' in locals() and form_data:
                    st.markdown("**Thông tin từ form (đã chỉnh sửa):**")
                    has_modified_data = False
                    
                    for ma, value in form_data.items():
                        if value:
                            # So sánh với giá trị từ API để chỉ hiển thị field đã thay đổi
                            # Determine baseline (saved edit > API)
                            baseline = saved_edits.get(ma, field_values.get(ma, ''))

                            # Chỉ hiển thị nếu giá trị khác với baseline (saved/API)
                            if str(value) != str(baseline):
                                has_modified_data = True
                                # Tìm tên field tương ứng
                                field_name = ""
                                for _, field in filtered_fields.iterrows():
                                    if field['ma'] == ma:
                                        field_name = field['ten']
                                        break
                                
                                if field_name:
                                    # Show both API and Saved if applicable
                                    api_value = field_values.get(ma, '')
                                    saved_val = saved_edits.get(ma)
                                    meta = []
                                    if saved_val is not None and str(saved_val) != str(api_value):
                                        meta.append(f"Đã lưu: {saved_val}")
                                    if api_value:
                                        meta.append(f"API: {api_value}")

                                    meta_txt = f" ({' | '.join(meta)})" if meta else ""
                                    st.write(f"**{field_name} ({ma}):** {value}{meta_txt}")
                                else:
                                    st.write(f"**{ma}:** {value}")
                    
                    if not has_modified_data:
                        st.info("Không có thông tin nào được chỉnh sửa so với dữ liệu API.")
                else:
                    st.info("Chưa có thông tin được nhập vào form.")
                
                st.markdown("---")
                
                # Hiển thị thông tin API data
                if api_data:
                    st.markdown("**📊 Thông tin dữ liệu API:**")
                    st.success(f"✅ Đã load dữ liệu API cho record ID: {document_id}")
                    st.write(f"🔍 **Số field đã trích xuất:** {len(field_values)}")
                    
                    # Đếm số field có bbox
                    bbox_count = 0
                    extraction_results = api_data.get('data', {}).get('extraction_results', {})
                    for field_name, field_data in extraction_results.items():
                        if isinstance(field_data, dict):
                            bbox_list = field_data.get('bbox', [])
                            if bbox_list and isinstance(bbox_list, list) and len(bbox_list) > 0:
                                bbox_count += 1
                    
                    st.write(f"📍 **Số field có thông tin vị trí (bbox):** {bbox_count}")
                    
                    # Hiển thị các field đã trích xuất
                    if field_values:
                        st.markdown("**Dữ liệu đã trích xuất từ API:**")
                        for field_name, value in field_values.items():
                            if value:  # Chỉ hiển thị field có giá trị
                                # Tìm tên field tương ứng từ information_fields
                                field_display_name = field_name
                                for _, field in filtered_fields.iterrows():
                                    if field['ma'] == field_name:
                                        field_display_name = field['ten']
                                        break
                                
                                # Kiểm tra field có bbox không
                                has_bbox = False
                                field_data = extraction_results.get(field_name, {})
                                if isinstance(field_data, dict):
                                    bbox_list = field_data.get('bbox', [])
                                    has_bbox = bbox_list and isinstance(bbox_list, list) and len(bbox_list) > 0
                                
                                bbox_indicator = " 📍" if has_bbox else ""
                                st.write(f"- **{field_display_name} ({field_name}){bbox_indicator}:** {value}")
                        
                        # Hiển thị raw API data dưới dạng expandable
                        with st.expander("🔍 Xem dữ liệu API gốc"):
                            st.json(api_data)
                    else:
                        st.info("Không có field nào được trích xuất từ API.")
                else:
                    st.warning(f"⚠️ Không tìm thấy dữ liệu API cho record ID: {document_id}")
                    st.info("Dữ liệu có thể chưa được xử lý OCR hoặc bị lỗi trong quá trình lưu trữ.")
            
            with tab2:
                st.markdown("**File đính kèm:**")
                st.write(f"📎 {pdf_file_name}")
                
                # Nút download file
                if st.button("⬇️ Tải xuống PDF", type="primary"):
                    try:
                        with open(pdf_file_path, "rb") as f:
                            pdf_bytes = f.read()
                        st.download_button(
                            label="📥 Tải xuống",
                            data=pdf_bytes,
                            file_name=pdf_file_name,
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"Lỗi khi tải file: {str(e)}")
            
            with tab1:
                # Hiển thị thông tin field đang được highlight
                if st.session_state.highlighted_field:
                    field_code = st.session_state.highlighted_field
                    positions = get_field_position(field_code, ma_loai_van_ban)
                    
                    st.markdown(f"**🎯 Đang hiển thị vị trí của field:** `{field_code}`")
                    
                    # Hiển thị số lượng bbox
                    if positions:
                        st.markdown(f"**📍 Số vùng được đánh dấu:** {len(positions)}")
                        
                        # Hiển thị tọa độ nếu từ API
                        api_positions = get_field_positions_from_api(field_code)
                        if api_positions:
                            st.success("✅ Sử dụng vị trí từ dữ liệu OCR")
                        else:
                            st.info("ℹ️ Sử dụng vị trí mặc định (không có dữ liệu OCR)")
                        
                        # Hiển thị thông tin chi tiết các bbox
                        with st.expander("📍 Chi tiết vị trí các vùng"):
                            for i, pos in enumerate(positions):
                                st.markdown(f"**Vùng {i+1}:**")
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"• **Left:** {pos['left']:.1f}")
                                    st.write(f"• **Width:** {pos['width']:.1f}")
                                with col2:
                                    st.write(f"• **Top:** {pos['top']:.1f}")
                                    st.write(f"• **Height:** {pos['height']:.1f}")
                                
                                # Tính toán right và bottom
                                right = pos['left'] + pos['width']
                                bottom = pos['top'] + pos['height']
                                st.write(f"• **Right:** {right:.1f} | **Bottom:** {bottom:.1f}")
                                
                                if i < len(positions) - 1:
                                    st.markdown("---")
                    
                    col_clear, col_debug = st.columns([1, 1])
                    with col_clear:
                        if st.button("❌ Xóa highlight", key="clear_highlight"):
                            st.session_state.highlighted_field = None
                            st.rerun()
                    
                    with col_debug:
                        # Nút để copy coordinates để debug
                        if st.button("📋 Copy coordinates", key="copy_coords"):
                            if positions:
                                coords_text = f"Field: {field_code}\n"
                                for i, pos in enumerate(positions):
                                    coords_text += f"Vùng {i+1}: left={pos['left']:.1f}, top={pos['top']:.1f}, width={pos['width']:.1f}, height={pos['height']:.1f}\n"
                                st.code(coords_text, language="text")
                
                # Hiển thị PDF với streamlit-pdf-viewer
                try:
                    # Sử dụng streamlit-pdf-viewer để hiển thị PDF
                    with open(pdf_file_path, "rb") as pdf_file:
                        original_pdf_bytes = pdf_file.read()
                    
                    # Tạo PDF với highlight nếu có field được chọn
                    if st.session_state.highlighted_field:
                        display_pdf_bytes = create_highlighted_pdf(
                            original_pdf_bytes, 
                            st.session_state.highlighted_field,
                            ma_loai_van_ban  # Truyền mã loại văn bản
                        )
                        pdf_key = f"pdf_viewer_highlighted_{st.session_state.highlighted_field}"
                    else:
                        display_pdf_bytes = original_pdf_bytes
                        pdf_key = "pdf_viewer_normal"
                    
                    # Hiển thị PDF với streamlit-pdf-viewer (100% zoom để xem toàn bộ trang)
                    pdf_viewer(
                        display_pdf_bytes,
                        height=750,
                        width="100%",
                        key=pdf_key
                    )
        
        
                    
                except Exception as e:
                    st.error(f"Không thể đọc file PDF: {str(e)}")
                    st.info("Vui lòng kiểm tra file PDF có bị lỗi không.")
        
        except Exception as e:
            st.error(f"Lỗi khi xử lý file PDF: {str(e)}")
    
    else:
        st.error(f"Không tìm thấy file PDF: {pdf_file_name}")
        st.info("File có thể đã bị xóa hoặc di chuyển.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Nút quay về trang chính ở cuối
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("← Quay về trang chính", type="secondary"):
        # Xóa query params khi quay về
        try:
            st.query_params.clear()
        except:
            pass
        # Xóa session state
        if 'selected_id' in st.session_state:
            del st.session_state['selected_id']
        st.switch_page("app.py")
