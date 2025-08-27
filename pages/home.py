import streamlit as st
import pandas as pd
import time
from io import BytesIO
import base64
from PIL import Image
from config import get_nav_from_toml

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
    doc_type = st.selectbox("Chọn loại hồ sơ", ["Biên bản", "Hợp đồng"])

    uploaded_file = st.file_uploader(
        "Chọn một tệp PDF để trích xuất thông tin", type="pdf"
    )

    if uploaded_file is not None:
        pdf_bytes = uploaded_file.getvalue()
        pdf_file_object = BytesIO(pdf_bytes)
        pdf_file_object.name = uploaded_file.name

        if st.button("Bắt đầu trích xuất và Lưu"):
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
                new_stt = add_record(file_name, doc_type, file_path)
                
                # Cập nhật session state
                st.session_state['data'] = load_records()

                # Lưu kết quả OCR và thông tin file vào session (key: STT)
                st.session_state['ocr_results'][new_stt] = {
                    "ocr_data": ocr_result,
                    "pdf_bytes": base64.b64encode(pdf_bytes).decode('utf-8'),
                    "doc_type": doc_type,
                    "file_name": file_name,
                    "file_path": file_path  # Lưu đường dẫn file vật lý
                }

                st.success(f"Đã thêm hồ sơ mới và xử lý OCR thành công! File đã được lưu tại: {file_path}")
                st.rerun()
                
            except Exception as e:
                st.error(f"Lỗi khi lưu file: {str(e)}")

    if st.button("Hủy"):
        pass



# Hàm load danh sách hồ sơ từ CSV
def load_records():
    import os
    csv_path = "data/records.csv"
    if os.path.exists(csv_path):
        try:
            return pd.read_csv(csv_path)
        except:
            return pd.DataFrame(columns=["STT", "Tên File", "THỜI GIAN TẢI LÊN", "TRẠNG THÁI DỮ LIỆU", "LOẠI HỒ SƠ"])
    else:
        return pd.DataFrame(columns=["STT", "Tên File", "THỜI GIAN TẢI LÊN", "TRẠNG THÁI DỮ LIỆU", "LOẠI HỒ SƠ"])

# Hàm lưu danh sách hồ sơ vào CSV
def save_records(df):
    import os
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    csv_path = os.path.join(data_dir, "records.csv")
    df.to_csv(csv_path, index=False)

# Hàm thêm hồ sơ mới
def add_record(file_name, doc_type, file_path):
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
        "LOẠI HỒ SƠ": [doc_type]
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
# if menu_choice == "Số hóa tài liệu":
# Upload section
col_u1, col_u2, col_u3 = st.columns([6, 2, 2],vertical_alignment="bottom")
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
                st.switch_page("pages/ocr_detail.py")
        
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
