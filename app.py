import streamlit as st
import pandas as pd
import time
from io import BytesIO
import base64
from PIL import Image

def call_ocr_api(pdf_file):
    """Hàm giả lập gọi API OCR"""
    time.sleep(3)
    mock_response = {
        "status": "success",
        "data": {
            "invoice_id": "INV-2023-123",
            "customer_name": "Công ty TNHH ABC",
            "address": "123 Đường XYZ, Quận 1, TP. HCM",
            "total_amount": "15.000.000 VND",
            "items": [
                {
                    "description": "Sản phẩm A",
                    "quantity": 2,
                    "price": "5.000.000 VND",
                },
                {
                    "description": "Sản phẩm B",
                    "quantity": 1,
                    "price": "5.000.000 VND",
                },
            ],
        },
        "processing_time": "2.5s",
    }
    return mock_response

@st.dialog("Thêm mới hồ sơ", width="small")
def show_modal():
    st.write("Thêm mới hồ sơ")
    
    # Load document types from CSV
    def load_document_types():
        import os
        csv_path = "data/document_types.csv"
        if os.path.exists(csv_path):
            try:
                df = pd.read_csv(csv_path)
                return df
            except:
                return pd.DataFrame()
        return pd.DataFrame()
    
    # Load document types
    doc_types_df = load_document_types()
    
    if not doc_types_df.empty:
        # Create options list with format: "ten_loai (ma_loai)"
        doc_type_options = []
        doc_type_mapping = {}  # Map display name to ma_loai
        
        for _, row in doc_types_df.iterrows():
            display_name = f"{row['ten_loai']} ({row['ma_loai']})"
            doc_type_options.append(display_name)
            doc_type_mapping[display_name] = row['ma_loai']
        
        selected_display = st.selectbox("Chọn loại hồ sơ", doc_type_options)
        doc_type_code = doc_type_mapping.get(selected_display, "")
        doc_type_name = selected_display.split(" (")[0] if selected_display else ""
    else:
        st.warning("Chưa có loại văn bản nào được định nghĩa!")
        doc_type_code = ""
        doc_type_name = ""
        selected_display = ""

    uploaded_file = st.file_uploader(
        "Chọn một tệp PDF để trích xuất thông tin", type="pdf"
    )

    if uploaded_file is not None:
        pdf_bytes = uploaded_file.getvalue()
        pdf_file_object = BytesIO(pdf_bytes)
        pdf_file_object.name = uploaded_file.name

        if st.button("Bắt đầu trích xuất và Lưu"):
            # Kiểm tra đã chọn loại văn bản chưa
            if not doc_type_code:
                st.error("Vui lòng chọn loại văn bản trước khi upload!")
                return
                
            try:
                # Tạo thư mục data/pdf nếu chưa tồn tại
                import os
                pdf_dir = "data/pdf"
                if not os.path.exists(pdf_dir):
                    os.makedirs(pdf_dir)
                
                # Tạo tên file duy nhất để tránh trùng lặp
                file_name = uploaded_file.name
                base_name, ext = os.path.splitext(file_name)
                counter = 1
                while os.path.exists(os.path.join(pdf_dir, file_name)):
                    file_name = f"{base_name}_{counter}{ext}"
                    counter += 1
                
                # Lưu file PDF vào thư mục data/pdf
                file_path = os.path.join(pdf_dir, file_name)
                with open(file_path, "wb") as f:
                    f.write(pdf_bytes)
                
                # Gọi OCR giả lập
                ocr_result = call_ocr_api(pdf_file_object)

                # Thêm hồ sơ mới vào CSV và session
                new_stt = add_record(file_name, doc_type_code, doc_type_name, file_path)
                
                # Cập nhật session state
                st.session_state['data'] = load_records()

                # Lưu kết quả OCR và thông tin file vào session (key: STT)
                st.session_state['ocr_results'][new_stt] = {
                    "ocr_data": ocr_result,
                    "pdf_bytes": base64.b64encode(pdf_bytes).decode('utf-8'),
                    "doc_type": doc_type_name,
                    "doc_type_code": doc_type_code,
                    "file_name": file_name,
                    "file_path": file_path  # Lưu đường dẫn file vật lý
                }

                st.success(f"Đã thêm hồ sơ mới và xử lý OCR thành công! Loại văn bản: {doc_type_name} (Mã: {doc_type_code}) - File đã được lưu tại: {file_path}")
                st.rerun()
                
            except Exception as e:
                st.error(f"Lỗi khi lưu file: {str(e)}")

    if st.button("Hủy"):
        pass

# Giao diện trang chính
st.set_page_config(layout="wide", page_title="Trang Chính - Table")

# Hide Streamlit's default pages navigation (the auto-generated multipage list)
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
st.markdown("""
<div class="breadcrumb-container">
    <span class="breadcrumb-item"> Trang chủ</span>
    <span class="breadcrumb-separator">/</span>
    <span class="breadcrumb-current">Số hóa tài liệu</span>
</div>
""", unsafe_allow_html=True)


# # --- Sidebar header với logo -------------------------------------------------
# try:
#     sidebar_logo_path = "data/logo-toa-an-nhan-dan-toi-cao.png"
#     sidebar_logo_img = Image.open(sidebar_logo_path)
#     st.sidebar.image(sidebar_logo_img, width=100)
# except Exception:
#     st.sidebar.markdown("### 🏛️")

# st.sidebar.markdown("---")

# --- Sidebar hierarchical menu (custom, at top, no page nav) ---------
st.sidebar.markdown("## Menu")
with st.sidebar.expander("SỐ HÓA HỒ SƠ TÀI LIỆU", expanded=True):
    # Kiểm tra session state để chọn menu item đúng
    default_index = 0
    if 'menu_choice' in st.session_state:
        if st.session_state['menu_choice'] == "Quản lý danh mục trường thông tin":
            default_index = 1
        elif st.session_state['menu_choice'] == "Quản lý loại văn bản":
            default_index = 2
    
    menu_choice = st.radio(
        "Chọn chức năng",
        ["Số hóa tài liệu", "Quản lý danh mục trường thông tin", "Quản lý loại văn bản"],
        index=default_index,
        key="menu_choice",
        label_visibility="collapsed"
    )
    
    # Reset session state sau khi đã sử dụng
    if 'menu_choice' in st.session_state:
        del st.session_state['menu_choice']

# Xử lý chuyển trang từ menu
if menu_choice == "Quản lý danh mục trường thông tin":
    st.switch_page("pages/information_fields.py")
elif menu_choice == "Quản lý loại văn bản":
    st.switch_page("pages/document_types.py")


# Hàm load danh sách hồ sơ từ CSV
def load_records():
    import os
    csv_path = "data/records.csv"
    if os.path.exists(csv_path):
        try:
            return pd.read_csv(csv_path)
        except:
            return pd.DataFrame(columns=["STT", "Tên File", "THỜI GIAN TẢI LÊN", "TRẠNG THÁI DỮ LIỆU", "LOẠI HỒ SƠ", "MA_LOAI"])
    else:
        return pd.DataFrame(columns=["STT", "Tên File", "THỜI GIAN TẢI LÊN", "TRẠNG THÁI DỮ LIỆU", "LOẠI HỒ SƠ", "MA_LOAI"])

# Hàm lưu danh sách hồ sơ vào CSV
def save_records(df):
    import os
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    csv_path = os.path.join(data_dir, "records.csv")
    df.to_csv(csv_path, index=False)

# Hàm thêm hồ sơ mới
def add_record(file_name, doc_type_code, doc_type_name, file_path):
    df = load_records()
    
    # Tạo STT mới
    if df.empty:
        new_stt = 1
    else:
        new_stt = df['STT'].max() + 1
    
    # Thêm dòng mới
    new_row = pd.DataFrame({
        "STT": [new_stt],
        "Tên File": [file_name],
        "THỜI GIAN TẢI LÊN": [time.strftime("%m/%d/%y %H:%M:%S")],
        "TRẠNG THÁI DỮ LIỆU": ["Complete"],
        "LOẠI HỒ SƠ": [doc_type_name],  # Hiển thị tên cho người dùng
        "MA_LOAI": [doc_type_code]      # Lưu mã để mapping
    })
    
    df = pd.concat([df, new_row], ignore_index=True)
    save_records(df)
    
    return new_stt

# Khởi tạo session state
if 'data' not in st.session_state:
    st.session_state['data'] = load_records()

if 'ocr_results' not in st.session_state:
    st.session_state['ocr_results'] = {}


# Main content switches based on menu selection
if menu_choice == "Số hóa tài liệu":
    # Upload section
    col_u1, col_u2, col_u3 = st.columns([6, 2, 2])
    with col_u1:
        search_query = st.text_input("Nhập số ID, BGD, tên tài liệu, hoặc tên việc", placeholder="Tìm kiếm...")
    with col_u2:
        st.write("")  # Spacer
    with col_u3:
        if st.button("Upload", type="primary"):
            show_modal()

    # Load dữ liệu từ CSV mỗi lần
    records_df = load_records()
    
    # Filter data based on search query
    filtered_data = records_df
    if search_query:
        filtered_data = records_df[
            records_df.apply(
                lambda row: search_query.lower() in str(row).lower(), axis=1
            )
        ]

    # Display table
    st.markdown("<h3>Danh sách hồ sơ</h3>", unsafe_allow_html=True)

    # Table header
    hdr_col1, hdr_col2, hdr_col3, hdr_col4, hdr_col5, hdr_col6 = st.columns([0.5, 2.5, 1, 2, 1.5, 1])
    with hdr_col1:
        st.markdown("**STT**")
    with hdr_col2:
        st.markdown("**Tên File**")
    with hdr_col3:
        st.markdown("**Loại hồ sơ**")
    with hdr_col4:
        st.markdown("**Thời gian tải lên**")
    with hdr_col5:
        st.markdown("**Trạng thái OCR**")
    with hdr_col6:
        st.markdown("**Thao tác**")

    st.markdown("---")

    # Table data
    if not filtered_data.empty:
        for index, row in filtered_data.iterrows():
            col1, col2, col3, col4, col5, col6 = st.columns([0.5, 2.5, 1, 2, 1.5, 1])
            with col1:
                st.write(f"**{row['STT']}**")
            with col2:
                st.write(row['Tên File'])
            with col3:
                st.write(row['LOẠI HỒ SƠ'])
            with col4:
                st.write(row['THỜI GIAN TẢI LÊN'])
            with col5:
                # Hiển thị trạng thái với màu sắc
                if row['TRẠNG THÁI DỮ LIỆU'] == "Complete":
                    st.success("✅ Complete")
                else:
                    st.warning("⏳ Processing")
            with col6:
                if st.button("View", key=f"view_{row['STT']}", type="secondary"):
                    st.session_state['selected_id'] = row['STT']
                    # Cập nhật URL với ID để hỗ trợ F5 refresh
                    try:
                        st.query_params['id'] = str(row['STT'])
                    except:
                        pass
                    st.switch_page("pages/document_detail.py")
            
            if index < len(filtered_data) - 1:  # Không hiển thị divider cho dòng cuối
                st.divider()
        
        # Hiển thị thông tin số lượng kết quả
        if search_query:
            st.info(f"Tìm thấy {len(filtered_data)} kết quả cho từ khóa: '{search_query}'")
        else:
            st.info(f"Hiển thị tất cả {len(filtered_data)} hồ sơ")
    else:
        if search_query:
            st.warning(f"Không tìm thấy kết quả nào cho từ khóa: '{search_query}'")
        else:
            st.info("Chưa có hồ sơ nào. Hãy upload file đầu tiên!")

elif menu_choice == "Quản lý danh mục trường thông tin":
    st.switch_page("pages/information_fields.py")

elif menu_choice == "Quản lý loại văn bản":
    st.markdown("<h3>Quản lý loại văn bản</h3>", unsafe_allow_html=True)
    
    # Hiển thị thông tin và nút chuyển trang
    st.info("Chức năng quản lý loại văn bản cho phép bạn thêm, sửa, xóa các loại văn bản trong hệ thống.")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("Mở trang quản lý loại văn bản", type="primary"):
            st.switch_page("pages/document_types.py")
    
    # Hiển thị danh sách loại văn bản hiện tại từ CSV
    try:
        import os
        csv_path = "data/document_types.csv"
        if os.path.exists(csv_path):
            doc_types_df = pd.read_csv(csv_path)
            st.markdown("<h4>Danh sách loại văn bản hiện tại</h4>", unsafe_allow_html=True)
            
            # Hiển thị bảng
            st.dataframe(doc_types_df, use_container_width=True, hide_index=True)
        else:
            st.warning("Chưa có dữ liệu loại văn bản. Hãy tạo dữ liệu đầu tiên!")
    except Exception as e:
        st.error(f"Lỗi khi đọc dữ liệu: {str(e)}")