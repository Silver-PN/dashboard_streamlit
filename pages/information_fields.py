import streamlit as st
import pandas as pd
import os
from PIL import Image
import json

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
except Exception:
    logo_img = None


st.markdown("<h2 style='margin:0'>DEMO SỐ HÓA TÀI LIỆU</h2>", unsafe_allow_html=True)

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
    # Menu 2 cấp với tên mới
    main_default = 1  # đang ở khu vực quản lý
    main_menu = st.radio(
        "Chọn chức năng",
        ["Số hóa tài liệu", "Quản lý danh mục trường thông tin"],
        index=main_default,
        key="main_menu",
        label_visibility="collapsed",
    )

    if main_menu == "Số hóa tài liệu":
        st.switch_page("app.py")

    # Submenu Quản lý (đổi nhãn và item)
    st.markdown("<div style='margin: 4px 0 6px 6px; color:#6c757d;'>— Quản lý danh mục trường thông tin</div>", unsafe_allow_html=True)
    manage_default = 0  # Trang hiện tại là "Danh mục trường thông tin"
    manage_choice = st.radio(
        "Quản lý danh mục trường thông tin",
        ["Danh mục trường thông tin", "Loại văn bản"],
        index=manage_default,
        key="manage_choice",
        label_visibility="collapsed",
    )

    if manage_choice == "Loại văn bản":
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
            # Đảm bảo có cột 'mota' (mô tả) để dùng cho schema
            if 'mota' not in df.columns:
                try:
                    df['mota'] = df['ten'] if 'ten' in df.columns else ""
                except Exception:
                    df['mota'] = ""
                df.to_csv(csv_file_path, index=False)
            return df
        except:
            # Nếu file bị lỗi, tạo file mới với dữ liệu mặc định
            default_data = pd.DataFrame({
                'ma': ['QD'],
                'ten': ['Quyết định'],
                'mota': ['Quyết định'],
                'loai_van_ban': ['Văn bản hành chính'],
                'ma_loai_van_ban': ['VBHC2'],
                'thu_tu': [1],
                'kieu_nhap': ['Danh mục phông']
            })
            default_data.to_csv(csv_file_path, index=False)
            return default_data
    else:
        # Tạo file mới nếu chưa tồn tại
        default_data = pd.DataFrame({
            'ma': ['QD'],
            'ten': ['Quyết định'],
            'mota': ['Quyết định'],
            'loai_van_ban': ['Văn bản hành chính'],
            'ma_loai_van_ban': ['VBHC2'],
            'thu_tu': [1],
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

# Đánh dấu các hồ sơ thuộc mã loại văn bản cần re-request
def mark_records_need_request(ma_loai_van_ban: str):
    try:
        import pandas as _pd
        rec_path = current_dir.parent / "data" / "records.csv"
        if not os.path.exists(rec_path):
            return
        df = _pd.read_csv(rec_path)
        if 'isrequest' not in df.columns:
            df['isrequest'] = 0
        mask = df['MA_LOAI'] == ma_loai_van_ban
        if mask.any():
            df.loc[mask, 'isrequest'] = 1
            df.to_csv(rec_path, index=False)
    except Exception:
        pass

# Hàm cập nhật tên và mô tả cho một trường thông tin
def update_information_field(ma, ten_moi, mota_moi):
    df = load_information_fields()
    mask = df['ma'] == ma
    if not mask.any():
        return False, "Không tìm thấy mã danh mục cần cập nhật!"
    # Chuẩn hóa giá trị
    ten_moi = (ten_moi or "").strip()
    mota_moi = (mota_moi if mota_moi is not None else ten_moi).strip()
    if not ten_moi:
        return False, "Tên không được để trống!"
    # Cập nhật
    df.loc[mask, 'ten'] = ten_moi
    # Đảm bảo cột 'mota' tồn tại
    if 'mota' not in df.columns:
        df['mota'] = ''
    df.loc[mask, 'mota'] = mota_moi
    save_information_fields(df)
    # Lấy mã loại VB của trường này để đánh dấu các hồ sơ liên quan
    try:
        ma_loai_vb = df.loc[mask, 'ma_loai_van_ban'].iloc[0]
        mark_records_need_request(str(ma_loai_vb))
    except Exception:
        pass
    return True, "Cập nhật trường thông tin thành công!"

# Hàm thêm trường thông tin mới
def add_information_field(ma, ten, mota, loai_van_ban, ma_loai_van_ban, thu_tu, kieu_nhap):
    df = load_information_fields()
    
    # Kiểm tra mã đã tồn tại
    if ma in df['ma'].values:
        return False, "Mã danh mục đã tồn tại!"
    
    # Thêm dòng mới
    new_row = pd.DataFrame({
        'ma': [ma],
        'ten': [ten],
    'mota': [mota if mota is not None else ten],
        'loai_van_ban': [loai_van_ban],
        'ma_loai_van_ban': [ma_loai_van_ban],
        'thu_tu': [thu_tu],
        'kieu_nhap': [kieu_nhap]
    })
    df = pd.concat([df, new_row], ignore_index=True)
    
    # Lưu vào CSV
    save_information_fields(df)
    # Đánh dấu các hồ sơ của mã loại văn bản này cần re-request
    try:
        mark_records_need_request(str(ma_loai_van_ban))
    except Exception:
        pass
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
        # Lấy danh sách loại văn bản từ CSV (đưa lên hàng trên)
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

    # Hàng dưới: ô Mô tả riêng
    d1, = st.columns([1])
    with d1:
        mota = st.text_input("Mô tả", placeholder="Mô tả hiển thị trong schema", key="mota_input")
    
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
            success, message = add_information_field(ma, ten, mota, loai_van_ban, ma_loai_van_ban, thu_tu, kieu_nhap)
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
header_col1, header_col2, header_col2b, header_col3, header_col4, header_col5, header_col6 = st.columns([1, 1, 2, 2, 1, 2, 1])
with header_col1:
    st.markdown("**Mã**")
with header_col2:
    st.markdown("**Tên**")
with header_col2b:
    st.markdown("**Mô tả**")
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
    # Khởi tạo trạng thái chỉnh sửa
    if 'edit_field_ma' not in st.session_state:
        st.session_state['edit_field_ma'] = None

    for index, row in filtered_df.iterrows():
        col1, col2, col2b, col3, col4, col5, col6 = st.columns([1, 1, 2, 2, 1, 2, 1])

        ma_row = row['ma']
        is_editing = st.session_state.get('edit_field_ma') == ma_row
        mota_val = None
        try:
            mota_val = row.get('mota') if hasattr(row, 'get') else row['mota']
        except Exception:
            mota_val = ""

        with col1:
            st.write(f"**{ma_row}**")

        with col2:
            if is_editing:
                st.text_input(
                    "Tên",
                    value=str(row['ten']) if pd.notna(row['ten']) else "",
                    key=f"edit_ten_{ma_row}",
                    label_visibility="collapsed",
                )
            else:
                st.write(row['ten'])

        with col2b:
            if is_editing:
                st.text_input(
                    "Mô tả",
                    value=str(mota_val) if mota_val is not None and pd.notna(mota_val) else "",
                    key=f"edit_mota_{ma_row}",
                    label_visibility="collapsed",
                )
            else:
                st.write(mota_val or "")

        with col3:
            st.write(row['loai_van_ban'])

        with col4:
            st.write(row['thu_tu'])

        with col5:
            st.write(row['kieu_nhap'])

        with col6:
            if is_editing:
                b1, b2 = st.columns([1, 1])
                with b1:
                    if st.button("Lưu", key=f"save_{ma_row}", type="primary"):
                        ten_new = st.session_state.get(f"edit_ten_{ma_row}", "")
                        mota_new = st.session_state.get(f"edit_mota_{ma_row}", "")
                        ok, msg = update_information_field(ma_row, ten_new, mota_new)
                        if ok:
                            st.session_state['edit_field_ma'] = None
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                with b2:
                    if st.button("Hủy", key=f"cancel_{ma_row}", type="secondary"):
                        st.session_state['edit_field_ma'] = None
                        st.rerun()
            else:
                # Hai nút Sửa/Xóa cùng hàng
                b1, b2 = st.columns([1, 1])
                with b1:
                    if st.button("Sửa", key=f"edit_{ma_row}"):
                        st.session_state['edit_field_ma'] = ma_row
                        # Prefill handled by default values in inputs
                        st.rerun()
                with b2:
                    if st.button("Xóa", key=f"delete_{ma_row}", type="secondary"):
                        delete_information_field(ma_row)
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
