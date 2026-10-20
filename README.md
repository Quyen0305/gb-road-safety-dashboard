# RoadLens · Great Britain 2024

Dashboard tiếng Việt cho bài tập lớn **Phân tích trực quan đặc điểm thời gian, không gian và mức độ nghiêm trọng của tai nạn giao thông tại Great Britain**.

Notebook xử lý dữ liệu thiếu và gộp dữ liệu 2024: [xu_ly_du_lieu_thieu_va_gop_2024_da_chinh_sua.ipynb](notebooks/xu_ly_du_lieu_thieu_va_gop_2024_da_chinh_sua.ipynb). Giữ nguyên nội dung và kết quả đã lưu trong tệp gốc.

## Chạy trên máy này

Mở PowerShell trong `D:\trucquan`, chạy:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Hoặc dùng script có sẵn:

```powershell
.\run_dashboard.ps1
```

Mở **http://127.0.0.1:8501** trong trình duyệt. Nhấn `Ctrl+C` ở cửa sổ chạy lệnh để dừng. Nếu cổng đang được dùng, chạy `./run_dashboard.ps1 -Port 8502` rồi mở địa chỉ với cổng tương ứng. Nếu PowerShell chặn script, dùng lệnh Python phía trên; không cần thay đổi chính sách hệ thống.

Ứng dụng chỉ lắng nghe ở máy cục bộ và tắt gửi thống kê sử dụng Streamlit. Lần đọc CSV đầu tiên mất vài giây; những lần đổi bộ lọc sau sử dụng dữ liệu đã cache.

## Cài trên máy khác

Đã kiểm tra với Python **3.14.6** trên Windows và các phiên bản trong `requirements.txt`. Mang theo mã nguồn và CSV đã chuẩn bị, rồi chạy:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Tệp dữ liệu mặc định đặt cạnh `app.py`: `du_lieu_tai_nan_2024_san_sang_truc_quan.csv`. Ba CSV `dft-road-casualty-statistics-*-2024.csv` dùng để kiểm chứng, không cần để mở dashboard. Không chỉnh sửa các CSV nguồn.

Có thể chỉ định CSV khác cùng cấu trúc 2024 trong phiên PowerShell hiện tại:

```powershell
$env:ROADLENS_DATA = 'D:\du_lieu\tai_nan_2024.csv'
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## Sáu trang

| Trang | Nội dung |
| --- | --- |
| Tổng quan | Chỉ số chính, xu hướng tháng, cơ cấu mức độ, quốc gia, đô thị/nông thôn |
| Thời gian | Tháng, giờ, heatmap thứ × giờ, ngày thường/cuối tuần |
| Không gian | Tô màu vùng theo số vụ hoặc quốc gia, bản đồ tên địa phương, tìm kiếm/phóng tới địa phương, top 10 và bảng đầy đủ |
| Mức độ nghiêm trọng | Số vụ, tỷ trọng theo thời gian, quy mô và tỷ trọng theo khu vực |
| Người & phương tiện | Tuổi, giới tính, vai trò người thương vong; loại phương tiện |
| Điều kiện xảy ra | Thời tiết, ánh sáng, mặt đường, loại đường, giới hạn tốc độ |

Menu nằm phía trên bộ lọc ở thanh bên trái. Dùng menu này để giữ bộ lọc khi chuyển trang; tải lại trang trình duyệt tạo phiên mới và có thể đặt lại lựa chọn. Ở màn hình nhỏ, mở/đóng thanh bên bằng nút mũi tên góc trên trái.

Bộ lọc chung: ngày/quý, quốc gia, mức độ vụ, đô thị/nông thôn và khu vực cảnh sát trong mục **Lọc chi tiết**. Chọn rỗng nghĩa là không có kết quả. Nút **Đặt lại bộ lọc** chọn lại toàn bộ dữ liệu và giữ trang đang xem. Mở **Bảng số liệu · Tải CSV** dưới mỗi phân tích để xem và tải bảng UTF-8 có BOM dùng được trong Excel. Các bộ chọn bên trong trang (ví dụ điều kiện hoặc lớp bản đồ) độc lập với bộ lọc chung.

Nút **✕** cạnh tên mỗi bộ lọc nhiều lựa chọn xóa toàn bộ lựa chọn của riêng bộ lọc đó. Dấu **×** trên từng ô màu xanh chỉ bỏ một lựa chọn. Bộ lọc đã trống sẽ giữ nguyên khi chuyển trang; dùng **Đặt lại bộ lọc** để khôi phục toàn bộ lựa chọn.

## Cách tính và giới hạn

| Chỉ số mặc định | Giá trị |
| --- | ---: |
| Vụ tai nạn duy nhất | 100.927 |
| Người thương vong | 128.272 |
| Người tử vong | 1.602 |
| Phương tiện liên quan | 183.514 |

- CSV ghép có 200.522 dòng. Đếm riêng theo `collision_index`, `vehicle_key`, `casualty_key`; thương vong chỉ lấy bản ghi có `has_casualty_record`. Không cộng số dòng ghép.
- Bộ lọc chọn vụ trước, sau đó lấy người và phương tiện thuộc vụ đó. Ví dụ lọc “Có tử vong” vẫn bao gồm người bị thương trong các vụ có tử vong.
- Số vụ theo mức độ gốc: tử vong **1.502**, nghiêm trọng **23.567**, nhẹ **75.858**. Số người tử vong không đồng nhất với số vụ có tử vong.
- Sử dụng mức độ ghi nhận gốc, **chưa hiệu chỉnh theo phương pháp DfT**. Không trộn với tổng KSI đã hiệu chỉnh trong các báo cáo chính thức.
- Tỷ trọng dùng tổng số vụ của nhóm sau bộ lọc làm mẫu số. Bình quân ngày thường/cuối tuần chia cho toàn bộ ngày lịch thuộc nhóm trong khoảng chọn, kể cả ngày không có vụ; không có ngày thuộc nhóm thì để trống.
- Quốc gia suy ra từ tiền tố E/S/W của mã local authority. Nhóm thiếu/chưa rõ vẫn được giữ; mã không có nhãn hiển thị nguyên mã. Giờ thiếu không vào biểu đồ giờ nhưng vẫn được đếm trong KPI.
- Bản đồ hiển thị tất cả vụ có tọa độ trong vùng −9°…3° kinh độ, 49°…61° vĩ độ; báo số vụ bị loại. Mật độ theo ô 0,08° bảo toàn số vụ, không phải mật độ trên km². Chế độ điểm giữ từng vụ; các điểm có thể chồng nhau.
- Lớp **Theo địa phương** đếm theo `local_authority_ons_district`, tra tên từ bảng mã DfT 2024 lưu sẵn trong `local_authorities.json` (tái tạo bằng `scripts/build_lookups.py`). Đơn vị này có thể bao gồm vùng ngoài thành phố. Điểm đại diện là trung bình tọa độ tai nạn hợp lệ, không phải tâm hoặc ranh giới thành phố. Bảng xếp hạng đếm mọi vụ sau bộ lọc, kể cả vụ thiếu tọa độ. Nhãn top 10 có tên, hạng và số vụ; bố trí lệch cùng đường nối ở góc nhìn ban đầu để dễ đọc. Phóng to hoặc tìm địa phương khi các nhãn nằm sát nhau. Hai lớp mật độ và điểm vẫn giữ nguyên.
- Lớp **Tô màu địa phương** ghép số vụ theo mã vào 350 vùng ONS 2024 ở Great Britain. Màu xanh có các ngưỡng cố định **1–49, 50–149, 150–399, 400–999, ≥ 1.000 vụ**; xám là 0 vụ sau bộ lọc. Tổng hợp bao gồm cả vụ thiếu tọa độ. Mã đặc biệt `EHEATHROW` không có polygon ONS riêng: 33 vụ trong dữ liệu mặc định được giữ bằng điểm tím và trong bảng, không cộng vào vùng khác. Các mã chưa khớp khác cũng được báo và giữ trong bảng; chỉ hiện điểm khi có tọa độ đại diện hợp lệ.
- Lớp **Tô màu quốc gia** dùng ba màu riêng cho England, Scotland, Wales, không mã hóa số vụ bằng độ đậm. Tổng quốc gia lấy theo trường `country` đã chuẩn hóa nên vẫn gồm mã Heathrow. Quốc gia có 0 vụ sau bộ lọc được tô xám. Cả hai lớp có tooltip tên/số vụ và hoạt động ngoại tuyến với ranh giới lưu tại máy. Nền CARTO tùy chọn có lớp tô bán trong suốt.
- Mặc định dùng đường bờ đơn giản lưu tại máy, không tải nền đường. Bật **Nền đường trực tuyến** để dùng CARTO/OpenStreetMap, cần Internet. Tắt công tắc nếu mạng không khả dụng. Chế độ ngoại tuyến vẫn cần trình duyệt hỗ trợ WebGL.
- Số vụ không phải xác suất rủi ro khi chưa có lưu lượng giao thông làm mẫu số. Các mối liên hệ không chứng minh nguyên nhân. `speed_limit` là giới hạn tốc độ của đường (mph), không phải tốc độ xe. Chỉ có 2024 nên không so sánh năm trước.
- STATS19 chỉ bao gồm tai nạn có thương vong trên đường công cộng được cảnh sát ghi nhận; không đại diện cho mọi sự cố giao thông.

## Kiểm tra và đối chiếu

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -X utf8 scripts/validate_data.py
```

Kiểm tra bao gồm chống đếm trùng, đảo thứ tự dòng, dữ liệu thiếu, mẫu số, lọc rỗng, giữ bộ lọc qua sáu trang, tải CSV và cấu hình bản đồ. Script đối chiếu so sánh tập khóa và mức độ từng bản ghi với ba CSV gốc; trả lỗi nếu có chênh lệch. Cần chạy lại sau khi thay dữ liệu hoặc thư viện.

## Mã nguồn và nguồn tham khảo

- `app.py`: khung chung, điều hướng và trạng thái.
- `road_safety/data.py`, `analytics.py`: chuẩn hóa, kiểm tra, lọc và tổng hợp.
- `road_safety/charts.py`, `ui.py`: biểu đồ và thành phần giao diện.
- `views/`: sáu trang phân tích; `.streamlit/config.toml`: cấu hình.
- [DfT road safety open data và bảng mã](https://www.gov.uk/government/statistical-data-sets/road-safety-open-data), Open Government Licence v3.0. Bản bảng mã tải ngày 19/10/2026 được lưu tại `road_safety/assets/dft-data-guide.xlsx`, dùng sheet `2024_code_list`; nhãn tiếng Việt và nhãn gốc tại `lookups.json`. Chạy `scripts/build_lookups.py` để tái tạo nhãn từ bản đã lưu (cần openpyxl).
- [Báo cáo DfT 2024](https://www.gov.uk/government/statistics/reported-road-casualties-great-britain-annual-report-2024/reported-road-casualties-great-britain-annual-report-2024).
- [Natural Earth](https://www.naturalearthdata.com/about/terms-of-use/): hình học public domain, [nguồn GeoJSON 1:110m](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson). Lưu đường bờ UK/Ireland làm bối cảnh; số liệu chỉ gồm Great Britain, không bao gồm Northern Ireland.
- ONS: [Local Authority Districts May 2024 BGC](https://www.data.gov.uk/dataset/0efbbd6b-6200-4104-9d14-f30e58118fd4/local-authority-districts-may-2024-boundaries-uk-bgc), [Countries December 2024 BGC](https://www.data.gov.uk/dataset/c0ebe11c-0c81-4eed-81b3-a0394d4116a9/countries-december-2024-boundaries-uk-bgc1). Ranh giới OS/ONS © Crown copyright / database right 2024, Open Government Licence v3.0. Tái tạo bằng `scripts/build_boundaries.py` (cần mạng lúc chạy script, không cần mạng khi dùng dashboard). Lưu WGS84, lọc Northern Ireland, giản lược thêm 0,001° và 5 chữ số thập phân để hiển thị; không dùng hình học giản lược này đo diện tích hay gán tai nạn bằng tọa độ.
- [Streamlit multipage apps](https://docs.streamlit.io/develop/concepts/multipage-apps/page-and-navigation), [Plotly](https://plotly.com/python/), [Pydeck](https://deckgl.readthedocs.io/).
