import streamlit as st
import pandas as pd
import time
from io import BytesIO
import base64

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

@st.dialog("📌 Thêm mới hồ sơ", width="small")
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
            # Gọi OCR giả lập
            ocr_result = call_ocr_api(pdf_file_object)

            # Thêm row mới vào bảng
            new_stt = len(st.session_state['data']) + 1

            new_row = pd.DataFrame({
                "STT": [new_stt],
                "Tên File": [uploaded_file.name],
                "THỜI GIAN TẢI LÊN": [time.strftime("%m/%d/%y %H:%M:%S")],
                "TRẠNG THÁI DỮ LIỆU": ["Complete"],
            })
            st.session_state['data'] = pd.concat(
                [st.session_state['data'], new_row], ignore_index=True
            )

            # Lưu kết quả OCR và pdf_bytes vào session (key: STT)
            st.session_state['ocr_results'][new_stt] = {
                "ocr_data": ocr_result,
                "pdf_bytes": base64.b64encode(pdf_bytes).decode('utf-8'),
                "doc_type": doc_type,
                "file_name": uploaded_file.name
            }

            st.success("Đã thêm row mới và xử lý OCR thành công!")
            st.rerun()

    if st.button("Hủy"):
        pass

# Giao diện trang chính
st.set_page_config(layout="wide", page_title="Trang Chính - Table")
st.title("Ứng dụng Demo OCR - Trang Chính")

# Khởi tạo session state
if 'data' not in st.session_state:
    # Mock data for initialization
    mock_ocr_result = {
        "status": "success",
        "data": {
            "invoice_id": "MOCK-INV-001",
            "customer_name": "Công ty Mock Data",
            "address": "456 Đường Giả Lập, Quận 2, TP. HCM",
            "total_amount": "1.234.567 VND",
            "items": [
                {"description": "Sản phẩm Mock A", "quantity": 1, "price": "1.000.000 VND"},
                {"description": "Sản phẩm Mock B", "quantity": 1, "price": "234.567 VND"}
            ]
        },
        "processing_time": "1.1s"
    }
    mock_pdf_bytes = b"This is a mock PDF file."
    mock_pdf_bytes_b64 = base64.b64encode(mock_pdf_bytes).decode('utf-8')

    st.session_state['data'] = pd.DataFrame({
        "STT": [1],
        "Tên File": ["File_01.pdf"],
        "THỜI GIAN TẢI LÊN": [time.strftime("%m/%d/%y %H:%M:%S")],
        "TRẠNG THÁI DỮ LIỆU": ["Complete"],
    })
    st.session_state['ocr_results'] = {
        1: {
            "ocr_data": mock_ocr_result,
            "pdf_bytes": mock_pdf_bytes_b64,
            "doc_type": "Biên bản",
            "file_name": "File_01.pdf"
        }
    }

if 'ocr_results' not in st.session_state:
    st.session_state['ocr_results'] = {}

# Nút để mở modal upload
if st.button("Upload"):
    show_modal()

# Tìm kiếm
search_query = st.text_input("🔍 Nhập số ID, BGD, tên tài liệu, hoặc tên việc")

# Lọc dữ liệu dựa trên search_query
filtered_data = st.session_state['data']
if search_query:
    filtered_data = filtered_data[
        filtered_data.apply(
            lambda row: search_query.lower() in str(row).lower(), axis=1
        )
    ]

# Hiển thị bảng và buttons để view details
st.subheader("Danh sách hồ sơ")

# Hiển thị dữ liệu với buttons
for index, row in filtered_data.iterrows():
    col1, col2, col3, col4, col5 = st.columns([1, 3, 2, 2, 2])
    
    with col1:
        st.write(f"**{row['STT']}**")
    with col2:
        st.write(row['Tên File'])
    with col3:
        st.write(row['THỜI GIAN TẢI LÊN'])
    with col4:
        st.write(row['TRẠNG THÁI DỮ LIỆU'])
    with col5:
        # Sử dụng button + switch_page thay vì link
        if st.button("👁️ View", key=f"view_{row['STT']}"):
            # Lưu ID được chọn vào session state
            st.session_state['selected_id'] = row['STT']
            # Chuyển trang mà không reset session state
            st.switch_page("pages/ocr_detail.py")

 