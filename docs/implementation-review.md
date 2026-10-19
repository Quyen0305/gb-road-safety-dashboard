# Kiểm tra bàn giao RoadLens

- Triển khai theo thiết kế sáu trang menu bên trái đã được duyệt.
- 32 kiểm tra tự động đạt: dữ liệu, mẫu số, bộ lọc, điều hướng, CSV, bản đồ và thứ tự giờ/tháng.
- Đối chiếu với ba CSV DfT gốc: khớp mọi khóa vụ/phương tiện/người thương vong và mức độ vụ/người; tổng 100.927 vụ, 183.514 phương tiện, 128.272 người thương vong, 1.602 tử vong.
- Kiểm tra trình duyệt: sáu trang với dữ liệu thật; Scotland giữ 4.167 vụ qua chuyển trang; đặt lại phục hồi toàn năm; CSV tải xuống có BOM, 12 tháng, tổng 4.167.
- Kiểm tra desktop và chiều rộng 390 px: menu đóng/mở được, không tràn ngang. Ảnh tại `dashboard-preview.png`.
- Bản đồ ngoại tuyến hiển thị đường bờ lưu tại máy và toàn bộ dữ liệu hợp lệ; chế độ trực tuyến là tùy chọn.
- Rà soát độc lập phát hiện một lỗi thứ tự giờ khi nhóm tử vong thiếu giờ. Đã sửa bằng thứ tự danh mục rõ ràng, kiểm tra hồi quy cho cả giờ/tháng và xác minh với dữ liệu Wales thật.
- Không còn lỗi Critical/Important hoặc Minor được hoãn từ lượt rà soát.

## Quyết định trong quá trình triển khai

1. Thư mục chưa có Git: làm trực tiếp tại `D:\trucquan`, giữ nhật ký thay cho lịch sử commit. CSV nguồn không sửa. Giới hạn: không có khôi phục theo commit.
2. Chỉ chạy tại máy cục bộ theo phạm vi đã duyệt. Giới hạn: chưa truy cập được từ máy khác.
3. Người rà soát độc lập kiểm tra mã, chạy test và kiểm tra cấu hình biểu đồ; không lặp lại thao tác trình duyệt để tránh ảnh hưởng phiên đang mở. Giao diện đã được người triển khai kiểm tra; giới hạn: một người kiểm tra trực quan, không phải hai.

Hướng dẫn mở lại ứng dụng và kiểm chứng: xem `../README.md`.
