import streamlit as st
import pandas as pd
import os
from PIL import Image
import base64
from io import BytesIO
from streamlit_pdf_viewer import pdf_viewer
import fitz  # PyMuPDF để vẽ khung đỏ

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
    .st-emotion-cache-10p9htt {display: none !important;}
    
    
    
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
    
    .stSelectbox > div > div > div {
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
    logo_path = current_dir.parent / "data" / "logo-toa-an-nhan-dan-toi-cao.png"
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
st.markdown("""
<div class="breadcrumb-container">
    <span class="breadcrumb-item" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'app.py'}, '*')">Trang chủ</span>
    <span class="breadcrumb-separator">/</span>
    <span class="breadcrumb-item" onclick="window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'app.py'}, '*')">Số hóa tài liệu</span>
    <span class="breadcrumb-separator">/</span>
    <span class="breadcrumb-current">Thông tin tài liệu</span>
</div>
""", unsafe_allow_html=True)

# Sidebar menu
st.sidebar.markdown("## Menu")
with st.sidebar.expander("SỐ HÓA HỒ SƠ TÀI LIỆU", expanded=True):
    menu_choice = st.radio(
        "Chọn chức năng",
        ["Số hóa tài liệu", "Quản lý danh mục trường thông tin", "Quản lý loại văn bản"],
        index=0,
        key="menu_choice",
        label_visibility="collapsed"
    )

# Xử lý chuyển trang từ menu
if menu_choice == "Quản lý danh mục trường thông tin":
    st.switch_page("pages/information_fields.py")
elif menu_choice == "Quản lý loại văn bản":
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

# Load dữ liệu
information_fields_df = load_information_fields()
records_df = load_records()
document_types_df = load_document_types()

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

# Hàm load vị trí các field từ file CSV hoặc database (tương lai)
def load_field_positions():
    """Load vị trí các field từ nguồn dữ liệu"""
    # Tọa độ thực tế dựa trên document PDF Vietbank
    # Tọa độ theo định dạng (x1, y1, x2, y2) - pixel coordinates
    return {
        # Fields cho Văn bản hành chính (VBHC2)
        "QD": [(0, 100, 200, 260)],           # "Tờ trình" ở góc phải trên
        "SBAQD": [(850, 350, 1050, 380)],      # Số văn bản ở trung tâm
        "SBAQDLQ": [(100, 400, 300, 430)],     # Các trường liên quan bên trái
        "SBAQDHH": [(100, 450, 300, 480)],     # Các trường hiệu lực
        "QDBALH": [(100, 500, 400, 530)],      # Dropdown cho lý hôn tại
        "NGAYHH": [(750, 300, 950, 330)],      # Ngày tháng ở bên phải
        "TRICHYEU": [(100, 550, 600, 650)],    # Nội dung lớn ở giữa
        "TENCOQUAN": [(700, 260, 1100, 290)],  # Tên cơ quan ở phần header
        "TENNGUYENDON": [(100, 700, 400, 730)], # Tên nguyên đơn
        "NAMSINHNGUYENDON": [(450, 700, 550, 730)], # Năm sinh
        "SOCHUNGMINH": [(600, 700, 800, 730)], # Số CMND
        
        # Fields cho Biên bản (BB)
        "BB": [(400, 100, 600, 130)],          # Tiêu đề biên bản
        "TENVIEC": [(100, 200, 500, 230)],     # Tên việc
        "NGAYLAP": [(600, 200, 800, 230)],     # Ngày lập
        "NOIDUNG": [(100, 300, 700, 500)],     # Nội dung biên bản
        "NGUOILAP": [(100, 600, 300, 630)],    # Người lập
        "NGUOIKY": [(500, 600, 700, 630)],     # Người ký
        
        # Fallback positions for common field types
        "NGAY": [(750, 300, 950, 330)],        # Ngày tháng chung
        "SO": [(850, 350, 1050, 380)],         # Số văn bản chung
        "NOI_DUNG": [(100, 300, 700, 500)],    # Nội dung chung
        "TEN": [(100, 200, 400, 230)],         # Tên chung
        
        # Mapping mặc định
        "DEFAULT": [(100, 100, 300, 130)]      # Vị trí mặc định góc trên trái
    }

# Load vị trí các field
FIELD_POSITIONS = load_field_positions()

# Hàm lấy vị trí field theo mã field và loại văn bản
def get_field_position(field_code, document_type_code=None):
    """Lấy vị trí (x1, y1, x2, y2) của field trong PDF"""
    
    # Thử tìm vị trí theo mã field trực tiếp
    if field_code in FIELD_POSITIONS:
        return FIELD_POSITIONS[field_code]
    
    # Thử tìm theo loại văn bản + mã field
    if document_type_code:
        combined_key = f"{document_type_code}_{field_code}"
        if combined_key in FIELD_POSITIONS:
            return FIELD_POSITIONS[combined_key]
    
    # Fallback: sử dụng vị trí mặc định
    return FIELD_POSITIONS.get("DEFAULT", [(100, 100, 300, 130)])

# Hàm tạo PDF với khung đỏ highlight
def create_highlighted_pdf(pdf_bytes, field_code, document_type_code=None):
    """Tạo PDF với khung đỏ highlight cho field được chọn"""
    try:
        # Mở PDF từ bytes
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Lấy vị trí của field
        positions = get_field_position(field_code, document_type_code)
        
        if positions:
            # Vẽ khung đỏ cho trang đầu tiên (có thể mở rộng cho nhiều trang)
            page = doc[0]
            for pos in positions:
                x1, y1, x2, y2 = pos
                rect = fitz.Rect(x1, y1, x2, y2)
                
                # Vẽ khung đỏ với độ dày 3px và fill trong suốt
                page.draw_rect(rect, color=(1, 0, 0), width=3, fill=None)
                
                # Thêm highlight background trong suốt (optional)
                page.draw_rect(rect, color=(1, 0, 0), fill=(1, 0, 0), fill_opacity=0.1)
        
        # Chuyển thành bytes
        modified_pdf_bytes = doc.write()
        doc.close()
        return modified_pdf_bytes
    except Exception as e:
        st.error(f"Lỗi khi tạo PDF highlight: {str(e)}")
        return pdf_bytes




# Giao diện chính
st.markdown(f"<h3>Thông tin tài liệu - ID: {document_id}</h3>", unsafe_allow_html=True)

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
        st.markdown("**Khung biên mục tài liệu:**")
        
        # Tạo form với các trường thông tin
        form_data = {}
        
        # Hiển thị thông tin về số lượng trường (ẩn thông báo màu xanh)
        # st.info(f"📋 Hiển thị {len(filtered_fields)} trường thông tin cho loại văn bản '{document_type}'")
        
        for _, field in filtered_fields.iterrows():
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
                        # Tạo input field đơn giản
                        if field['kieu_nhap'] == "Chữ":
                            input_value = st.text_input(
                                f"{field['ten']}", 
                                key=f"field_{field['ma']}", 
                                placeholder=f"Nhập {field['ten'].lower()}", 
                                label_visibility="collapsed"
                            )
                        elif field['kieu_nhap'] == "Ngày tháng tuỳ chọn":
                            input_value = st.date_input(
                                f"{field['ten']}", 
                                key=f"field_{field['ma']}", 
                                label_visibility="collapsed"
                            )
                        elif field['kieu_nhap'] == "TextArea":
                            input_value = st.text_area(
                                f"{field['ten']}", 
                                key=f"field_{field['ma']}", 
                                placeholder=f"Nhập {field['ten'].lower()}", 
                                label_visibility="collapsed"
                            )
                        elif field['kieu_nhap'] == "Danh mục phông":
                            phong_options = ["-Mã phông-", "PHONG001", "PHONG002", "PHONG003"]
                            input_value = st.selectbox(
                                f"{field['ten']}", 
                                phong_options, 
                                key=f"field_{field['ma']}", 
                                label_visibility="collapsed"
                            )
                        elif field['kieu_nhap'] == "Danh mục động":
                            dong_options = ["-Chọn-", "Tùy chọn 1", "Tùy chọn 2", "Tùy chọn 3"]
                            input_value = st.selectbox(
                                f"{field['ten']}", 
                                dong_options, 
                                key=f"field_{field['ma']}", 
                                label_visibility="collapsed"
                            )
                        else:
                            input_value = st.text_input(
                                f"{field['ten']}", 
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
        
        st.markdown("---")
        
        # Nút điều khiển
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        
        with col_btn1:
            if st.button("← Thoát", type="secondary"):
                # Xóa query params khi thoát
                try:
                    st.query_params.clear()
                except:
                    pass
                # Xóa session state
                if 'selected_id' in st.session_state:
                    del st.session_state['selected_id']
                st.switch_page("app.py")
        
        with col_btn2:
            if st.button("← Trước", type="primary"):
                # Logic chuyển đến record trước đó
                prev_id = document_id - 1
                if prev_id >= 1:
                    st.session_state['selected_id'] = prev_id
                    # Cập nhật URL
                    try:
                        st.query_params['id'] = str(prev_id)
                    except:
                        pass
                    st.rerun()
                else:
                    st.warning("Đây là record đầu tiên!")
        
        with col_btn3:
            if st.button("Sau →", type="primary"):
                # Logic chuyển đến record tiếp theo
                next_id = document_id + 1
                max_id = records_df['STT'].max() if not records_df.empty else 0
                if next_id <= max_id:
                    st.session_state['selected_id'] = next_id
                    # Cập nhật URL
                    try:
                        st.query_params['id'] = str(next_id)
                    except:
                        pass
                    st.rerun()
                else:
                    st.warning("Đây là record cuối cùng!")
        
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
                
                st.markdown("---")
                
                # Hiển thị thông tin từ form_data nếu có
                if 'form_data' in locals() and form_data:
                    st.markdown("**Thông tin từ form:**")
                    for ma, value in form_data.items():
                        if value:
                            # Tìm tên field tương ứng
                            field_name = ""
                            for _, field in filtered_fields.iterrows():
                                if field['ma'] == ma:
                                    field_name = field['ten']
                                    break
                            
                            if field_name:
                                st.write(f"**{field_name} ({ma}):** {value}")
                            else:
                                st.write(f"**{ma}:** {value}")
                else:
                    st.info("Chưa có thông tin được nhập vào form.")
            
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
                # if st.session_state.highlighted_field:
                #     field_code = st.session_state.highlighted_field
                #     positions = get_field_position(field_code, ma_loai_van_ban)
                    
                    # st.markdown(f"**🎯 Đang hiển thị vị trí của field:** `{field_code}`")
                    
                    # # Hiển thị tọa độ hiện tại
                    # if positions:
                    #     for i, pos in enumerate(positions):
                    #         x1, y1, x2, y2 = pos
                    #         st.markdown(f"**Tọa độ {i+1}:** x1={x1}, y1={y1}, x2={x2}, y2={y2}")
                    
                    # col_clear, col_edit = st.columns([1, 1])
                    # with col_clear:
                    #     if st.button("❌ Xóa highlight", key="clear_highlight"):
                    #         st.session_state.highlighted_field = None
                    #         st.rerun()
                    
                    # with col_edit:
                    #     # Nút để mở modal chỉnh sửa vị trí (tương lai)
                    #     if st.button("✏️ Chỉnh sửa vị trí", key="edit_position"):
                    #         st.info("🔧 Tính năng chỉnh sửa vị trí sẽ được phát triển trong phiên bản tiếp theo")
                    #         st.markdown("**Hướng dẫn tạm thời:**")
                    #         st.markdown(f"- Cập nhật tọa độ cho field `{field_code}` trong hàm `load_field_positions()`")
                    #         st.markdown("- Tọa độ theo format: (x1, y1, x2, y2) với đơn vị pixel")
                    #         st.markdown("- x1,y1: góc trên-trái; x2,y2: góc dưới-phải")
                
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
