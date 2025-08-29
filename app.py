import streamlit as st
import pandas as pd
import time
import threading
import traceback
from io import BytesIO
import base64
from PIL import Image
import requests
import json
import os

def load_information_fields():
    """Load danh sách trường thông tin từ CSV"""
    csv_path = "data/information_fields.csv"
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            # Ensure backward compatibility: if 'mota' (description) column is missing, derive from 'ten'
            if 'mota' not in df.columns:
                try:
                    df['mota'] = df['ten'] if 'ten' in df.columns else ""
                except Exception:
                    df['mota'] = ""
            return df
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def create_schema_from_fields(doc_type_code, doc_type_name=None):
    """Tạo schema JSON từ information_fields dựa trên loại văn bản
    If doc_type_name is supplied, it's used as the schema title.
    """
    fields_df = load_information_fields()
    
    if fields_df.empty:
        return {}
    
    # Lọc các trường theo loại văn bản
    filtered_fields = fields_df[fields_df['ma_loai_van_ban'] == doc_type_code]
    
    title = doc_type_name if doc_type_name else "Vietnamese Legal Document"
    schema = {
        "title": title,
        "type": "object",
        "properties": {}
    }
    
    for _, field in filtered_fields.iterrows():
        field_name = field['ma']
        # Use 'mota' (mô tả) as the description if available; fallback to 'ten' for compatibility
        field_description = None
        try:
            field_description = field.get('mota') if hasattr(field, 'get') else field['mota']
        except Exception:
            pass
        if not field_description or (isinstance(field_description, float) and pd.isna(field_description)):
            try:
                field_description = field['ten']
            except Exception:
                field_description = ""

        schema["properties"][field_name] = {
            "type": "string",
            "description": field_description
        }
    
    return schema


def safe_rerun():
    """Force a reliable rerun across Streamlit versions.
    Tries st.rerun() first, then experimental_rerun, then raises RerunException properly.
    """
    # Preferred API in newer Streamlit
    if hasattr(st, 'rerun'):
        st.rerun()
        return
    # Back-compat API
    if hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()
        return
    # Lowest-level fallback: raise RerunException with RerunData
    try:
        from streamlit.runtime.scriptrunner import RerunException, RerunData
        raise RerunException(RerunData(widget_states=None))
    except Exception:
        # Last resort: stop; user can manually refresh
        st.stop()

def call_ocr_api(pdf_file, doc_type_code, doc_type_name=None):
    """Gọi API OCR thật
    doc_type_name (optional) will be used as schema title when provided.
    """
    try:
        # Tạo schema từ information fields
        schema = create_schema_from_fields(doc_type_code, doc_type_name)
        
        if not schema.get('properties'):
            st.warning(f"Không tìm thấy trường thông tin cho loại văn bản: {doc_type_code}")
            return {"status": "error", "message": "Không có schema"}
        
        # Chuẩn bị file và payload
        files = {
            'file': (pdf_file.name, pdf_file.getvalue(), 'application/pdf')
        }
        
        data = {
            'schema': json.dumps(schema),
            'strategy': 'vision_llm',
            'use_embedding': 'true'
        }
        
        # Gọi API
        response = requests.post(
            'http://192.168.1.28:1111/api/extract',
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            return {
                "status": "success",
                "data": response.json(),
                "processing_time": "API call completed"
            }
        else:
            return {
                "status": "error",
                "message": f"API returned status code: {response.status_code}",
                "data": response.text
            }
            
    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "message": "Cannot connect to API server at 192.168.1.28:1111"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"API call failed: {str(e)}"
        }


# Background worker control
BACKGROUND_WORKER_LOCK = threading.Lock()
BACKGROUND_WORKER_RUNNING = False


def background_worker_loop(poll_interval=1.0):
    """Background worker that processes records with status 'Pending' sequentially.
    It reads `data/records.csv`, finds the oldest Pending record, marks it Processing,
    calls the OCR API, saves API data and updates the record status.
    """
    global BACKGROUND_WORKER_RUNNING
    try:
        while True:
            # Load records and find the first pending
            records_df = load_records()
            pending = records_df[records_df['TRẠNG THÁI DỮ LIỆU'] == 'Pending']
            if pending.empty:
                break

            # Process the oldest pending (smallest STT)
            pending = pending.sort_values('STT')
            row = pending.iloc[0]
            stt = int(row['STT'])
            file_name = row['Tên File']
            doc_type_code = row.get('MA_LOAI', '')
            doc_type_name = row.get('LOẠI HỒ SƠ', '')
            file_path = row.get('MA_LOAI')

            # Determine file path from records (prefer explicit file path in data/pdf)
            pdf_path = os.path.join('data', 'pdf', file_name)
            if not os.path.exists(pdf_path):
                # try stored path in session or alternate
                # if file missing, mark as Error
                update_record_status(stt, 'Error')
                add_api_data(stt, {"status": "error", "message": f"File not found: {pdf_path}"})
                continue

            # Mark as Processing
            update_record_status(stt, 'Processing')

            # Read file bytes
            try:
                with open(pdf_path, 'rb') as f:
                    pdf_bytes = f.read()
                pdf_file_object = BytesIO(pdf_bytes)
                pdf_file_object.name = file_name

                # Call OCR API
                ocr_result = call_ocr_api(pdf_file_object, doc_type_code, doc_type_name)

                # Save API data and update status
                add_api_data(stt, ocr_result)
                if ocr_result.get('status') == 'success':
                    update_record_status(stt, 'Complete')
                else:
                    update_record_status(stt, 'Error')

            except Exception as e:
                # On unexpected error mark as Error and log
                try:
                    update_record_status(stt, 'Error')
                    add_api_data(stt, {"status": "error", "message": str(e)})
                except Exception:
                    pass

            # Small pause to avoid tight loop
            time.sleep(poll_interval)

    except Exception:
        traceback.print_exc()
    finally:
        with BACKGROUND_WORKER_LOCK:
            BACKGROUND_WORKER_RUNNING = False


def start_background_worker():
    """Start the background worker in a new daemon thread if not already running."""
    global BACKGROUND_WORKER_RUNNING
    with BACKGROUND_WORKER_LOCK:
        if BACKGROUND_WORKER_RUNNING:
            return
        BACKGROUND_WORKER_RUNNING = True

    t = threading.Thread(target=background_worker_loop, daemon=True)
    t.start()

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

    uploaded_files = st.file_uploader(
        "Chọn một hoặc nhiều tệp PDF để trích xuất thông tin", type="pdf", accept_multiple_files=True
    )

    if uploaded_files:
        if st.button("Bắt đầu trích xuất và Lưu"):
            # Kiểm tra đã chọn loại văn bản chưa
            if not doc_type_code:
                st.error("Vui lòng chọn loại văn bản trước khi upload!")
                return

            pdf_dir = "data/pdf"
            try:
                if not os.path.exists(pdf_dir):
                    os.makedirs(pdf_dir)

                added = []
                for uploaded_file in uploaded_files:
                    try:
                        pdf_bytes = uploaded_file.getvalue()
                        # Tạo tên file duy nhất nếu trùng
                        file_name = uploaded_file.name
                        base_name, ext = os.path.splitext(file_name)
                        counter = 1
                        while os.path.exists(os.path.join(pdf_dir, file_name)):
                            file_name = f"{base_name}_{counter}{ext}"
                            counter += 1

                        # Lưu file
                        file_path = os.path.join(pdf_dir, file_name)
                        with open(file_path, "wb") as f:
                            f.write(pdf_bytes)

                        # Thêm hồ sơ mới vào CSV với trạng thái Pending
                        new_stt = add_record(file_name, doc_type_code, doc_type_name, file_path, status="Pending")

                        # Thêm placeholder vào session ocr_results so UI can reference it
                        st.session_state['ocr_results'][new_stt] = {
                            "ocr_data": None,
                            "pdf_bytes": base64.b64encode(pdf_bytes).decode('utf-8'),
                            "doc_type": doc_type_name,
                            "doc_type_code": doc_type_code,
                            "file_name": file_name,
                            "file_path": file_path
                        }

                        added.append(new_stt)
                    except Exception as e:
                        st.error(f"Lỗi khi lưu file {uploaded_file.name}: {e}")

                # Refresh data shown in UI
                st.session_state['data'] = load_records()

                if added:
                    st.success(f"Đã upload {len(added)} file. Chúng sẽ được xử lý tuần tự trong nền.")
                    # Start background worker to process pending items
                    start_background_worker()
                    safe_rerun()

            except Exception as e:
                st.error(f"Lỗi khi tạo thư mục lưu PDF: {e}")

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

    .st-emotion-cache-wfksaw {justify-content: end !important;}
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
    
    /* Căn giữa nút View theo chiều cao nhưng không kéo giãn toàn hàng */
    .stButton > button[data-testid="baseButton-secondary"] {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: auto !important;
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
st.markdown("<h2 style='margin:0'>DEMO SỐ HÓA TÀI LIỆU</h2>", unsafe_allow_html=True)

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
    # Backward-compat: chuyển các key/giá trị cũ sang schema & tên mới
    if 'menu_choice' in st.session_state:
        legacy = st.session_state['menu_choice']
        if legacy in ("Quản lý danh mục trường thông tin", "Quản lý loại văn bản"):
            st.session_state['main_menu'] = "Quản lý danh mục trường thông tin"
            # map tên cũ -> mới cho submenu
            st.session_state['manage_choice'] = (
                "Danh mục trường thông tin" if legacy == "Quản lý danh mục trường thông tin" else "Loại văn bản"
            )
        else:
            st.session_state['main_menu'] = "Số hóa tài liệu"
        del st.session_state['menu_choice']

    # Nếu còn lưu giá trị cũ trong main_menu / manage_choice thì migrate
    if st.session_state.get('main_menu') == 'Quản lý':
        st.session_state['main_menu'] = 'Quản lý danh mục trường thông tin'
    if st.session_state.get('manage_choice') == 'Quản lý danh mục trường thông tin':
        st.session_state['manage_choice'] = 'Danh mục trường thông tin'
    if st.session_state.get('manage_choice') == 'Quản lý loại văn bản':
        st.session_state['manage_choice'] = 'Loại văn bản'

    # Main level
    main_default = 0 if st.session_state.get('main_menu', 'Số hóa tài liệu') == 'Số hóa tài liệu' else 1
    main_menu = st.radio(
        "Chọn chức năng",
        ["Số hóa tài liệu", "Quản lý danh mục trường thông tin"],
        index=main_default,
        key="main_menu",
        label_visibility="collapsed",
    )

    # Sub level for Quản lý (đổi nhãn và item)
    manage_choice = None
    if main_menu == "Quản lý danh mục trường thông tin":
        manage_default = 0 if st.session_state.get('manage_choice', 'Danh mục trường thông tin') == 'Danh mục trường thông tin' else 1
        # nhãn phụ để tạo cảm giác phân cấp
        st.markdown("<div style='margin: 4px 0 6px 6px; color:#6c757d;'>— Quản lý danh mục trường thông tin</div>", unsafe_allow_html=True)
        manage_choice = st.radio(
            "Quản lý danh mục trường thông tin",
            ["Danh mục trường thông tin", "Loại văn bản"],
            index=manage_default,
            key="manage_choice",
            label_visibility="collapsed",
        )

# Xử lý chuyển trang từ menu mới
if st.session_state.get('main_menu') == "Quản lý danh mục trường thông tin":
    if st.session_state.get('manage_choice') == "Danh mục trường thông tin":
        st.switch_page("pages/information_fields.py")
    elif st.session_state.get('manage_choice') == "Loại văn bản":
        st.switch_page("pages/document_types.py")


# Hàm load danh sách hồ sơ từ CSV
def load_records():
    import os
    csv_path = "data/records.csv"
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            # Ensure 'isrequest' column exists (0: hidden, 1: show Request)
            if 'isrequest' not in df.columns:
                df['isrequest'] = 0
            return df
        except:
            return pd.DataFrame(columns=["STT", "Tên File", "THỜI GIAN TẢI LÊN", "TRẠNG THÁI DỮ LIỆU", "LOẠI HỒ SƠ", "MA_LOAI", "isrequest"])
    else:
        return pd.DataFrame(columns=["STT", "Tên File", "THỜI GIAN TẢI LÊN", "TRẠNG THÁI DỮ LIỆU", "LOẠI HỒ SƠ", "MA_LOAI", "isrequest"])

# Hàm load dữ liệu API từ CSV
def load_api_data():
    import os
    csv_path = "data/records_api_data.csv"
    if os.path.exists(csv_path):
        try:
            return pd.read_csv(csv_path)
        except:
            return pd.DataFrame(columns=["record_id", "api_response"])
    else:
        return pd.DataFrame(columns=["record_id", "api_response"])

# Hàm lưu dữ liệu API vào CSV
def save_api_data(df):
    import os
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    csv_path = os.path.join(data_dir, "records_api_data.csv")
    df.to_csv(csv_path, index=False)

# Hàm thêm kết quả API mới
def add_api_data(record_id, api_response):
    df = load_api_data()
    
    # Chuyển đổi API response thành JSON string để lưu trong CSV
    api_response_json = json.dumps(api_response, ensure_ascii=False)
    
    # Kiểm tra xem record_id đã tồn tại chưa
    if record_id in df['record_id'].values:
        # Cập nhật dữ liệu cũ
        df.loc[df['record_id'] == record_id, 'api_response'] = api_response_json
    else:
        # Thêm dòng mới
        new_row = pd.DataFrame({
            "record_id": [record_id],
            "api_response": [api_response_json]
        })
        df = pd.concat([df, new_row], ignore_index=True)
    
    save_api_data(df)
    return True

# Hàm lấy dữ liệu API theo record_id
def get_api_data(record_id):
    df = load_api_data()
    
    if record_id in df['record_id'].values:
        api_response_json = df.loc[df['record_id'] == record_id, 'api_response'].iloc[0]
        try:
            return json.loads(api_response_json)
        except:
            return None
    return None

# Hàm lưu danh sách hồ sơ vào CSV
def save_records(df):
    import os
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    csv_path = os.path.join(data_dir, "records.csv")
    df.to_csv(csv_path, index=False)

# Hàm thêm hồ sơ mới
def add_record(file_name, doc_type_code, doc_type_name, file_path, status="Complete"):
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
        "TRẠNG THÁI DỮ LIỆU": [status],
        "LOẠI HỒ SƠ": [doc_type_name],  # Hiển thị tên cho người dùng
        "MA_LOAI": [doc_type_code],      # Lưu mã để mapping
        "isrequest": [0]                 # 0: không hiển thị Request, 1: hiển thị
    })
    
    df = pd.concat([df, new_row], ignore_index=True)
    save_records(df)
    
    return new_stt

# Hàm cập nhật trạng thái hồ sơ
def update_record_status(stt, new_status):
    df = load_records()
    
    # Tìm và cập nhật dòng có STT tương ứng
    mask = df['STT'] == stt
    if mask.any():
        df.loc[mask, 'TRẠNG THÁI DỮ LIỆU'] = new_status
        save_records(df)
        return True
    return False

# Hàm cập nhật cờ isrequest cho một hồ sơ
def update_record_isrequest(stt, flag):
    df = load_records()
    mask = df['STT'] == stt
    if mask.any():
        df.loc[mask, 'isrequest'] = int(1 if flag else 0)
        save_records(df)
        return True
    return False

# Khởi tạo session state
if 'data' not in st.session_state:
    st.session_state['data'] = load_records()

if 'ocr_results' not in st.session_state:
    st.session_state['ocr_results'] = {}

# Load lại dữ liệu API từ CSV vào session state
def sync_api_data_to_session():
    """Đồng bộ dữ liệu API từ CSV vào session state"""
    api_df = load_api_data()
    
    for _, row in api_df.iterrows():
        record_id = row['record_id']
        try:
            api_data = json.loads(row['api_response'])
            
            # Kiểm tra xem record_id có tồn tại trong records.csv không
            records_df = load_records()
            record_exists = record_id in records_df['STT'].values
            
            if record_exists and record_id not in st.session_state['ocr_results']:
                # Lấy thông tin từ records.csv
                record_info = records_df[records_df['STT'] == record_id].iloc[0]
                
                st.session_state['ocr_results'][record_id] = {
                    "ocr_data": api_data,
                    "pdf_bytes": "",  # Sẽ được load khi cần
                    "doc_type": record_info['LOẠI HỒ SƠ'],
                    "doc_type_code": record_info['MA_LOAI'],
                    "file_name": record_info['Tên File'],
                    "file_path": f"data/pdf/{record_info['Tên File']}"
                }
        except:
            continue

# Đồng bộ dữ liệu khi khởi tạo
sync_api_data_to_session()

# Start background worker if there are Pending items
try:
    records_start = load_records()
    if not records_start[records_start['TRẠNG THÁI DỮ LIỆU'] == 'Pending'].empty:
        start_background_worker()
except Exception:
    pass


# Main content chỉ hiển thị khi ở mục "Số hóa tài liệu"
if st.session_state.get('main_menu', 'Số hóa tài liệu') == "Số hóa tài liệu":
    # Upload section
    col_u1, col_u3 = st.columns([8, 2])
    with col_u1:
        search_query = st.text_input("Nhập số ID, BGD, tên tài liệu, hoặc tên việc", placeholder="Tìm kiếm...")

    with col_u3:
        if st.button("Upload", type="primary"):
            show_modal()

    # Load dữ liệu từ CSV mỗi lần
    records_df = load_records()

    # --- Filters and pagination controls ---------------------------------
    # Load document types for filter options
    doc_type_options = ["Tất cả"]
    try:
        dt_path = os.path.join('data', 'document_types.csv')
        if os.path.exists(dt_path):
            dt_df = pd.read_csv(dt_path)
            if 'ten_loai' in dt_df.columns:
                opts = dt_df['ten_loai'].astype(str).tolist()
                # keep unique while preserving order
                seen = set()
                for v in opts:
                    if v not in seen:
                        seen.add(v)
                        doc_type_options.append(v)
    except Exception:
        pass
    fcol1, fcol2, fcol3, fcol4 = st.columns([3, 2, 2, 1.2])
    with fcol1:
        sort_order = st.selectbox("Sắp xếp theo ngày", ["D - Mới → Cũ", "A - Cũ → Mới"], index=0, key='sort_order')
    with fcol2:
        doc_type_filter = st.selectbox("Lọc loại văn bản", doc_type_options, index=0, key='filter_doc_type')
    with fcol3:
        # status filter options from records
        status_opts = ["Tất cả"]
        try:
            if 'TRẠNG THÁI DỮ LIỆU' in records_df.columns:
                for s in records_df['TRẠNG THÁI DỮ LIỆU'].astype(str).unique():
                    if s not in status_opts:
                        status_opts.append(s)
        except Exception:
            pass
        status_filter = st.selectbox("Lọc trạng thái OCR", status_opts, index=0, key='filter_status')
    with fcol4:
        page_size = st.selectbox("Số hàng / trang", [10, 20, 50, 100], index=3, key='page_size')

    # Reset page when filters change
    prev_key = 'prev_filters'
    current_filters = (sort_order, doc_type_filter, status_filter, page_size)
    if st.session_state.get(prev_key) != current_filters:
        st.session_state['page'] = 1
        st.session_state[prev_key] = current_filters

    # Filter data based on search query and selected doc type/status
    filtered_data = records_df
    if search_query:
        filtered_data = filtered_data[
            filtered_data.apply(
                lambda row: search_query.lower() in str(row).lower(), axis=1
            )
        ]

    if doc_type_filter and doc_type_filter != "Tất cả":
        filtered_data = filtered_data[filtered_data['LOẠI HỒ SƠ'] == doc_type_filter]

    if status_filter and status_filter != "Tất cả":
        filtered_data = filtered_data[filtered_data['TRẠNG THÁI DỮ LIỆU'] == status_filter]

    # Ensure timestamp column parsed for sorting
    if 'THỜI GIAN TẢI LÊN' in filtered_data.columns:
        filtered_data = filtered_data.copy()
        filtered_data['__ts'] = pd.to_datetime(filtered_data['THỜI GIAN TẢI LÊN'], format="%m/%d/%y %H:%M:%S", errors='coerce')
        ascending = True if sort_order.startswith('A') else False
        filtered_data = filtered_data.sort_values('__ts', ascending=ascending)
        # remove helper column later

    # Pagination
    total_rows = len(filtered_data)
    page = int(st.session_state.get('page', 1))
    page_size = int(page_size)
    total_pages = max(1, (total_rows + page_size - 1) // page_size)
    if page > total_pages:
        page = total_pages
        st.session_state['page'] = page

    start = (page - 1) * page_size
    end = start + page_size
    page_data = filtered_data.iloc[start:end]

    # Display table
    st.markdown("<h3>Danh sách hồ sơ</h3>", unsafe_allow_html=True)

    # Table header
    hdr_col1, hdr_col2, hdr_col3, hdr_col4, hdr_col5, hdr_col6 = st.columns([0.5, 3, 1, 1, 1.5, 1.5])
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

    # Table data (paginated)
    if not page_data.empty:
        # Reset index so row indices are 0..n-1 within the current page
        page_rows = page_data.reset_index(drop=True)
        for i, row in page_rows.iterrows():
            col1, col2, col3, col4, col5, col6 = st.columns([0.5, 3, 1, 1, 1.5, 1.5])
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
                elif row['TRẠNG THÁI DỮ LIỆU'] == "Pending":
                    st.warning("⏳ Pending")
                elif row['TRẠNG THÁI DỮ LIỆU'] == "Error":
                    st.error("❌ Error")
                else:
                    st.warning("⏳ Processing")
            with col6:
                # Bố trí hai nút cùng một hàng trong cột Thao tác
                bcol1, bcol2 = st.columns([1, 1])
                with bcol1:
                    # Chỉ hiển thị nút Request khi isrequest = 1 và không Pending/Processing
                    try:
                        isreq = int(row.get('isrequest', 0))
                    except Exception:
                        isreq = 0
                    state = str(row['TRẠNG THÁI DỮ LIỆU'])
                    can_request = (isreq == 1) and (state not in ["Pending", "Processing"])
                    if can_request:
                        if st.button("Request", key=f"request_{row['STT']}"):
                            try:
                                stt = int(row['STT'])
                                file_name = str(row['Tên File'])
                                pdf_path = os.path.join('data', 'pdf', file_name)
                                if not os.path.exists(pdf_path):
                                    st.error(f"Không tìm thấy file PDF đã lưu: {pdf_path}")
                                else:
                                    # Đánh dấu hồ sơ cần xử lý và reset cờ yêu cầu (đã request)
                                    update_record_status(stt, 'Pending')
                                    update_record_isrequest(stt, 0)
                                    start_background_worker()
                                    safe_rerun()
                            except Exception as _e:
                                st.error(f"Không thể gửi lại request cho hồ sơ {row['STT']}: {_e}")
                    else:
                        st.write("")
                with bcol2:
                    if st.button("View", key=f"view_{row['STT']}", type="secondary"):
                        st.session_state['selected_id'] = row['STT']
                        try:
                            st.query_params['id'] = str(row['STT'])
                        except:
                            pass
                        st.switch_page("pages/document_detail.py")
            
            # Hiển thị divider giữa các dòng trong trang hiện tại (ẩn cho dòng cuối của trang)
            if i < len(page_rows) - 1:
                st.divider()
        
        # Pagination controls and info
        colp1, colp2, colp3 = st.columns([1, 1, 6])
        with colp1:
            # Show Prev only when not on first page
            if page > 1:
                if st.button("⟵ Prev", key=f"prev_{page}"):
                    st.session_state['page'] = max(1, page - 1)
                    safe_rerun()
            else:
                st.write("")
        with colp2:
            # Show Next only when not on last page
            if page < total_pages:
                if st.button("Next ⟶", key=f"next_{page}"):
                    st.session_state['page'] = min(total_pages, page + 1)
                    safe_rerun()
            else:
                st.write("")
        with colp3:
            st.markdown(f"Page {page} / {total_pages} — {total_rows} rows")
    else:
        if search_query:
            st.warning(f"Không tìm thấy kết quả nào cho từ khóa: '{search_query}'")
        else:
            st.info("Chưa có hồ sơ nào. Hãy upload file đầu tiên!")

    # (Khi chọn Quản lý, trang sẽ chuyển sang các trang con tương ứng.)