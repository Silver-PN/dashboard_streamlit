import streamlit as st
import pandas as pd
import os

# Đường dẫn file CSV - sử dụng đường dẫn tuyệt đối
try:
    import pathlib
    current_dir = pathlib.Path(__file__).parent
    csv_file_path = current_dir.parent / "data" / "document_types.csv"
except Exception:
    csv_file_path = None


# Hàm load dữ liệu từ CSV
def load_document_types():
    if os.path.exists(csv_file_path):
        try:
            return pd.read_csv(csv_file_path)
        except:
            # Nếu file bị lỗi, tạo file mới với dữ liệu mặc định
            default_data = pd.DataFrame({
                'ma_loai': ['VB001', 'VB002', 'VB003'],
                'ten_loai': ['Biên bản', 'Hợp đồng', 'Quyết định']
            })
            default_data.to_csv(csv_file_path, index=False)
            return default_data
    else:
        # Tạo file mới nếu chưa tồn tại
        default_data = pd.DataFrame({
            'ma_loai': ['VB001', 'VB002', 'VB003'],
            'ten_loai': ['Biên bản', 'Hợp đồng', 'Quyết định']
        })
        default_data.to_csv(csv_file_path, index=False)
        return default_data

# Hàm lưu dữ liệu vào CSV
def save_document_types(df):
    df.to_csv(csv_file_path, index=False)

# Hàm thêm loại văn bản mới
def add_document_type(ma_loai, ten_loai):
    df = load_document_types()
    
    # Kiểm tra mã loại đã tồn tại
    if ma_loai in df['ma_loai'].values:
        return False, "Mã loại văn bản đã tồn tại!"
    
    # Thêm dòng mới
    new_row = pd.DataFrame({'ma_loai': [ma_loai], 'ten_loai': [ten_loai]})
    df = pd.concat([df, new_row], ignore_index=True)
    
    # Lưu vào CSV
    save_document_types(df)
    return True, "Thêm loại văn bản thành công!"

# Hàm xóa loại văn bản
def delete_document_type(ma_loai):
    df = load_document_types()
    df = df[df['ma_loai'] != ma_loai]
    save_document_types(df)
    return "Đã xóa loại văn bản!"

# Hàm cập nhật tên loại văn bản
def update_document_type_name(ma_loai, ten_moi):
    df = load_document_types()
    df.loc[df['ma_loai'] == ma_loai, 'ten_loai'] = ten_moi
    save_document_types(df)
    return True, "Cập nhật tên loại văn bản thành công!"

# Load dữ liệu hiện tại
document_types_df = load_document_types()

# Giao diện chính
st.markdown("<h3>Quản lý loại văn bản</h3>", unsafe_allow_html=True)

# Form thêm mới
with st.expander("Thêm loại văn bản mới", expanded=True):
    col1, col2 = st.columns(2)
    
    with col1:
        ma_loai = st.text_input("Mã loại văn bản (*)", placeholder="Nhập mã loại văn bản")
    
    with col2:
        ten_loai = st.text_input("Tên loại văn bản (*)", placeholder="Nhập tên loại văn bản")
    
    if st.button("Thêm", type="primary"):
        if ma_loai and ten_loai:
            success, message = add_document_type(ma_loai, ten_loai)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        else:
            st.error("Vui lòng nhập đầy đủ thông tin!")

# Hiển thị danh sách loại văn bản
st.markdown("<h4>Danh sách loại văn bản hiện tại</h4>", unsafe_allow_html=True)

# Header cho bảng
header_col1, header_col2, header_col3, header_col4 = st.columns([2, 3, 1, 1])
with header_col1:
    st.markdown("**Mã loại**")
with header_col2:
    st.markdown("**Tên loại**")
with header_col3:
    st.markdown("**Thao tác**")
with header_col4:
    st.markdown("**Xóa**")

st.markdown("---")

# Reload dữ liệu sau khi thêm mới
document_types_df = load_document_types()

if not document_types_df.empty:
    # Tạo bảng hiển thị
    for index, row in document_types_df.iterrows():
        # Tạo cột chính
        col1, col2, col3, col4 = st.columns([2, 3, 1, 1])
        
        with col1:
            st.write(f"**{row['ma_loai']}**")
        
        with col2:
            # Tạo key duy nhất cho mỗi row
            edit_key = f"edit_{row['ma_loai']}"
            save_key = f"save_{row['ma_loai']}"
            
            # Kiểm tra xem có đang edit không
            if f"editing_{row['ma_loai']}" not in st.session_state:
                st.session_state[f"editing_{row['ma_loai']}"] = False
            
            if st.session_state[f"editing_{row['ma_loai']}"]:
                # Chế độ edit
                new_name = st.text_input(
                    "Tên mới", 
                    value=row['ten_loai'], 
                    key=f"input_{row['ma_loai']}",
                    label_visibility="collapsed"
                )
            else:
                # Chế độ hiển thị
                st.write(row['ten_loai'])
        
        with col3:
            if st.session_state[f"editing_{row['ma_loai']}"]:
                # Tạo 2 cột con để đặt nút save và cancel cạnh nhau
                save_col, cancel_col = st.columns(2)
                
                # Nút lưu khi đang edit
                with save_col:
                    if st.button("💾", key=save_key, help="Lưu thay đổi"):
                        if new_name and new_name.strip():
                            success, message = update_document_type_name(row['ma_loai'], new_name.strip())
                            if success:
                                st.success(message)
                                st.session_state[f"editing_{row['ma_loai']}"] = False
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.error("Tên không được để trống!")
                
                # Nút hủy khi đang edit
                with cancel_col:
                    if st.button("❌", key=f"cancel_{row['ma_loai']}", help="Hủy bỏ"):
                        st.session_state[f"editing_{row['ma_loai']}"] = False
                        st.rerun()
            else:
                # Nút edit khi không edit
                if st.button("✏️", key=edit_key, help="Chỉnh sửa tên"):
                    st.session_state[f"editing_{row['ma_loai']}"] = True
                    st.rerun()
        
        with col4:
            if st.button("🗑️", key=f"delete_{index}", help="Xóa loại văn bản", type="secondary"):
                delete_document_type(row['ma_loai'])
                st.success("Đã xóa loại văn bản!")
                st.rerun()
        
        st.divider()
else:
    st.info("Chưa có loại văn bản nào. Hãy thêm loại văn bản đầu tiên!")

# Nút quay về trang chính
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    if st.button("← Quay về trang chính", type="secondary"):
        st.switch_page("pages/home.py")