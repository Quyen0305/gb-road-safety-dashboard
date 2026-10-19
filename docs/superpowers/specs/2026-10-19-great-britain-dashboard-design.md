# Thiết kế dashboard tai nạn giao thông Great Britain 2024

Trạng thái: người dùng đã chốt phương án sáu trang với menu bên trái ngày 19/10/2026, sau khi xem hai bản mẫu tương tác. Tài liệu này ghi lại phương án được chọn.

## 1. Mục tiêu và các lựa chọn

- Bài tập lớn môn Trực quan hóa dữ liệu: phân tích đặc điểm thời gian, không gian và mức độ nghiêm trọng của tai nạn giao thông tại Great Britain.
- Người dùng đã chọn Streamlit/Python và yêu cầu bố cục giống ảnh dashboard bán lẻ đã gửi.
- Giao diện tiếng Việt; chạy tại máy từ thư mục `D:\trucquan`.
- Một ứng dụng gồm sáu trang, chọn bằng menu bên trái. Trang Tổng quan bám sát ảnh tham khảo; các trang còn lại dành cho phân tích chi tiết.
- Phương án được chọn là “Sáu trang · menu bên trái” trong bản mẫu tương tác. Các trang dùng chung dữ liệu, bộ lọc và một cửa sổ trình duyệt.

## 2. Bố cục theo ảnh tham khảo

### Thanh bên trái

Thanh bên nền xám nhạt, rộng khoảng 250–280 px trên màn hình máy tính:

1. Biểu tượng giao thông đơn giản, tên RoadLens và dòng phụ Great Britain · 2024.
2. Nhóm “PHÂN TÍCH”: Tổng quan; Thời gian; Không gian; Mức độ nghiêm trọng; Người & phương tiện; Điều kiện xảy ra.
3. Tiêu đề “BỘ LỌC DỮ LIỆU”.
4. Khoảng ngày trong năm 2024; có lựa chọn nhanh cả năm hoặc quý.
5. Quốc gia: England, Scotland, Wales; mặc định chọn tất cả. Bộ lọc khu vực cảnh sát được đặt trong mục lọc chi tiết để thanh bên gọn.
6. Mức độ nghiêm trọng của vụ tai nạn, cho phép chọn nhiều.
7. Đô thị/nông thôn/không xác định.
8. Nút đặt lại bộ lọc; thông tin phạm vi dữ liệu.

Mặc định chọn toàn bộ dữ liệu. Chọn rỗng ở bộ lọc nhiều lựa chọn có nghĩa là không có kết quả; không tự chuyển thành chọn tất cả. Mọi nhãn đều thể hiện rõ bộ lọc thuộc cấp vụ tai nạn. Chuyển trang bằng menu giữ nguyên các lựa chọn; nút đặt lại đưa bộ lọc về toàn bộ năm 2024 nhưng giữ trang đang xem.

### Nội dung chính

- Nền trắng, khoảng cách thoáng, tiêu đề “Tai nạn giao thông tại Great Britain”.
- Dòng phụ nêu năm 2024 và phạm vi bộ lọc đang áp dụng.
- Tên trang đang xem nằm phía trên biểu đồ. Điều hướng bằng menu bên trái; vùng nội dung không có thanh sáu tab ngang.
- Hàng bốn chỉ số dùng chung: số vụ tai nạn; số người thương vong; số người tử vong; số phương tiện liên quan. Mỗi chỉ số ghi rõ đơn vị, không hiển thị phần trăm tăng/giảm so với năm trước.
- Bố cục trang Tổng quan:

```text
┌ RoadLens ────────┐  Tiêu đề và phạm vi dữ liệu
│ PHÂN TÍCH       │  [Số vụ] [Thương vong] [Tử vong] [Phương tiện]
│ • Tổng quan     │  Tổng quan
│   Thời gian     │  ┌ Xu hướng số vụ theo tháng ──┐ ┌ Cơ cấu mức độ ┐
│   Không gian    │  │ Biểu đồ đường              │ │ Donut        │
│   Nghiêm trọng  │  └────────────────────────────┘ └──────────────┘
│   Người & xe    │  ┌ Tai nạn theo quốc gia ─────┐ ┌ Đô thị/nông thôn ┐
│   Điều kiện     │  │ Thanh ngang               │ │ Cột chồng        │
│ BỘ LỌC DỮ LIỆU │  └───────────────────────────┘ └──────────────────┘
│ Ngày, vùng...   │  Nhận xét / bảng tổng hợp / phương pháp
└─────────────────┘
```

Hàng biểu đồ đầu chia chiều rộng xấp xỉ 1,7:1; hàng thứ hai chia 1:1. Biểu đồ khu vực ở Tổng quan so sánh England, Scotland và Wales như bản mẫu đã chọn. Xếp hạng top 10 khu vực cảnh sát được đặt ở trang Không gian, có bảng đầy đủ để tải về. Donut tính trên số vụ tai nạn, không dùng số người thương vong.

Trên cửa sổ hẹp, thanh bên có thể thu gọn và các biểu đồ được xếp dọc. Giữ chữ dễ đọc và hạn chế cuộn ngang.

## 3. Nội dung sáu trang

| Trang | Nội dung chính |
| --- | --- |
| Tổng quan | Bốn biểu đồ theo bố cục trên; nhận xét ngắn về tháng và khu vực có số vụ cao nhất trong tập đang chọn. |
| Thời gian | Diễn biến theo tháng; số vụ theo giờ; heatmap thứ trong tuần × giờ; so sánh ngày thường/cuối tuần bằng tổng số vụ và bình quân theo số ngày trong khoảng ngày chọn. |
| Không gian | Bản đồ mật độ hoặc lớp điểm tổng hợp; lớp màu theo mức độ nghiêm trọng; xếp hạng top 10 khu vực cảnh sát; so sánh đô thị/nông thôn. Bản đồ và biểu đồ cùng nhận bộ lọc chung. |
| Mức độ nghiêm trọng | Số lượng và tỷ trọng ba mức độ; cột chồng 100% theo giờ hoặc tháng; so sánh số vụ với tỷ trọng vụ tử vong/nghiêm trọng theo khu vực. Luôn kèm số quan sát. |
| Người & phương tiện | Thương vong theo tuổi, giới tính, người lái/hành khách/người đi bộ; phương tiện theo loại. Phân biệt rõ biểu đồ đếm người và biểu đồ đếm phương tiện. |
| Điều kiện xảy ra | Số vụ và cơ cấu mức độ nghiêm trọng theo thời tiết, ánh sáng, mặt đường, loại đường, giới hạn tốc độ. Cho phép chọn điều kiện phân tích để tránh hiển thị quá nhiều biểu đồ cùng lúc. |

Các phép so sánh chính dùng những nhóm cố định, như đô thị/nông thôn hoặc ngày thường/cuối tuần. Phiên bản đầu không cần trình tạo hai bộ lọc A/B độc lập.

## 4. Ngôn ngữ trực quan và tương tác

- Đỏ (#e66b76): vụ có tử vong; cam (#eea34a): vụ nghiêm trọng; xanh dương (#4b91e8): vụ nhẹ; xám: không xác định. Giữ màu nhất quán trên mọi trang, kèm nhãn và chú giải.
- Biểu đồ có tooltip tiếng Việt, đơn vị rõ ràng, tháng/thứ/giờ được sắp xếp theo thời gian.
- Bộ chuyển số lượng/tỷ trọng chỉ xuất hiện trên các biểu đồ mà hai cách đo đều có ý nghĩa.
- Nhận xét được tính từ dữ liệu đang lọc, chỉ mô tả kết quả quan sát; có xử lý trường hợp đồng hạng và không có dữ liệu.
- Cung cấp bảng tổng hợp của từng phân tích và nút tải CSV UTF-8 có BOM để mở bằng Excel.
- Có mục thu gọn giải thích nguồn dữ liệu, phương pháp đếm, đơn vị, các giá trị chưa xác định và giới hạn diễn giải.
- Không đưa biểu tượng hay chỉ số thương mại từ ảnh mẫu vào nội dung tai nạn giao thông.

## 5. Nguồn dữ liệu và mô hình đếm

Nguồn ứng dụng: `du_lieu_tai_nan_2024_san_sang_truc_quan.csv`. Ba CSV gốc được dùng để đối chiếu, không sửa dữ liệu nguồn.

Kết quả khảo sát đã thực hiện:

| Đại lượng | Giá trị |
| --- | ---: |
| Số dòng bảng ghép | 200.522 |
| Số cột | 121 |
| Vụ tai nạn duy nhất | 100.927 |
| Phương tiện duy nhất | 183.514 |
| Người thương vong duy nhất | 128.272 |
| Người tử vong theo dữ liệu gốc | 1.602 |
| Vụ có tử vong | 1.502 |
| Vụ nghiêm trọng | 23.567 |
| Vụ nhẹ | 75.858 |
| Khoảng ngày | 01/01/2024–31/12/2024 |

Tách các bảng phân tích trong bộ nhớ:

1. Vụ tai nạn: một dòng cho mỗi `collision_index`.
2. Phương tiện: một dòng cho mỗi `vehicle_key`.
3. Thương vong: một dòng cho mỗi `casualty_key`, chỉ lấy bản ghi thực có thương vong (`has_casualty_record`).

Bộ lọc chung tạo tập `collision_index` phù hợp. Các chỉ số phương tiện và thương vong lấy từ những bảng riêng, liên kết bằng tập mã vụ này. Không đếm số dòng của bảng ghép và không cộng cờ đếm sau một phép lọc có thể loại bỏ dòng đại diện.

Chỉ số mức độ nghiêm trọng của vụ dùng `collision_severity`; mức độ của người dùng `casualty_severity`. Số người tử vong có thể khác số vụ có tử vong.

Tỷ trọng vụ tử vong/nghiêm trọng = số vụ có `collision_severity` thuộc {1, 2} chia tổng số vụ của nhóm đang phân tích sau bộ lọc chung. Ghi rõ mẫu số và đơn vị; khi mẫu số bằng 0 hiển thị không có dữ liệu.

Sử dụng mức độ nghiêm trọng ghi nhận gốc cho phiên bản đầu. Các số đã hiệu chỉnh của DfT không được trộn với số gốc. Chú thích rõ lựa chọn này trong phương pháp.

Các mã phân loại phải được đối chiếu bảng mã chính thức DfT trước triển khai nhãn. Xác định quốc gia từ tiền tố E/S/W của `local_authority_ons_district`; tiền tố khác hoặc thiếu vào nhóm không xác định. Dùng tên khu vực cảnh sát cho phân tích chi tiết. Trường chưa có tên hiển thị mã và ghi rõ, không tự đoán tên.

Ngày, tháng, giờ và thứ được chuẩn hóa từ trường ngày/giờ. Các giá trị thiếu, không áp dụng và không xác định không tự đổi thành 0 hoặc loại bỏ khỏi tổng số. Kiểm tra tính hợp lệ của tọa độ; tọa độ không hợp lệ chỉ bị loại khỏi bản đồ và phải có thông báo số điểm không thể hiển thị.

## 6. Kiến trúc dự kiến

- Streamlit dùng `st.Page` và `st.navigation` để quản lý sáu trang. Menu và bộ lọc đặt trong phần khung dùng chung; dùng điều hướng gốc của Streamlit để giữ trạng thái khi chuyển trang.
- pandas đọc các cột cần thiết, chuẩn hóa kiểu dữ liệu, tách các bảng theo cấp đếm; kết quả được cache và làm mới khi tệp nguồn thay đổi.
- Plotly vẽ các biểu đồ tương tác; Pydeck phục vụ bản đồ. Chọn lớp tổng hợp hoặc lớp điểm phù hợp với khoảng 101 nghìn vụ, tránh lấy mẫu ngẫu nhiên mà không công bố.
- Tách phần đọc dữ liệu, phép tính, biểu đồ và giao diện để có thể kiểm tra công thức mà không cần chạy trình duyệt.
- Luồng dữ liệu: CSV → bảng chuẩn hóa → bộ lọc cấp vụ → chỉ số/bảng tổng hợp → biểu đồ và tải CSV.
- Phân phối mã nguồn, danh sách thư viện và hướng dẫn chạy trên Windows. Chưa yêu cầu triển khai lên dịch vụ bên ngoài.

## 7. Trạng thái lỗi và diễn giải

- Thiếu tệp hoặc thiếu cột bắt buộc: thông báo rõ tên tệp/cột cần có.
- Khoảng ngày chưa chọn đủ hoặc bộ lọc không có kết quả: thông báo phù hợp và nút đặt lại; tránh biểu đồ lỗi hoặc nhận xét sai.
- Nếu nền bản đồ không tải được do kết nối mạng, phần phân tích và dữ liệu số vẫn có thể sử dụng; giao diện nêu giới hạn của bản đồ.
- Số vụ cao không tự chứng minh xác suất gặp tai nạn cao vì chưa có mẫu số lưu lượng giao thông.
- Giới hạn tốc độ là giới hạn của đường, không phải tốc độ thực tế khi xảy ra tai nạn.
- Các so sánh điều kiện mô tả mối liên hệ trong dữ liệu; không kết luận nguyên nhân.
- Dữ liệu có một năm nên không tạo so sánh giữa các năm.

## 8. Tiêu chí nghiệm thu

1. Giao diện Tổng quan nhận diện được cấu trúc ảnh mẫu: thanh bên, bốn KPI, hàng đường + donut, hàng thanh ngang + cột.
2. Mặc định các tổng số khớp bảng kiểm tra ở mục 5 và ba CSV gốc.
3. Tổng số không đổi khi thay đổi thứ tự các dòng của bảng ghép; bộ lọc cập nhật nhất quán ở ba cấp vụ, người và phương tiện.
4. Kiểm tra phép tính tỷ trọng, bình quân theo ngày, nhóm không xác định và tập lọc rỗng bằng những ví dụ có kết quả đối chiếu được.
5. Các bảng biểu thể hiện cùng tập dữ liệu; bản đồ dùng mỗi vụ đúng một lần hoặc tổng hợp bảo toàn số vụ hợp lệ.
6. Chạy thử cả sáu trang, lựa chọn bộ lọc hẹp và nút đặt lại; chuyển trang giữ bộ lọc; tải CSV mở được với tiếng Việt và đúng số liệu.
7. Kiểm tra trực quan trên cửa sổ máy tính và cửa sổ hẹp: nhãn không bị cắt, màu nhất quán, đơn vị rõ ràng.

## 9. Tham khảo

- Ảnh bố cục do người dùng cung cấp: `codex-clipboard-2fd97e5b-f4d5-40f2-bf9f-3100864f00c3.png`.
- [DfT Road safety open data](https://www.gov.uk/government/statistical-data-sets/road-safety-open-data).
- [DfT annual report 2024](https://www.gov.uk/government/statistics/reported-road-casualties-great-britain-annual-report-2024/reported-road-casualties-great-britain-annual-report-2024).
