# Great Britain Road Safety Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Tạo ứng dụng Streamlit tiếng Việt gồm sáu trang với menu bên trái, dùng dữ liệu tai nạn Great Britain 2024 và bố cục người dùng đã chọn.

**Architecture:** CSV được đọc và chuẩn hóa thành ba bảng riêng ở cấp vụ tai nạn, phương tiện và người thương vong. Phần khung ứng dụng giữ menu, bộ lọc và bốn KPI; mỗi trang sử dụng cùng tập vụ đã lọc và chỉ tạo các biểu đồ của trang đang mở. Phần tính toán độc lập với Streamlit để có thể kiểm tra kết quả trên dữ liệu nhỏ và đối chiếu với toàn bộ dữ liệu thật.

**Tech Stack:** Python, Streamlit (`st.Page` / `st.navigation`), pandas, Plotly, Pydeck, pytest. Dùng môi trường `.venv` riêng tại dự án; ghi lại các phiên bản cài đặt thành công để tái lập.

**Spec:** `docs/superpowers/specs/2026-10-19-great-britain-dashboard-design.md`.

## Global Constraints

- Một ứng dụng gồm sáu trang, chọn bằng menu bên trái.
- Giao diện tiếng Việt; chạy tại máy từ thư mục `D:\trucquan`.
- Nguồn ứng dụng: `du_lieu_tai_nan_2024_san_sang_truc_quan.csv`. Ba CSV gốc được dùng để đối chiếu, không sửa dữ liệu nguồn.
- Mặc định chọn toàn bộ dữ liệu. Chọn rỗng ở bộ lọc nhiều lựa chọn có nghĩa là không có kết quả; không tự chuyển thành chọn tất cả.
- Chuyển trang bằng menu giữ nguyên các lựa chọn; nút đặt lại đưa bộ lọc về toàn bộ năm 2024 nhưng giữ trang đang xem.
- Sử dụng mức độ nghiêm trọng ghi nhận gốc cho phiên bản đầu. Các số đã hiệu chỉnh của DfT không được trộn với số gốc.
- Đỏ (#e66b76): vụ có tử vong; cam (#eea34a): vụ nghiêm trọng; xanh dương (#4b91e8): vụ nhẹ; xám: không xác định.
- Bốn KPI mặc định: 100.927 vụ, 128.272 người thương vong, 1.602 người tử vong, 183.514 phương tiện.
- Phân tích và xuất CSV bảo toàn nhóm không xác định; không quy số thiếu thành 0.
- Chưa yêu cầu triển khai lên dịch vụ bên ngoài.

## Review Focus

1. Các dòng lặp sau phép ghép không làm tăng KPI; đổi thứ tự dòng vẫn cho cùng kết quả — kiểm tra ở Task 1.
2. Ngày không có vụ vẫn được tính vào mẫu số khi tính bình quân theo ngày thường/cuối tuần — kiểm tra ở Task 2.
3. Chuyển trang hoặc đặt lại không vô tình thay đổi các bộ lọc ngoài ý muốn; tập lọc rỗng không bị đổi thành tất cả — kiểm tra ở Task 3.
4. Mã chưa có nhãn, giờ thiếu và tọa độ không hợp lệ không làm mất vụ khỏi KPI — kiểm tra ở Tasks 1–2.
5. CSV tiếng Việt xuất được và dữ liệu bản đồ không bị lấy mẫu ngầm; nếu nền bản đồ cần mạng thì ứng dụng nêu rõ — kiểm tra ở Tasks 2–4.

## Cấu trúc tệp

```text
D:\trucquan\
  app.py                         # khung chung, điều hướng và trạng thái
  requirements.txt               # thư viện đã kiểm tra tương thích
  requirements-dev.txt           # công cụ kiểm thử
  README.md                      # cài đặt, chạy, cách đọc dashboard
  run_dashboard.ps1              # chạy bằng Python trong .venv
  .streamlit/config.toml         # nền sáng, màu và cấu hình cục bộ
  road_safety/
    __init__.py
    data.py                      # đọc CSV, chuẩn hóa, bảng ở ba cấp
    labels.py                    # nhãn và thứ tự các nhóm phân loại
    analytics.py                 # lọc, tổng hợp, tỷ trọng, thời gian, bản đồ
    charts.py                    # Plotly và Pydeck từ bảng tổng hợp
    ui.py                        # bộ lọc, KPI, bảng tải về và phương pháp
    assets/theme.css             # bố cục tương ứng bản mẫu đã chọn
    assets/lookups.json          # mã DfT dùng trong ứng dụng và nguồn
    assets/gb-ireland.geojson    # đường bờ đơn giản cho chế độ không có nền trực tuyến
  views/
    overview.py
    temporal.py
    spatial.py
    severity.py
    people_vehicles.py
    conditions.py
  tests/
    conftest.py
    test_data.py
    test_analytics.py
    test_app.py
  scripts/
    validate_data.py             # đối chiếu với ba CSV gốc
```

Thư mục hiện tại chưa có Git. Các bước hoàn thành được đánh dấu trong kế hoạch; không giả định có nhánh hoặc remote, không đưa các CSV lớn vào một kho Git tự tạo.

## Task 1: Nạp dữ liệu, bảng mã và môi trường chạy

**Files:** `requirements.txt`, `requirements-dev.txt`, `road_safety/__init__.py`, `road_safety/data.py`, `road_safety/labels.py`, `road_safety/assets/lookups.json`, `tests/conftest.py`, `tests/test_data.py`.

**Interfaces:**
- `DataBundle`: dataclass gồm `collisions`, `vehicles`, `casualties` (pandas DataFrame) và `quality` (dict[str, int]).
- `normalize_data(frame: pd.DataFrame) -> DataBundle`: không phụ thuộc Streamlit.
- `load_data(path: Path, mtime_ns: int, file_size: int) -> DataBundle`: cache theo đường dẫn, thời điểm và kích thước tệp; chỉ đọc các cột cần dùng.
- `category_label(field: str, code: object) -> str`: giá trị thiếu thành nhóm chưa xác định; mã chưa có nhãn vẫn có tên hiển thị chứa mã.
- Giữ các tên cột gốc cần phân tích; bổ sung `country`, `month`, `weekday`, `hour`, `is_weekend`, `severity_label`, `valid_coordinates` vào bảng vụ; liên kết hai bảng còn lại bằng `collision_index`.

- [x] Tạo `.venv` từ Python cục bộ đã có; cài Streamlit/pandas/Plotly/Pydeck/pytest tương thích. Xác nhận import thành công bằng Python trong `.venv`; ghi phiên bản vào các tệp yêu cầu. Không cài vào runtime dùng chung của Codex.
- [x] Đọc bảng mã chính thức liên kết tại [DfT open data](https://www.gov.uk/government/statistical-data-sets/road-safety-open-data); lưu các mã thực sự dùng, nhãn tiếng Việt và nguồn. Đối chiếu với mã có trong CSV 2024, đặc biệt loại phương tiện và nhóm không xác định.
- [x] Viết fixture nhỏ có ba vụ A/B/C: A có V1 với hai người P1/P2 và V2 không có thương vong; B có V3/P3 tử vong; C có V4/P4 bị thương nhẹ. Lặp thêm một dòng của A. A nghiêm trọng, B tử vong, C nhẹ; A ở England, B Wales, C Scotland.
- [x] Viết các kiểm tra ban đầu:

```python
def test_join_duplicates_and_row_order_do_not_change_counts(joined_fixture):
    first = normalize_data(joined_fixture)
    second = normalize_data(joined_fixture.sample(frac=1, random_state=7))
    for bundle in (first, second):
        assert len(bundle.collisions) == 3
        assert len(bundle.vehicles) == 4
        assert len(bundle.casualties) == 4
        assert bundle.casualties['casualty_severity'].eq(1).sum() == 1

def test_unknown_labels_remain_visible():
    assert category_label('weather_conditions', None) == 'Không xác định'
    assert '999' in category_label('weather_conditions', 999)
```

- [x] Chạy `.\.venv\Scripts\python.exe -m pytest tests/test_data.py -q` trong PowerShell; xác nhận kiểm tra thất bại vì chức năng chưa có.
- [x] Triển khai nạp và chuẩn hóa. Kiểm tra thiếu tệp/cột bắt buộc có lỗi dễ đọc; chỉ giữ thương vong thực có bản ghi; kiểm tra giá trị cấp vụ không mâu thuẫn giữa các dòng cùng khóa. Bổ sung kiểm tra giờ thiếu, tọa độ thiếu và khóa bản ghi không hợp lệ; dữ liệu vị trí/giờ thiếu vẫn giữ trong KPI.
- [x] Chạy lại `tests/test_data.py`; tất cả kiểm tra đạt và bốn tổng trên dữ liệu thật khớp Global Constraints.

## Task 2: Phép tính và dữ liệu cho sáu trang

**Files:** `road_safety/analytics.py`, `tests/test_analytics.py`, `road_safety/assets/gb-ireland.geojson`.

**Consumes:** `DataBundle`, các cột chuẩn hóa và `category_label` từ Task 1.

**Produces:**
- `FilterSpec`: dataclass gồm `start: date`, `end: date`, `countries: tuple[str, ...]`, `severities: tuple[int, ...]`, `urban_areas: tuple[int, ...]`, `police_forces: tuple[int, ...]`. Các bộ lọc dùng danh sách mã đầy đủ khi chọn tất cả; tuple rỗng nghĩa là không có kết quả.
- `filter_bundle(bundle: DataBundle, filters: FilterSpec) -> DataBundle`: lọc bảng vụ trước, lấy phương tiện/người theo tập `collision_index`.
- `headline_metrics(bundle: DataBundle) -> dict[str, int]` với các khóa `collisions`, `casualties`, `fatalities`, `vehicles`.
- `count_by(frame: pd.DataFrame, column: str, order: list | None = None) -> pd.DataFrame`: trả cột `group`, `count`; nhóm không xác định được giữ.
- `severity_by(collisions: pd.DataFrame, column: str) -> pd.DataFrame`: `group`, `severity`, `count`, `group_total`, `percentage`.
- `time_heatmap(collisions: pd.DataFrame) -> pd.DataFrame`: bảng thứ 0–6 × giờ 0–23, lấp ô không có vụ bằng 0; giờ thiếu được báo riêng.
- `day_type_summary(collisions: pd.DataFrame, start: date, end: date) -> pd.DataFrame`: `day_type`, `collisions`, `calendar_days`, `per_day`.
- `map_cells(collisions: pd.DataFrame, cell_degrees: float) -> pd.DataFrame`: tâm ô và số vụ theo mức độ, tổng bằng số vụ có tọa độ hợp lệ.
- `csv_bytes(table: pd.DataFrame) -> bytes`: UTF-8 có BOM, không xuất index nội bộ.

- [x] Viết kiểm tra `test_filter_relates_people_and_vehicles`: chọn England từ fixture cho 1 vụ, 2 phương tiện, 2 người, 0 tử vong. Chọn không có mức độ cho bốn KPI bằng 0.
- [x] Viết kiểm tra `test_day_type_denominator_includes_zero_collision_dates`: dùng A vào 01/01/2024, B vào 06/01/2024, C vào 07/01/2024; khoảng 01–07/01 có 5 ngày thường, 2 ngày cuối tuần; bình quân lần lượt 0,2 và 1,0 vụ/ngày.
- [x] Viết kiểm tra `test_severity_percentage_uses_collision_denominator`: cả ba vụ có tỷ trọng tử vong/nghiêm trọng 2/3; mỗi nhóm phần trăm cộng thành 100% khi có vụ.
- [x] Viết kiểm tra tổng số vụ trên bảng tháng/heatmap/bản đồ; một bản ghi giờ hoặc tọa độ thiếu chỉ giảm số quan sát của biểu đồ liên quan. Kiểm tra không chia cho 0; CSV có BOM và mở lại giữ nguyên nhãn tiếng Việt.
- [x] Chạy `python -m pytest tests/test_analytics.py -q` trong `.venv`, xác nhận thất bại trước triển khai.
- [x] Triển khai đúng các giao diện trên; các bảng nhóm tuổi, giới tính, vai trò và loại phương tiện dùng đúng bảng nguồn. Lấy hình học đã xác minh từ bản mẫu Natural Earth để dự phòng bản đồ; lưu nguồn và giấy phép trong README.
- [x] Chạy lại kiểm tra; đối chiếu tổng quốc gia mặc định: England 93.847, Scotland 4.167, Wales 2.913; tổng mức độ vụ: tử vong 1.502, nghiêm trọng 23.567, nhẹ 75.858.

## Task 3: Khung giao diện và sáu trang phân tích

**Files:** `app.py`, `.streamlit/config.toml`, `road_safety/charts.py`, `road_safety/ui.py`, `road_safety/assets/theme.css`, sáu tệp `views/*.py`, `tests/test_app.py`.

**Consumes:** dữ liệu, bộ lọc và các hàm tổng hợp từ Tasks 1–2.

**Produces:**
- `DashboardContext`: dataclass gồm `data: DataBundle`, `filters: FilterSpec`, `source_path: Path`.
- `render_filters(bundle: DataBundle) -> FilterSpec | None`: trạng thái đặt ở khung chung; trả `None` khi khoảng ngày chưa chọn đủ.
- `get_context() -> DashboardContext`: lấy tập dữ liệu đã lọc được entrypoint đặt vào `st.session_state['_dashboard_context']`.
- `render_header(context: DashboardContext) -> None` và `render_table_download(table: pd.DataFrame, name: str) -> None`.
- `line_chart(table: pd.DataFrame, x: str, y: str, title: str) -> plotly.graph_objects.Figure`.
- `bar_chart(table: pd.DataFrame, x: str, y: str, title: str, horizontal: bool = False) -> plotly.graph_objects.Figure`.
- `severity_chart(table: pd.DataFrame, percentage: bool) -> plotly.graph_objects.Figure`.
- `collision_map(collisions: pd.DataFrame, mode: str) -> pydeck.Deck`: mode mật độ/từng mức độ; sử dụng tất cả vụ hợp lệ hoặc tổng hợp bảo toàn số vụ.
- Mỗi tệp trang lấy `get_context()` rồi dựng nội dung của mình. Đường dẫn trang: `/`, `/thoi-gian`, `/khong-gian`, `/muc-do`, `/nguoi-phuong-tien`, `/dieu-kien`.

- [x] Viết smoke test bằng `streamlit.testing.v1.AppTest`: mở `app.py` không có exception, xuất hiện bốn KPI; chọn England rồi chuyển sang Thời gian vẫn giữ England; bỏ chọn toàn bộ mức độ cho thông báo không có kết quả; đặt lại khôi phục toàn năm và giữ trang đang xem.
- [x] Chạy `python -m pytest tests/test_app.py -q` và xác nhận thất bại trước khi có ứng dụng.
- [x] Tạo khung chung bằng `st.navigation` với sáu `st.Page`. Dùng menu gốc hoặc `st.page_link` ở thanh bên để đặt thương hiệu trước menu. Thêm bộ lọc chung và cache đọc dữ liệu; dữ liệu ngày chưa đầy đủ hoặc tập lọc rỗng có thông báo rõ ràng.
- [x] Áp dụng nền sáng, thanh bên xám nhạt và các màu trong spec. Trang Tổng quan: bốn KPI, đường theo tháng + donut (1,7:1), thanh ngang theo quốc gia + cột chồng đô thị/nông thôn (1:1), nhận xét xử lý được đồng hạng.
- [x] Trang Thời gian: tháng, giờ, heatmap thứ × giờ, ngày thường/cuối tuần với lựa chọn tổng số hoặc bình quân/ngày. Trang Không gian: bản đồ lớn, số điểm không thể hiển thị, top 10 khu vực cảnh sát và so sánh đô thị/nông thôn.
- [x] Trang Mức độ nghiêm trọng: cơ cấu số vụ, tỷ trọng theo thời gian/khu vực kèm số quan sát. Trang Người & phương tiện: tuổi, giới tính, vai trò, loại phương tiện, ghi đúng đơn vị. Trang Điều kiện: chọn một trong thời tiết/ánh sáng/mặt đường/loại đường/giới hạn tốc độ, hiển thị số vụ và cơ cấu mức độ.
- [x] Thêm bảng tổng hợp và tải CSV cho từng phân tích; ghi mẫu số tỷ trọng, nguồn và cách đếm trong phần phương pháp. Các nhận xét mô tả dữ liệu hiện tại, không tự gán nguyên nhân hoặc gọi số vụ là xác suất rủi ro.
- [x] Chạy lại các smoke test và kiểm tra biểu đồ không có lỗi với nhóm thiếu hoặc một quan sát. Thử sáu trang trong trình duyệt, giữ bộ lọc qua chuyển trang, thu gọn thanh bên và kiểm tra nhãn/tooltip ở cửa sổ rộng và hẹp.

## Task 4: Đối chiếu cuối và bàn giao bản chạy được

**Files:** `scripts/validate_data.py`, `README.md`, `run_dashboard.ps1`; cập nhật `requirements.txt` với phiên bản đã chạy thành công.

**Consumes:** toàn bộ chức năng ở Tasks 1–3.

**Produces:** lệnh chạy tái lập được, báo cáo đối chiếu dữ liệu và ứng dụng cục bộ để người dùng mở.

- [x] Viết `scripts/validate_data.py` dùng `load_data` và `headline_metrics`, so sánh khóa/số lượng với từng CSV gốc và đối chiếu phân bố mức độ. Script trả exit code khác 0 nếu có sai lệch, in kết quả tóm tắt khi đúng.
- [x] Chạy `python -m pytest -q` và `python scripts/validate_data.py` bằng `.venv`; tất cả đạt. Kiểm tra thêm tải CSV và bản đồ trên trình duyệt; nếu nền trực tuyến không khả dụng, xác nhận chế độ hình học dự phòng vẫn hiện dữ liệu.
- [x] Ghi README tiếng Việt: cách tạo môi trường, cài thư viện, chạy `streamlit run app.py`, vị trí CSV, ý nghĩa chỉ số, cách giữ bộ lọc, các nguồn và phụ thuộc mạng của nền bản đồ.
- [x] Tạo `run_dashboard.ps1` dùng đường dẫn tương đối từ chính thư mục script, kiểm tra `.venv` và CSV trước khi chạy. Cấu hình chỉ nghe trên máy cục bộ, tắt thu thập usage của Streamlit.
- [x] Chạy lại ứng dụng bằng lệnh bàn giao, xác nhận trang Tổng quan và sáu mục điều hướng hiển thị. Đưa đường dẫn mở ứng dụng và hướng dẫn chạy lại cho người dùng; ghi rõ giới hạn nào còn chưa kiểm chứng nếu có.

## Cách thực hiện đề xuất

Thực hiện trực tiếp trong cuộc trò chuyện hiện tại (Native), vì bốn công việc phụ thuộc liên tiếp vào cùng mô hình dữ liệu và cần giữ nhất quán cách đếm. Sau khi triển khai, thực hiện một lượt rà soát độc lập theo quy trình thực thi của Superpowers. Người dùng vẫn có thể chọn cách triển khai bằng các subagent cho từng công việc.

## Tài liệu kỹ thuật

- [Streamlit: tổ chức nhiều trang](https://docs.streamlit.io/develop/concepts/multipage-apps/page-and-navigation).
- [Streamlit: bộ lọc giữ trạng thái giữa các trang](https://docs.streamlit.io/develop/concepts/multipage-apps/widgets).
- [DfT: dữ liệu và bảng mã](https://www.gov.uk/government/statistical-data-sets/road-safety-open-data).
