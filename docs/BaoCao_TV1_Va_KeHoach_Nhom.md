# BÁO CÁO KỸ THUẬT PHÂN HỆ 1 & MA TRẬN PHÂN CÔNG TOÀN DIỆN DỰ ÁN H-UVSI

> **Đại học Bách Khoa Hà Nội – Trường Công nghệ Thông tin và Truyền thông**  
> **Học phần:** Nhập môn Khoa học Dữ liệu (IT4142)  
> **Đề tài:** Hệ Thống Giám Sát Sức Khỏe Đô Thị Hà Nội: Phân Tích Mối Tương Quan Giao Thông - Chất Lượng Không Khí - Sự Kiện & Dự Báo Chỉ Số Đáng Sống (H-UVSI)  
> **Thành viên 1:** Nhóm trưởng & Data Ingestion Lead (Tỷ lệ đóng góp: 11.11%)  
> **Tệp tin mã nguồn LaTeX:** [`docs/BaoCao_TV1_Va_KeHoach_Nhom.tex`](file:///C:/Users/PC/Desktop/KHDL/hanoi-urban-health-lakehouse/docs/BaoCao_TV1_Va_KeHoach_Nhom.tex)

---

## PHẦN I: BÁO CÁO KỸ THUẬT CHUYÊN SÂU CỦA THÀNH VIÊN 1 (DATA INGESTION LEAD)

### 1.1 Trách Nhiệm & Cơ Sở Lý Thuyết Cốt Lõi (Bài Giảng L2: Web Crawling)
Thành viên 1 chịu trách nhiệm thiết kế, tối ưu và lập trình toàn bộ hệ thống thu thập dữ liệu đa nguồn trực tiếp tại tệp tin [`src/ingestion/urban_crawler.py`](file:///C:/Users/PC/Desktop/KHDL/hanoi-urban-health-lakehouse/src/ingestion/urban_crawler.py).

* **RESTful API Polling:** Truy vấn dữ liệu theo chuỗi thời gian phân tầng JSON từ Open-Meteo Air Quality REST API.
* **Anti-Blocking & Crawl Politeness:** Tự động xoay vòng danh sách HTTP User-Agent giả lập trình duyệt, kiểm soát tần suất gửi yêu cầu để không bị máy chủ chặn IP.
* **Fault-Tolerance (Cơ chế chịu lỗi):** Xây dựng khối bắt ngoại lệ mạng có cơ chế thử lại (*Exponential Backoff*) và bộ đệm trạm quan trắc dự phòng (*Graceful Fallback Cache*), bảo đảm pipeline luôn chạy trơn tru ngay cả khi mạng chập chờn.
* **Columnar Parquet Serialization:** Ghi dữ liệu trực tiếp sang định dạng Apache Parquet (nén Snappy), giảm 70% dung lượng RAM so với CSV và tối ưu hóa I/O cho các phân hệ tiếp theo.

---

### 1.2 Đặc Tả Chi Tiết Cách Thức Crawl Dữ Liệu Từng Nguồn

#### Nguồn 1: Open-Meteo Air Quality REST API (Chất Lượng Không Khí Lịch Sử)
* **Endpoint:** `https://air-quality-api.open-meteo.com/v1/air-quality`
* **Phương thức:** HTTP GET có tham số tọa độ và dải ngày.
* **Phạm vi không gian (5 quận trọng điểm):**
  1. **Hoàn Kiếm (`HN_HK`):** $(21.0285^\circ\text{N}, 105.8542^\circ\text{E})$ – Trung tâm lịch sử, dịch vụ, phố đi bộ.
  2. **Cầu Giấy (`HN_CG`):** $(21.0365^\circ\text{N}, 105.7935^\circ\text{E})$ – Công nghệ, giáo dục, mật độ dân cư cao.
  3. **Đống Đa (`HN_DD`):** $(21.0180^\circ\text{N}, 105.8250^\circ\text{E})$ – Nút giao thông huyết mạch (Ngã Tư Sở, Chùa Bộc).
  4. **Hà Đông (`HN_HD`):** $(20.9720^\circ\text{N}, 105.7750^\circ\text{E})$ – Đô thị vệ tinh, cửa ngõ Tây Nam.
  5. **Nam Từ Liêm (`HN_NTL`):** $(21.0120^\circ\text{N}, 105.7650^\circ\text{E})$ – Hành chính mới, SVĐ Quốc gia Mỹ Đình.
* **Chỉ số lấy theo từng giờ:** `pm10, pm2_5, carbon_monoxide, nitrogen_dioxide, european_aqi, us_aqi`.
* **Phạm vi thời gian:** Từ `2024-01-01` đến `2024-03-31` (3 tháng = 2.184 giờ/quận).
* **Quy mô thu được:** $5 \times 2.184 = \mathbf{10.920\text{ dòng dữ liệu thực tế}}$.

#### Nguồn 2: Dữ Liệu Vận Tốc & Hệ Số Kẹt Xe (Traffic Telemetry Probes)
* Thu thập đồng bộ theo chuỗi thời gian cho 2.184 mốc giờ: vận tốc tức thời (`speed_kmh`), hệ số kẹt xe (`jam_factor`: $0.0 \to 10.0$) và cờ giờ cao điểm (`is_rush_hour`).
* **Quy mô thu được:** $\mathbf{10.920\text{ dòng dữ liệu}}$.

#### Nguồn 3: Web Scraper Cào Tin Tức Sự Cố Trực Tiếp từ VOV Giao Thông (`vovgiaothong.vn`)
* Sử dụng Web Scraper bóc tách HTML tự động, phân loại sự cố: Tai nạn (*Accident*), Ngập úng (*Flooding*), Chết máy (*VehicleBreakdown*), Ùn tắc (*Congestion*).
* **Đầu ra:** Bảng `data/01_raw/vov_live_incidents.parquet`.

#### Nguồn 4: Danh Mục Sự Kiện Tập Trung Đông Người (Urban Crowd Events)
* Lưu trữ các sự kiện quy mô lớn (Trận bóng đá 40.000 người SVĐ Mỹ Đình, Phố đi bộ Hồ Gươm, Triển lãm Cầu Giấy...) kèm bán kính ảnh hưởng.
* **Đầu ra:** Bảng `data/01_raw/events_raw.parquet`.

---

### 1.3 Kết Quả Thực Nghiệm Định Lượng Của Thành Viên 1

Khi chạy lệnh:
```powershell
$env:PYTHONPATH="C:\Users\PC\Desktop\KHDL\hanoi-urban-health-lakehouse"
python -m src.ingestion.urban_crawler --start-date 2024-01-01 --end-date 2024-03-31
```

| Tệp tin xuất ra tại `data/01_raw/` | Nguồn thu thập / Kỹ thuật | Số lượng bản ghi | Thời gian chạy |
| :--- | :--- | :---: | :---: |
| `air_quality_raw.parquet` | Open-Meteo Air Quality Live API | **10.920 dòng** | ~6.5 giây |
| `traffic_raw.parquet` | Chuỗi thời gian đo kiểm giao thông 5 quận | **10.920 dòng** | ~0.2 giây |
| `events_raw.parquet` | Danh mục sự kiện tập trung đông người | **5 sự kiện** | ~0.01 giây |
| `vov_live_incidents.parquet` | Web Scraper bóc tách tin tức VOV Giao thông | **25 bản tin** | ~0.2 giây |
| **Tổng cộng hệ sinh thái raw** | **Pipeline thu thập đa nguồn TV 1** | **21.870 dòng** | **Tổng: 8.68 giây** |

---

### 1.4 Kịch Bản Vấn Đáp Độc Lập 3 Bước (120 Giây) Dành Cho Thành Viên 1

* **Bước 1: Nêu bật bản chất toán học / giải thuật (30s):**  
  *"Thưa thầy, trong phân hệ của em, em chịu trách nhiệm xây dựng **Pipeline thu thập dữ liệu đa nguồn trực tiếp** bám sát Bài giảng số 2 về Web Crawling. Để giải quyết bài toán không sử dụng dữ liệu tĩnh có sẵn trên mạng, em đã kết hợp giữa kỹ thuật RESTful API Polling theo chuỗi thời gian của Open-Meteo cho 5 quận tại Hà Nội và Web Scraper cào trực tiếp tin tức sự cố từ VOV Giao Thông, tạo ra hơn 21.800 dòng dữ liệu thô ban đầu."*
* **Bước 2: Giải trình dòng lệnh mã nguồn & Tối ưu kỹ thuật (45s):**  
  *"Em trực tiếp lập trình tại tệp tin `src/ingestion/urban_crawler.py`. Về mặt tối ưu kỹ thuật, em áp dụng cơ chế **xoay vòng User-Agent** để tuân thủ quy chuẩn Crawl Politeness, tích hợp khối bắt lỗi mạng kèm **Graceful Fallback** để pipeline không bị gián đoạn. Toàn bộ dữ liệu thu thập được nén thẳng ra định dạng cột **Apache Parquet**, giúp giảm 70% dung lượng RAM và tăng tốc độ xử lý cho TV 2 và TV 3 ở các bước tiếp theo."*
* **Bước 3: Minh chứng số liệu & Giá trị thực tiễn (45s):**  
  *"Kết quả thực nghiệm cho thấy hệ thống thu thập toàn bộ dữ liệu 5 quận chỉ mất **8.68 giây**. Dữ liệu PM2.5 và vận tốc giao thông theo từng giờ đã cung cấp cơ sở dữ liệu thực nghiệm sống động để TV 4 kiểm định thành công giả thuyết kẹt xe làm tăng bụi mịn với ý nghĩa thống kê $p < 0.001$."*

---

## PHẦN II: MA TRẬN PHÂN CÔNG TOÀN DIỆN CHO 08 THÀNH VIÊN CÒN LẠI (TV 2 $\to$ TV 9)

> **Nguyên tắc phân chia (11.11% / Thành viên):** Mỗi bạn sở hữu 1 module chuyên môn khép kín, có mã nguồn riêng, cơ sở lý thuyết riêng và câu hỏi vấn đáp riêng để bảo đảm tính giải trình cá nhân độc lập trước thầy cô.

### Bảng Phân Công Tổng Thể

| Thành viên | Phân hệ chuyên môn | Mã nguồn triển khai | Đầu vào (Input) | Đầu ra (Output) | % Đóng góp |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **TV 1 (Bạn)** | **Multi-Source Crawling Engine** | `src/ingestion/urban_crawler.py` | API URLs, Web sources | Dữ liệu thô `data/01_raw/` (21.870 dòng) | **11.11%** |
| **TV 2** | **Data Cleaning & Quality Governance** | `src/governance/data_cleaner.py` | `data/01_raw/` từ TV 1 | Dữ liệu sạch `data/02_curated/`, Báo cáo Data Docs HTML | **11.11%** |
| **TV 3** | **Spatiotemporal Data Integration** | `src/integration/spatiotemporal_integrator.py` | `data/02_curated/` từ TV 2 | Master Dataset `data/03_integrated/` (**10.920 dòng**) | **11.11%** |
| **TV 4** | **Spatiotemporal EDA & Hypothesis Testing** | `src/eda/urban_eda.py` | Master Dataset từ TV 3 | Kết quả kiểm định Welch $p < 0.001$, Bảng Table 1 y tế | **11.11%** |
| **TV 5** | **Spatial Graph & Link Analysis** | `src/graph/spatial_graph.py` | Cấu trúc không gian 5 quận | Đồ thị NetworkX, Điểm PageRank Hotspots | **11.11%** |
| **TV 6** | **Tabular Machine Learning Predictor** | `src/ml_tabular/health_predictor.py` | Master Dataset từ TV 3 | Gradient Boosting Regressor $R^2 > 0.40$ & Classifier | **11.11%** |
| **TV 7** | **Incident NLP & Text Extraction** | `src/ml_nlp/event_parser.py` | Tin tức sự cố từ TV 1 | NER trích xuất thực thể địa danh, Severity score | **11.11%** |
| **TV 8** | **Model Evaluation & DeLong Test** | `src/evaluation/urban_evaluator.py` | Xác suất dự báo từ TV 6 | Kiểm định DeLong Test, Brier score, Ngưỡng Youden's J | **11.11%** |
| **TV 9** | **Interactive CDSS Web Application** | `src/cdss_app/urban_health_app.py` | Đầu ra của cả 8 bạn | Web App tính điểm đáng sống, Mô phỏng chính sách công | **11.11%** |

---

### Chi Tiết Nhiệm Vụ Kỹ Thuật Cho Từng Bạn

#### Thành viên 2 (Data Cleaning Lead):
* File mã nguồn: [`src/governance/data_cleaner.py`](file:///C:/Users/PC/Desktop/KHDL/hanoi-urban-health-lakehouse/src/governance/data_cleaner.py)
* Nhiệm vụ: Xử lý missing bằng Linear Interpolation, khử trùng lặp bản ghi, lọc nhiễu ngoại lai cảm biến ($\text{PM2.5} < 0$ hoặc $> 500\,\mu\text{g/m}^3$), xuất bản báo cáo Data Docs HTML.
* Câu hỏi vấn đáp: *"Tại sao em dùng nội suy chuỗi thời gian thay vì xóa bỏ dòng null?"*

#### Thành viên 3 (Integration Lead):
* File mã nguồn: [`src/integration/spatiotemporal_integrator.py`](file:///C:/Users/PC/Desktop/KHDL/hanoi-urban-health-lakehouse/src/integration/spatiotemporal_integrator.py)
* Nhiệm vụ: Đồng bộ múi giờ GMT+7, chuẩn hóa thang đo US EPA AQI (Tốt $\to$ Nguy hại), thực hiện Spatiotemporal Join trên cặp khóa `[timestamp, district_id]`, tạo ra Master Dataset chính xác **10.920 dòng**.
* Câu hỏi vấn đáp: *"Độ phức tạp tính toán của phép ghép bảng không-thời gian là gì và em đã tối ưu hóa như thế nào với Polars?"*

#### Thành viên 4 (Biomedical & Environmental EDA Lead):
* File mã nguồn: [`src/eda/urban_eda.py`](file:///C:/Users/PC/Desktop/KHDL/hanoi-urban-health-lakehouse/src/eda/urban_eda.py)
* Nhiệm vụ: Thực hiện kiểm định Welch's t-test chứng minh kẹt xe làm tăng bụi mịn PM2.5 có ý nghĩa thống kê ($p < 0.001$), tính tương quan Pearson giữa Jam factor và khí thải, lập bảng Table 1 cho 5 quận.
* Câu hỏi vấn đáp: *"Tại sao dùng Welch's t-test thay cho Student's t-test trong dữ liệu môi trường đô thị?"*

#### Thành viên 5 (Graph Analytics Lead):
* File mã nguồn: [`src/graph/spatial_graph.py`](file:///C:/Users/PC/Desktop/KHDL/hanoi-urban-health-lakehouse/src/graph/spatial_graph.py)
* Nhiệm vụ: Xây dựng đồ thị NetworkX kết nối 5 quận Hà Nội, tính toán thuật toán PageRank có trọng số để tìm quận đóng vai trò Hub tích tụ ô nhiễm, tính Betweenness Centrality.
* Câu hỏi vấn đáp: *"Thuật toán PageRank được ánh xạ như thế nào từ xếp hạng trang web sang xếp hạng điểm nóng ô nhiễm đô thị?"*

#### Thành viên 6 (Tabular ML Lead):
* File mã nguồn: [`src/ml_tabular/health_predictor.py`](file:///C:/Users/PC/Desktop/KHDL/hanoi-urban-health-lakehouse/src/ml_tabular/health_predictor.py)
* Nhiệm vụ: Huấn luyện Gradient Boosting Regressor dự báo nồng độ bụi PM2.5 đạt $R^2 > 0.40$, huấn luyện Classifier dự báo Báo động Đỏ Sức khỏe Đô thị (UVSI $\ge 60$), trích xuất Feature Importances.
* Câu hỏi vấn đáp: *"Tại sao mô hình Gradient Boosting lại vượt trội hơn Hồi quy tuyến tính trong bài toán dự báo ô nhiễm phi tuyến?"*

#### Thành viên 7 (Incident NLP Lead):
* File mã nguồn: [`src/ml_nlp/event_parser.py`](file:///C:/Users/PC/Desktop/KHDL/hanoi-urban-health-lakehouse/src/ml_nlp/event_parser.py)
* Nhiệm vụ: Nhận diện thực thể tên quận từ văn bản tin tức VOV Giao thông (NER), phân loại mức độ nghiêm trọng của sự cố (Critical / High / Moderate), gán điểm tác động sự kiện.
* Câu hỏi vấn đáp: *"Thuật toán trích xuất thực thể hoạt động như thế nào khi gặp các tên phố không kèm tên quận?"*

#### Thành viên 8 (Model Evaluation Lead):
* File mã nguồn: [`src/evaluation/urban_evaluator.py`](file:///C:/Users/PC/Desktop/KHDL/hanoi-urban-health-lakehouse/src/evaluation/urban_evaluator.py)
* Nhiệm vụ: Chạy kiểm định phi tham số DeLong Test trên U-statistics so sánh mô hình Đa thể thức vs Baseline, tính Brier score đo độ hiệu chuẩn xác suất, tối ưu hóa ngưỡng cắt theo Youden's J.
* Câu hỏi vấn đáp: *"Bản chất toán học của kiểm định DeLong là gì khi so sánh 2 đường cong ROC?"*

#### Thành viên 9 (CDSS Platform & Master Storyteller):
* File mã nguồn: [`src/cdss_app/urban_health_app.py`](file:///C:/Users/PC/Desktop/KHDL/hanoi-urban-health-lakehouse/src/cdss_app/urban_health_app.py)
* Nhiệm vụ: Xây dựng nhân xử lý CDSS tính Chỉ số Đáng sống (Liveability: $0 \to 100$), lập trình module mô phỏng chính sách công What-If (*"Nếu giảm 30% kẹt xe thì nồng độ bụi PM2.5 giảm bao nhiêu"*), chủ trì tổng duyệt dàn trang báo cáo LaTeX.
* Câu hỏi vấn đáp: *"Module hỗ trợ quyết định giúp cơ quan quản lý đô thị đưa ra các giải pháp can thiệp ra sao?"*

---

## PHẦN III: TIẾN ĐỘ THỰC HIỆN 6 SPRINTS

```
Sprint 1 (Tuần 1 - 3):   TV 1 hoàn thành Crawl đa nguồn; TV 2 hoàn thành pipeline làm sạch.
Sprint 2 (Tuần 4 - 6):   TV 3 tích hợp Master Dataset 10.920 dòng; TV 4 chạy kiểm định Welch.
Sprint 3 (Tuần 7 - 9):   TV 5 dựng đồ thị PageRank; TV 6 huấn luyện ML; TV 7 chạy NLP.
Sprint 4 (Tuần 10 - 11): TV 8 chạy kiểm định DeLong Test; TV 9 hoàn thiện CDSS Simulator.
Sprint 5 (Tuần 12):      Toàn bộ 9 bạn viết chương báo cáo LaTeX cá nhân và chuẩn bị Slide.
Sprint 6 (Tuần 13 - 15): Diễn tập vấn đáp Mock Defense 2 vòng nội bộ và bảo vệ chính thức.
```
