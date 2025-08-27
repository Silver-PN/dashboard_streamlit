import streamlit as st
import pandas as pd
import os
from PIL import Image

# Cấu hình trang
st.set_page_config(layout="wide", page_title="Danh mục trường thông tin")

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
    
    /* Thu gọn input fields */
    .stTextInput > div > div > input {
        padding: 0.5rem 0.75rem !important;
        font-size: 0.875rem !important;
    }
    
    .stSelectbox > div > div > div {
        padding: 0.5rem 0.75rem !important;
        font-size: 0.875rem !important;
    }
    
    .stNumberInput > div > div > input {
        padding: 0.5rem 0.75rem !important;
        font-size: 0.875rem !important;
    }
    
    /* Thu gọn button */
    .stButton > button {
        padding: 0.5rem 1rem !important;
        font-size: 0.875rem !important;
    }
    
    /* Thu gọn expander */
    .streamlit-expanderHeader {
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
    }
    
    /* Thu gọn spacing */
    .stMarkdown {
        margin-bottom: 0.25rem !important;
    }
    
    /* Thu gọn spacing giữa các section */
    .stExpander {
        margin-bottom: 0.5rem !important;
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
    st.caption("Quản lý danh mục trường thông tin")

# Thêm breadcrumb navigation
st.markdown("""
<div class="breadcrumb-container">
    <span class="breadcrumb-item"> Trang chủ</span>
    <span class="breadcrumb-separator">/</span>
    <span class="breadcrumb-item">Quản lý danh mục trường thông tin</span>
    <span class="breadcrumb-separator">/</span>
    <span class="breadcrumb-current">Danh mục trường thông tin</span>
</div>
""", unsafe_allow_html=True) 

# Sidebar menu
st.sidebar.markdown("## Menu")
with st.sidebar.expander("SỐ HÓA HỒ SƠ TÀI LIỆU", expanded=True):
    menu_choice = st.radio(
        "Chọn chức năng",
        ["Số hóa tài liệu", "Quản lý danh mục trường thông tin", "Quản lý loại văn bản"],
        index=1,
        key="menu_choice",
        label_visibility="collapsed"
    )

# Xử lý chuyển trang từ menu
if menu_choice == "Số hóa tài liệu":
    st.switch_page("app.py")
elif menu_choice == "Quản lý loại văn bản":
    st.switch_page("pages/document_types.py")

# Đường dẫn file CSV
csv_file_path = current_dir.parent / "data" / "information_fields.csv"
document_types_csv_path = current_dir.parent / "data" / "document_types.csv"

# Hàm load dữ liệu từ CSV
def load_information_fields():
    if os.path.exists(csv_file_path):
        try:
            df = pd.read_csv(csv_file_path)
            # Kiểm tra xem có cột ma_loai_van_ban chưa, nếu chưa thì thêm vào
            if 'ma_loai_van_ban' not in df.columns:
                df['ma_loai_van_ban'] = df['loai_van_ban']  # Tạm thời copy giá trị cũ
                df.to_csv(csv_file_path, index=False)
            return df
        except:
            # Nếu file bị lỗi, tạo file mới với dữ liệu mặc định
            default_data = pd.DataFrame({
                'ma': ['QD'],
                'ten': ['Quyết định'],
                'loai_van_ban': ['Văn bản hành chính'],
                'ma_loai_van_ban': ['VBHC2'],
                'thu_tu': [1],
                'ten_truong': ['Mã phông'],
                'ma_truong': ['IDProfileTemp'],
                'kieu_nhap': ['Danh mục phông']
            })
            default_data.to_csv(csv_file_path, index=False)
            return default_data
    else:
        # Tạo file mới nếu chưa tồn tại
        default_data = pd.DataFrame({
            'ma': ['QD'],
            'ten': ['Quyết định'],
            'loai_van_ban': ['Văn bản hành chính'],
            'ma_loai_van_ban': ['VBHC2'],
            'thu_tu': [1],
            'ten_truong': ['Mã phông'],
            'ma_truong': ['IDProfileTemp'],
            'kieu_nhap': ['Danh mục phông']
        })
        default_data.to_csv(csv_file_path, index=False)
        return default_data

# Hàm load danh sách loại văn bản
def load_document_types():
    if os.path.exists(document_types_csv_path):
        try:
            return pd.read_csv(document_types_csv_path)
        except:
            return pd.DataFrame({'ma_loai': [], 'ten_loai': []})
    else:
        return pd.DataFrame({'ma_loai': [], 'ten_loai': []})

# Hàm lưu dữ liệu vào CSV
def save_information_fields(df):
    df.to_csv(csv_file_path, index=False)

# Hàm thêm trường thông tin mới
def add_information_field(ma, ten, loai_van_ban, ma_loai_van_ban, thu_tu, ten_truong, ma_truong, kieu_nhap):
    df = load_information_fields()
    
    # Kiểm tra mã đã tồn tại
    if ma in df['ma'].values:
        return False, "Mã danh mục đã tồn tại!"
    
    # Thêm dòng mới
    new_row = pd.DataFrame({
        'ma': [ma],
        'ten': [ten],
        'loai_van_ban': [loai_van_ban],
        'ma_loai_van_ban': [ma_loai_van_ban],
        'thu_tu': [thu_tu],
        'ten_truong': [ten_truong],
        'ma_truong': [ma_truong],
        'kieu_nhap': [kieu_nhap]
    })
    df = pd.concat([df, new_row], ignore_index=True)
    
    # Lưu vào CSV
    save_information_fields(df)
    return True, "Thêm trường thông tin thành công!"

# Hàm xóa trường thông tin
def delete_information_field(ma):
    df = load_information_fields()
    df = df[df['ma'] != ma]
    save_information_fields(df)
    return "Đã xóa trường thông tin!"

# Load dữ liệu hiện tại
information_fields_df = load_information_fields()
document_types_df = load_document_types()

# Giao diện chính
st.markdown("<h3>Quản lý danh mục trường thông tin</h3>", unsafe_allow_html=True)

# Form thêm mới
with st.expander("Thêm mới danh mục trường thông tin", expanded=False):
    st.markdown("**Thông tin danh mục**")
    
    col1, col2, col3 = st.columns([1, 2, 2])
    
    with col1:
        ma = st.text_input("Mã (*)", placeholder="VD: QD", key="ma_input")
    
    with col2:
        ten = st.text_input("Tên (*)", placeholder="VD: Quyết định", key="ten_input")
    
    with col3:
        # Lấy danh sách loại văn bản từ CSV
        if not document_types_df.empty:
            # Tạo options với format "Mã - Tên" để hiển thị
            doc_type_options = [f"{row['ma_loai']} - {row['ten_loai']}" for _, row in document_types_df.iterrows()]
            doc_type_selected = st.selectbox("Loại văn bản (*)", doc_type_options, key="loai_van_ban_input")
            
            # Lấy mã và tên từ selection
            if doc_type_selected:
                ma_loai_van_ban = doc_type_selected.split(" - ")[0]
                loai_van_ban = doc_type_selected.split(" - ")[1]
            else:
                ma_loai_van_ban = ""
                loai_van_ban = ""
        else:
            doc_type_options = ['VBHC2 - Văn bản hành chính']
            doc_type_selected = st.selectbox("Loại văn bản (*)", doc_type_options, key="loai_van_ban_input")
            ma_loai_van_ban = "VBHC2"
            loai_van_ban = "Văn bản hành chính"
    
    st.markdown("**Cấu hình trường thông tin**")
    
    col1, col2, col3 = st.columns([1, 2, 2])
    
    with col1:
        thu_tu = st.number_input("Thứ tự (*)", min_value=1, value=1, key="thu_tu_input")
    
    with col2:
        kieu_nhap_options = ["Chữ", "Ngày tháng tuỳ chọn", "TextArea", "Danh mục phông", "Danh mục động"]
        kieu_nhap = st.selectbox("Kiểu nhập (*)", kieu_nhap_options, key="kieu_nhap_input")
    
    with col3:
        st.write("")  # Spacer
    
    if st.button("Thêm mới", type="primary"):
        if ma and ten and loai_van_ban and kieu_nhap:
            success, message = add_information_field(ma, ten, loai_van_ban, ma_loai_van_ban, thu_tu, "", "", kieu_nhap)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        else:
            st.error("Vui lòng nhập đầy đủ thông tin bắt buộc!")

# Hiển thị danh sách trường thông tin
st.markdown("<h4>Danh sách trường thông tin hiện tại</h4>", unsafe_allow_html=True)

# Filter theo loại văn bản
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    st.markdown("**Lọc theo loại văn bản:**")
with col2:
    # Tạo options cho filter
    if not document_types_df.empty:
        filter_options = ["Tất cả"] + [f"{row['ma_loai']} - {row['ten_loai']}" for _, row in document_types_df.iterrows()]
        selected_filter = st.selectbox("Chọn loại văn bản để lọc", filter_options, key="filter_doc_type", label_visibility="collapsed")
    else:
        filter_options = ["Tất cả", "VBHC2 - Văn bản hành chính"]
        selected_filter = st.selectbox("Chọn loại văn bản để lọc", filter_options, key="filter_doc_type", label_visibility="collapsed")
with col3:
    st.write("")  # Spacer

# Reload dữ liệu sau khi thêm mới
information_fields_df = load_information_fields()

# Lọc dữ liệu theo loại văn bản được chọn
if selected_filter and selected_filter != "Tất cả":
    ma_loai_filter = selected_filter.split(" - ")[0]
    filtered_df = information_fields_df[information_fields_df['ma_loai_van_ban'] == ma_loai_filter]
else:
    filtered_df = information_fields_df

# Header cho bảng
header_col1, header_col2, header_col3, header_col4, header_col5, header_col6 = st.columns([1, 1, 2, 1, 2, 1])
with header_col1:
    st.markdown("**Mã**")
with header_col2:
    st.markdown("**Tên**")
with header_col3:
    st.markdown("**Loại văn bản**")
with header_col4:
    st.markdown("**Thứ tự**")
with header_col5:
    st.markdown("**Kiểu nhập**")
with header_col6:
    st.markdown("**Thao tác**")

st.markdown("---")

if not filtered_df.empty:
    # Tạo bảng hiển thị
    for index, row in filtered_df.iterrows():
        col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 2, 1, 2, 1])
        
        with col1:
            st.write(f"**{row['ma']}**")
        
        with col2:
            st.write(row['ten'])
        
        with col3:
            st.write(row['loai_van_ban'])
        
        with col4:
            st.write(row['thu_tu'])
        
        with col5:
            st.write(row['kieu_nhap'])
        
        with col6:
            if st.button("Xóa", key=f"delete_{row['ma']}", type="secondary"):
                delete_information_field(row['ma'])
                st.success("Đã xóa trường thông tin!")
                st.rerun()
        
        st.divider()
    
    # Hiển thị thông tin về số lượng kết quả
    if selected_filter and selected_filter != "Tất cả":
        st.info(f"Hiển thị {len(filtered_df)} trường thông tin thuộc loại văn bản: {selected_filter}")
    else:
        st.info(f"Hiển thị tất cả {len(filtered_df)} trường thông tin")
else:
    if selected_filter and selected_filter != "Tất cả":
        st.info(f"Không có trường thông tin nào thuộc loại văn bản: {selected_filter}")
    else:
        st.info("Chưa có trường thông tin nào. Hãy thêm trường thông tin đầu tiên!")

# Nút quay về trang chính
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("← Quay về trang chính", type="secondary"):
        st.switch_page("app.py")
