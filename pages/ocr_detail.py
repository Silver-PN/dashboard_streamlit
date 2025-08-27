
import streamlit as st
import pandas as pd
import time
import base64
from streamlit_pdf_viewer import pdf_viewer
from io import BytesIO
from PIL import Image

def display_pdf(pdf_bytes):
    """Hiển thị PDF từ bytes bằng streamlit-pdf-viewer."""
    try:
        # Sử dụng streamlit-pdf-viewer để hiển thị PDF
        pdf_viewer(input=pdf_bytes, width=700)
    except Exception as e:
        st.error(f"Lỗi khi hiển thị PDF: {e}")
        # Fallback: hiển thị thông báo lỗi
        st.info("Không thể hiển thị PDF. Vui lòng kiểm tra lại tệp tin.")

def format_currency(amount):
    """Định dạng tiền tệ"""
    if not amount:
        return "N/A"
    try:
        # Nếu là số, định dạng thành tiền tệ
        if isinstance(amount, (int, float)):
            return f"{amount:,.0f} VND"
        return str(amount)
    except:
        return str(amount)
    
# Header với nút quay lại
col_header1, col_header2 = st.columns([6, 1])
with col_header1:
    st.title("Chi tiết kết quả OCR")
with col_header2:
    if st.button("← Quay lại", type="secondary"):
        st.switch_page("pages/home.py")

# Lấy dữ liệu từ session state
selected_id = st.session_state.get('selected_id', None)

if not selected_id:
    st.error("Không có ID nào được cung cấp.")
    st.page_link("pages/home.py", label="Quay về trang chính")
    st.stop()

# Kiểm tra xem ocr_results có trong session state không
if 'ocr_results' not in st.session_state or selected_id not in st.session_state['ocr_results']:
    st.error(f"Không tìm thấy dữ liệu cho ID: {selected_id}")
    st.page_link("pages/home.py", label="Quay về trang chính")
    st.stop()

# Lấy dữ liệu từ session
result_data = st.session_state['ocr_results'][selected_id]
ocr_data = result_data.get('ocr_data', {})
pdf_bytes_b64 = result_data.get('pdf_bytes', '')
doc_type = result_data.get('doc_type', 'Không xác định')
file_name = result_data.get('file_name', 'Không xác định')

# Hiển thị thông tin cơ bản
st.info(f"**Loại tài liệu:** {doc_type} | **Tên file:** {file_name}")

try:
    pdf_bytes = base64.b64decode(pdf_bytes_b64)
except Exception as e:
    st.error(f"Lỗi khi xử lý file PDF: {e}")
    st.stop()

# Tạo hai cột
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 Kết quả trích xuất từ OCR")
    
    # Hiển thị kết quả JSON trong expander
    with st.expander("Xem dữ liệu JSON gốc", expanded=False):
        st.json(ocr_data)
    
    # Hiển thị các trường dữ liệu một cách rõ ràng
    st.subheader("📝 Thông tin chi tiết")
    
    if ocr_data and ocr_data.get("status") == "success":
        data = ocr_data.get("data", {})
        
        # Tạo form hiển thị thông tin
        st.text_input("🆔 Mã hóa đơn", value=data.get("invoice_id", ""), disabled=True)
        st.text_input("👤 Tên khách hàng", value=data.get("customer_name", ""), disabled=True)
        st.text_area("📍 Địa chỉ", value=data.get("address", ""), disabled=True)
        st.text_input("💰 Tổng cộng", value=format_currency(data.get("total_amount")), disabled=True)
        
        # Hiển thị thời gian xử lý nếu có
        if "processing_time" in ocr_data:
            st.metric("⏱️ Thời gian xử lý", ocr_data["processing_time"])
        
        st.subheader("🛍️ Các mục hàng hóa")
        items = data.get("items", [])
        if items:
            for i, item in enumerate(items):
                with st.container():
                    st.markdown(f"**Mục {i+1}**")
                    col_item1, col_item2 = st.columns(2)
                    with col_item1:
                        st.text_input(f"Mô tả {i+1}", value=item.get('description', ''), disabled=True, key=f"desc_{i}")
                        st.text_input(f"Số lượng {i+1}", value=str(item.get('quantity', '')), disabled=True, key=f"qty_{i}")
                    with col_item2:
                        st.text_input(f"Giá {i+1}", value=format_currency(item.get('price')), disabled=True, key=f"price_{i}")
                    st.divider()
        else:
            st.info("Không có mục hàng hóa nào được tìm thấy.")
    else:
        st.error("Dữ liệu OCR không hợp lệ hoặc xử lý thất bại.")
        if ocr_data:
            st.json(ocr_data)

with col2:
    st.subheader("📄 Nội dung tệp PDF")
    
    # Thêm thông tin về file
    file_info_col1, file_info_col2 = st.columns(2)
    with file_info_col1:
        st.metric("Kích thước file", f"{len(pdf_bytes) / 1024:.1f} KB")
    with file_info_col2:
        st.metric("Trạng thái", "✅ Đã tải lên")
    
    # Hiển thị PDF
    display_pdf(pdf_bytes)

# Footer với các nút hành động
st.divider()
col_action1, col_action2, col_action3 = st.columns([1, 1, 1])
with col_action1:
    if st.button("🔄 Làm mới", type="secondary"):
        st.rerun()
with col_action2:
    if st.button("📥 Tải xuống PDF", type="secondary"):
        # Tạo link download
        st.download_button(
            label="Tải xuống PDF",
            data=pdf_bytes,
            file_name=f"document_{selected_id}.pdf",
            mime="application/pdf"
        )
with col_action3:
    if st.button("🏠 Về trang chính", type="primary"):
        st.switch_page("pages/home.py")