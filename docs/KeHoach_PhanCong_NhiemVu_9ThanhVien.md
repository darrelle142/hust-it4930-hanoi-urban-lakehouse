# KẾ HOẠCH TOÀN DIỆN TRIỂN KHAI BÀI TẬP LỚN (IT4142)
## Đề tài: Bản Đồ Sức Khỏe Đô Thị Hà Nội (H-UVSI): Thu Thập Đa Nguồn, Quản Trị Lakehouse, Mô Hình Hóa Học Máy & Hỗ Trợ Quyết Định Can Thiệp Sớm
**Nhóm Nghiên cứu Đô thị Thông minh -- Trường CNTT&TT (SOICT), Đại học Bách khoa Hà Nội**  
*Quy mô nhóm: 09 sinh viên | Phân bổ đóng góp: 11.11% / thành viên | Năm học: 2024 -- 2025*

---

## 1. NGUYÊN TẮC ĐÁNH GIÁ VÀ BẢO VỆ ĐỒ ÁN (CHỈ ĐẠO TỪ GIẢNG VIÊN)
1. **Đánh giá cá nhân trên sản phẩm nhóm:** Giảng viên thực hiện vấn đáp và chấm điểm hoàn toàn độc lập cho từng cá nhân. Điểm số phụ thuộc vào mức độ hiểu bản chất toán học, khả năng giải trình dòng lệnh (line-by-line code) và ý nghĩa thực tế trong phần phụ trách.
2. **Cấu trúc 09 phân hệ độc lập & khép kín (End-to-End):** Phân chia đều $11.11\%$ khối lượng cho 9 thành viên (TV 1 đến TV 9).
3. **Nghiêm cấm chia việc thụ động:** Tuyệt đối không có chuyện “chỉ vẽ slide” hay “chỉ làm word”. Mỗi người phải tự nắm lý thuyết, viết code, vẽ biểu đồ, viết báo cáo chương mình và độc lập trả lời phản biện.
4. **Tính thực chất & liên kết hữu cơ:** Dữ liệu và mô hình phải giải quyết vấn đề thực tế, không dùng mô hình phức tạp một cách hình thức.

---

## 2. MA TRẬN PHÂN CÔNG TỔNG THỂ (11.11% / THÀNH VIÊN)

| STT | Thành viên | Phân hệ kỹ thuật phụ trách | File mã nguồn | Đầu vào (Input) | Đầu ra (Output) | % Đóng góp |
| :---: | :--- | :--- | :--- | :--- | :--- | :---: |
| 1 | **TV 1** (Trưởng nhóm) | Multi-Source Crawling Engine | `src/ingestion/urban_crawler.py` | API Open-Meteo, VOV News | Dữ liệu thô `data/01_raw/` (21.800+ dòng) | **11.11%** |
| 2 | **TV 2** | Data Cleaning & Quality Governance | `src/governance/data_cleaner.py` | `data/01_raw/` từ TV 1 | Dữ liệu sạch `data/02_curated/`, Báo cáo Data Docs HTML | **11.11%** |
| 3 | **TV 3** | Spatiotemporal Data Integration | `src/integration/spatiotemporal_integrator.py` | `data/02_curated/` từ TV 2 | Master Dataset `data/03_integrated/` (**10.861 dòng**) | **11.11%** |
| 4 | **TV 4** | Spatiotemporal EDA & Welch's t-test | `src/eda/urban_eda.py` | Master Dataset từ TV 3 | Kết quả kiểm định Welch $p < 0.001$, Bảng Table 1 | **11.11%** |
| 5 | **TV 5** | Spatial Graph & PageRank Hotspots | `src/graph/spatial_graph.py` | Cấu trúc không gian 5 quận | Đồ thị NetworkX, Điểm PageRank Hotspots | **11.11%** |
| 6 | **TV 6** | Tabular Machine Learning Predictor | `src/ml_tabular/health_predictor.py` | Master Dataset từ TV 3 | Gradient Boosting Regressor $R^2 > 0.40$ & Classifier | **11.11%** |
| 7 | **TV 7** | Incident NLP & Text Mining | `src/ml_nlp/event_parser.py` | Tin tức sự cố từ TV 1 | NER trích xuất địa danh, Severity Impact Score | **11.11%** |
| 8 | **TV 8** | Model Evaluation & DeLong ROC Test | `src/evaluation/urban_evaluator.py` | Xác suất dự báo từ TV 6 | Kiểm định DeLong Test, Brier score, Ngưỡng Youden's J | **11.11%** |
| 9 | **TV 9** | CDSS Web App & Master Storytelling | `src/cdss_app/urban_health_app.py` | Đầu ra của cả 8 bạn | Web App tính điểm đáng sống, Mô phỏng chính sách What-If | **11.11%** |

---

## 3. CHI TIẾT NHIỆM VỤ, TOÁN HỌC & CÂU HỎI VẤN ĐÁP CHO TỪNG BẠN

### THÀNH VIÊN 1: Multi-Source Crawling Engine (Nhóm trưởng)
* **File phụ trách:** `src/ingestion/urban_crawler.py`
* **Nhiệm vụ:** Viết pipeline gọi Open-Meteo REST API thu thập bụi mịn PM2.5, PM10, CO, NO2 theo giờ cho 5 quận Hà Nội; viết scraper cào tin tai nạn/ngập úng từ VOV Giao thông; cố tình giữ lại các lỗi thực tế (nhiễu cảm biến -999, rớt mạng missing, trùng lặp 15 bản ghi) để TV 2 có dữ liệu làm sạch.
* **Đầu ra:** `data/01_raw/air_quality_raw.csv` (10.935 dòng), `traffic_raw.csv` (10.930 dòng), `vov_live_incidents.csv` (25 tin), `events_raw.csv`.
* **Câu hỏi vấn đáp mẫu:**
  * *Hỏi:* Tại sao em không tải dữ liệu tĩnh trên Kaggle mà phải xây dựng pipeline cào đa nguồn?
  * *Đáp:* Dữ liệu tĩnh trên mạng bị cũ, tách rời các chiều và không có tính thực nghiệm. Em cào trực tiếp từ Open-Meteo và VOV Giao thông để đồng bộ hóa nồng độ bụi và vận tốc xe theo từng giờ tại đúng 5 quận Hà Nội. Dữ liệu thô cào về giữ nguyên các lỗi thực tế (mã lỗi -999, rớt gói tin) để phân hệ tiền xử lý của TV 2 có cơ sở làm việc chuẩn mực.

---

### THÀNH VIÊN 2: Data Cleaning & Quality Governance
* **File phụ trách:** `src/governance/data_cleaner.py`
* **Nhiệm vụ:** Khử trùng lặp trên cặp khóa `[timestamp, district_id]`; lọc bỏ triệt để 59 dòng chứa mã lỗi cảm biến $-999.0$ và đột biến $> 500\,\mu\text{g/m}^3$; nội suy điền khuyết thiếu; tự động sinh báo cáo kiểm toán HTML.
* **Đầu ra:** `data/02_curated/air_quality_curated.csv` (10.861 dòng sạch), `traffic_curated.csv`, và báo cáo trực quan `docs/data_docs/urban_health_data_docs.html`.
* **Câu hỏi vấn đáp mẫu:**
  * *Hỏi:* Dữ liệu thô bị bẩn ở chỗ nào và thuật toán của em đã xử lý ra sao?
  * *Đáp:* Dữ liệu thô có 15 dòng trùng lặp do retry mạng, 59 dòng chứa mã lỗi cảm biến -999.0 hoặc xung điện > 500 ug/m3, và khoảng 2.5% ô trống. Thuật toán của em đã khử trùng lặp, loại bỏ 59 ngoại lai vật lý và điền khuyết bằng kỳ vọng có điều kiện, xuất báo cáo Data Docs HTML chứng minh kết quả.

---

### THÀNH VIÊN 3: Spatiotemporal Multi-Source Integration
* **File phụ trách:** `src/integration/spatiotemporal_integrator.py`
* **Nhiệm vụ:** Thực hiện Spatiotemporal Inner Join giữa Không khí và Giao thông trên cặp khóa `[timestamp, district_id]`; chuẩn hóa phân cấp US EPA AQI Categories; tính Chỉ số Áp lực Đô thị:
  $$\text{UVSI} = 0.6 \times \frac{\text{PM2.5}}{150} \times 100 + 0.4 \times \frac{\text{Jam\_Factor}}{10} \times 100$$
* **Đầu ra:** `data/03_integrated/master_urban_health.csv` (**10.861 dòng bản ghi** -- vượt chỉ tiêu $\ge 10.000$ dòng của Thầy).
* **Câu hỏi vấn đáp mẫu:**
  * *Hỏi:* Độ phức tạp của phép ghép bảng không-thời gian là bao nhiêu?
  * *Đáp:* Em sử dụng thuật toán Hash Join đa luồng của Polars trên cặp khóa [timestamp, district_id] với độ phức tạp O(N + M), ghép hơn 10.000 dòng chỉ mất chưa đầy 30 mili-giây.

---

### THÀNH VIÊN 4: Spatiotemporal EDA & Hypothesis Testing
* **File phụ trách:** `src/eda/urban_eda.py`
* **Nhiệm vụ:** Phân tích khám phá dữ liệu, vẽ biểu đồ phân phối; thực hiện **Kiểm định giả thuyết Welch's t-test**:
  $$t = \frac{\bar{X}_1 - \bar{X}_2}{\sqrt{\frac{s_1^2}{n_1} + \frac{s_2^2}{n_2}}}$$
  chứng minh nồng độ bụi vào giờ cao điểm tăng vọt có ý nghĩa thống kê ($p < 0.001$); tính ma trận tương quan Pearson.
* **Đầu ra:** Báo cáo kiểm định $p$-value, ma trận tương quan và bảng Table 1 thống kê theo quận.
* **Câu hỏi vấn đáp mẫu:**
  * *Hỏi:* Tại sao dùng Welch's t-test thay cho Student's t-test cổ điển?
  * *Đáp:* Vì dữ liệu giờ cao điểm có phương sai biến thiên lớn hơn nhiều so với giờ bình thường (vi phạm giả định phương sai đồng nhất). Welch's t-test hiệu chỉnh bậc tự do Welch-Satterthwaite, kiểm soát sai lầm loại I chuẩn xác mà không đòi hỏi phương sai bằng nhau.

---

### THÀNH VIÊN 5: Spatial Graph & Link Analysis
* **File phụ trách:** `src/graph/spatial_graph.py`
* **Nhiệm vụ:** Xây dựng đồ thị liên kết không gian 5 quận bằng `networkx`; ứng dụng thuật toán **PageRank có trọng số**:
  $$\text{PR}(u) = \frac{1-d}{|V|} + d \sum_{v \in \text{In}(u)} \frac{W(v, u)}{\sum W(v, k)} \text{PR}(v)$$
  để tìm ra quận đóng vai trò "Hub ô nhiễm" lớn nhất; tính Betweenness Centrality.
* **Đầu ra:** Bảng xếp hạng điểm PageRank Hotspot (xác định Cầu Giấy và Đống Đa là 2 điểm nóng trung tâm nhất).
* **Câu hỏi vấn đáp mẫu:**
  * *Hỏi:* Ý tưởng ánh xạ PageRank từ web sang ô nhiễm đô thị là gì?
  * *Đáp:* Một quận là Hub ô nhiễm nếu nhận luồng phương tiện và hướng gió mang bụi từ nhiều quận tiếp giáp đổ dồn về. PageRank phân bổ ngẫu nhiên có trọng số giúp lượng hóa chính xác mức độ tích tụ lan truyền rủi ro.

---

### THÀNH VIÊN 6: Tabular Machine Learning Predictor
* **File phụ trách:** `src/ml_tabular/health_predictor.py`
* **Nhiệm vụ:** Phân chia Train/Test theo chuỗi thời gian; huấn luyện `GradientBoostingRegressor` dự báo bụi PM2.5 ($R^2 > 0.40$); huấn luyện `GradientBoostingClassifier` dự báo nguy cơ Báo động Đỏ ($\text{UVSI} \ge 60$); trích xuất Feature Importance.
* **Đầu ra:** Trọng số mô hình và vector xác suất dự báo bàn giao cho TV 8.
* **Câu hỏi vấn đáp mẫu:**
  * *Hỏi:* Mô hình của em có ứng dụng thực tế gì hay chỉ dự báo con số trừu tượng?
  * *Đáp:* Mô hình giải quyết 3 bài toán cụ thể: (1) Tư vấn người dân chọn giờ tập thể dục an toàn và đeo khẩu trang N95 trước 3-6 tiếng; (2) Cảnh báo sớm 24h nguy cơ quá tải bệnh nhi cho bệnh viện hô hấp; (3) Cung cấp cỗ máy What-If cho CSGT: nếu giảm 30% kẹt xe ở Cầu Giấy thì PM2.5 giảm bao nhiêu ug/m3.

---

### THÀNH VIÊN 7: Incident NLP & Text Mining
* **File phụ trách:** `src/ml_nlp/event_parser.py`
* **Nhiệm vụ:** Khai phá văn bản tin tức sự cố VOV Giao thông; xây dựng bộ trích xuất thực thể địa danh (NER) dựa trên Gazetteer các tuyến đường huyết mạch; phân loại mức độ rủi ro sự cố.
* **Đầu ra:** Danh mục sự cố đã được bóc tách vị trí quận và gán điểm tác động tức thời.
* **Câu hỏi vấn đáp mẫu:**
  * *Hỏi:* Khi bản tin chỉ có tên đường (Chùa Bộc, Cầu Giấy) mà không có tên quận, em định vị thế nào?
  * *Đáp:* Em xây dựng từ điển địa danh phân cấp (Gazetteer) ánh xạ các tuyến phố, ngã tư về quận hành chính tương ứng (Chùa Bộc -> Đống Đa; Duy Tân, Xuân Thủy -> Cầu Giấy) với độ chính xác cao.

---

### THÀNH VIÊN 8: Model Evaluation & DeLong ROC Test
* **File phụ trách:** `src/evaluation/urban_evaluator.py`
* **Nhiệm vụ:** Vẽ đường cong ROC-AUC; thực hiện **Kiểm định phi tham số DeLong Test** dựa trên cấu trúc U-statistics:
  $$Z = \frac{\widehat{\text{AUC}}_1 - \widehat{\text{AUC}}_2}{\sqrt{\mathbb{V}\text{ar}(\widehat{\text{AUC}}_1 - \widehat{\text{AUC}}_2)}} \sim \mathcal{N}(0, 1)$$
  chứng minh mô hình tích hợp đa nguồn vượt trội hơn mô hình cơ sở ($p < 0.05$); tối ưu ngưỡng cắt theo chỉ số **Youden's J**: $J = \max \{\text{Sens} + \text{Spec} - 1\}$.
* **Đầu ra:** Bộ chỉ số thẩm định (AUC, Brier score, p-value của DeLong test, ngưỡng Youden's J tối ưu).
* **Câu hỏi vấn đáp mẫu:**
  * *Hỏi:* Bản chất toán học của kiểm định DeLong là gì?
  * *Đáp:* Khi mô hình A có AUC cao hơn mô hình B, sự chênh lệch có thể do ngẫu nhiên lấy mẫu. Kiểm định DeLong sử dụng U-statistics tính ma trận hiệp phương sai tiệm cận của hai đường cong trên cùng tập test để tính Z-score và p-value chính xác mà không cần giả định phân phối chuẩn.

---

### THÀNH VIÊN 9: CDSS Web Application & Master Storytelling
* **File phụ trách:** `src/cdss_app/urban_health_app.py` và `docs/KeHoach_PhanCong_NhiemVu_9ThanhVien.tex`
* **Nhiệm vụ:** Xây dựng cỗ máy hỗ trợ ra quyết định lâm sàng đô thị (CDSS); tính Điểm Đáng Sống Đô Thị (Liveability Score: $0 \to 100$); lập trình mô phỏng chính sách What-If (*"Nếu giảm 30% kẹt xe thì nồng độ bụi giảm bao nhiêu và điểm đáng sống tăng bao nhiêu"*); chủ trì dàn trang toàn văn báo cáo LaTeX và bộ Slide chung.
* **Đầu ra:** Giao diện CDSS tương tác và tập file báo cáo/slide bảo vệ hoàn chỉnh của cả nhóm.
* **Câu hỏi vấn đáp mẫu:**
  * *Hỏi:* Mô phỏng chính sách What-If hoạt động như thế nào?
  * *Đáp:* Khi người dùng kéo thanh trượt giảm kẹt xe (ví dụ giảm 30% tại Cầu Giấy), hệ thống nạp tham số mới vào mô hình dự báo của TV 6 để ước tính mức PM2.5 mới, từ đó tính ra mức cải thiện điểm Liveability (tăng từ 52 lên 68 điểm), giúp cơ quan quản lý thấy ngay lợi ích định lượng của chính sách can thiệp.

---

## 4. CHIẾN THUẬT VẤN ĐÁP 3 BƯỚC (120 GIÂY) CHO TẤT CẢ THÀNH VIÊN
1. **Bước 1 (30s) -- Bản chất toán học / thống kê:**  
   *“Thưa thầy, cơ sở lý thuyết cốt lõi trong phần của em là [Công thức / Định lý / Thuật toán], nhằm giải quyết câu hỏi nghiệp vụ đô thị là [...]”*
2. **Bước 2 (45s) -- Giải trình dòng lệnh mã nguồn:**  
   *“Em đã trực tiếp lập trình giải thuật này tại tệp tin `src/.../tên_file.py`, sử dụng [thư viện tối ưu] và giải quyết bài toán hiệu năng ở điểm [...]”*
3. **Bước 3 (45s) -- Ý nghĩa biểu đồ & Giá trị thực tế:**  
   *“Kết quả trực quan thu được thể hiện trên biểu đồ [Tên biểu đồ]. Con số này chứng minh cho người dân và cơ quan quản lý đô thị thấy rằng [...]”*
