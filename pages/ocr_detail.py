
import streamlit as st
import pandas as pd
import time
import base64
import fitz # PyMuPDF
from io import BytesIO

def display_pdf(pdf_bytes):
    """Hiển thị PDF từ bytes."""
    try:
        # Mở PDF từ bytes
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Hiển thị từng trang dưới dạng ảnh
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("png")
            st.image(img_bytes, caption=f"Trang {page_num + 1}", use_container_width=True)
            
    except Exception as e:
        st.error(f"Lỗi khi hiển thị PDF: {e}")


st.set_page_config(layout="wide", page_title="Chi tiết OCR")

st.title("Chi tiết kết quả OCR")
selected_id = st.session_state.get('selected_id', None)
# Lấy id từ query params
query_params = st.query_params
# print("st.session_state['ocr_results']",st.session_state['ocr_results'])
if selected_id:
    # Kiểm tra xem ocr_results có trong session state không
    if 'ocr_results' in st.session_state and selected_id in st.session_state['ocr_results']:
        # Lấy dữ liệu từ session
        result_data = st.session_state['ocr_results'][selected_id]
        ocr_data = result_data['ocr_data']
        pdf_bytes_b64 = result_data['pdf_bytes']
        pdf_bytes = base64.b64decode(pdf_bytes_b64)

        # Tạo hai cột
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Kết quả trích xuất từ OCR")
            
            # Hiển thị kết quả JSON
            st.json(ocr_data)
            
            # Hiển thị các trường dữ liệu một cách rõ ràng
            st.subheader("Thông tin chi tiết")
            
            if ocr_data and ocr_data.get("status") == "success":
                data = ocr_data.get("data", {})
                
                st.text_input("Mã hóa đơn", data.get("invoice_id"))
                st.text_input("Tên khách hàng", data.get("customer_name"))
                st.text_area("Địa chỉ", data.get("address"))
                st.text_input("Tổng cộng", data.get("total_amount"))
                
                st.subheader("Các mục hàng hóa")
                items = data.get("items", [])
                if items:
                    for i, item in enumerate(items):
                        st.markdown(f"**Mục {i+1}**")
                        st.text(f"  - Mô tả: {item.get('description')}")
                        st.text(f"  - Số lượng: {item.get('quantity')}")
                        st.text(f"  - Giá: {item.get('price')}")
                else:
                    st.write("Không có mục hàng hóa nào được tìm thấy.")
        with col2:
            st.subheader("Nội dung tệp PDF")
            display_pdf(pdf_bytes)
    else:
        st.error(f"Không tìm thấy dữ liệu cho ID: {selected_id}")
        st.page_link("app.py", label="Quay về trang chính")
else:
    st.warning("Không có ID nào được cung cấp.")
    st.page_link("app.py", label="Quay về trang chính")
