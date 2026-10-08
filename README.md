# Hanoi Urban Health & Liveability Lakehouse (H-UVSI)

## Hệ Thống Tích Hợp Dữ Liệu Đa Chiều Giám Sát Sức Khỏe Đô Thị Hà Nội (Không Khí - Giao Thông - Sự Kiện)
> **Học phần:** Nhập môn Khoa học Dữ liệu (IT4142) – Đại học Bách Khoa Hà Nội  
> **Quy mô nhóm:** 09 thành viên | **Tỷ lệ phân công:** 11.11% / thành viên  
> **Quy mô dữ liệu:** Đạt $\ge 15.000$ dòng bản ghi thực tế qua 4 giai đoạn chuẩn mực: **Crawl $\to$ Clean $\to$ Standardize $\to$ Integrate**.

---

## 1. Ma Trận Phân Công 09 Phân Hệ Chuyên Môn (Khép Kín & Độc Lập)

| STT | Thành Viên & Vai Trò | Phân Hệ Phụ Trách | Mã Nguồn Triển Khai | Sản Phẩm Bàn Giao | % Đóng Góp |
| :---: | :--- | :--- | :--- | :--- | :---: |
| 1 | **TV 1 - Ingestion Lead** | Multi-Source Crawling Engine | `src/ingestion/` | Thu thập 32.400 dòng AQI 5 quận, Traffic & Events | 11.11% |
| 2 | **TV 2 - Governance Lead**| Data Cleaning & Quality Contracts| `src/governance/` | Xử lý missing, loại bỏ outlier & xuất Data Docs HTML | 11.11% |
| 3 | **TV 3 - Integration Lead**| Spatiotemporal Data Integration | `src/integration/` | Chuẩn hóa Timezone, EPA AQI, ghép Master $\ge 15.000$ dòng | 11.11% |
| 4 | **TV 4 - EDA Lead** | Cross-Domain Spatiotemporal EDA | `src/eda/` | Kiểm định Welch: Kẹt xe làm tăng PM2.5 ($p < 0.001$) | 11.11% |
| 5 | **TV 5 - Graph Analytics Lead**| Spatial Graph & Link Analysis | `src/graph/` | Đồ thị liên quận, PageRank điểm nóng ô nhiễm | 11.11% |
| 6 | **TV 6 - Tabular ML Lead** | Urban Health Index ML Predictor | `src/ml_tabular/` | Gradient Boosting dự báo PM2.5 & Chỉ số Sức khỏe | 11.11% |
| 7 | **TV 7 - NLP Event Lead** | Urban Incident NLP & Extraction | `src/ml_nlp/` | Phân loại mức độ nghiêm trọng từ tin tức sự kiện | 11.11% |
| 8 | **TV 8 - Evaluation Lead** | Model Evaluation & DeLong Test | `src/evaluation/` | Kiểm định DeLong ROC Test, Brier Score & Youden's J | 11.11% |
| 9 | **TV 9 - CDSS Platform Lead**| Interactive Urban Health Map | `src/cdss_app/` | Web App bản đồ tương tác đa lớp & Báo cáo LaTeX | 11.11% |

---

## 2. Cấu Trúc Thư Mục Chuẩn Doanh Nghiệp (Enterprise Layout)

```text
hanoi-urban-health-lakehouse/
├── configs/            # YAML declarative configuration files
├── data/
│   ├── 01_raw/         # Raw crawled AQI (32.400 dòng), Traffic & Events
│   ├── 02_curated/     # Cleaned data (xử lý missing, lọc outlier)
│   ├── 03_integrated/  # Master Spatiotemporal Integrated Dataset (>= 15.000 dòng)
│   └── 04_features/    # Extracted features for ML & Graph
├── src/
│   ├── ingestion/      # TV 1: Multi-source crawlers & Open-Meteo API
│   ├── governance/     # TV 2: Data cleaning, contracts & Data Docs
│   ├── integration/    # TV 3: Standardization & Spatiotemporal Join
│   ├── eda/            # TV 4: Welch's t-test & Spatiotemporal EDA
│   ├── graph/          # TV 5: Spatial NetworkX graph & PageRank
│   ├── ml_tabular/     # TV 6: Gradient Boosting AQI & Health Index
│   ├── ml_nlp/         # TV 7: Incident text parsing & NLP
│   ├── evaluation/     # TV 8: DeLong Test & Calibration
│   └── cdss_app/       # TV 9: Urban Health Map Dashboard
├── tests/              # Automated verification test suite
├── docs/               # Technical specs & reports
├── slides/             # Master presentation slide deck
├── requirements.txt    # Python dependencies
└── README.md           # Setup & execution instructions
```

---

## 3. Hướng Dẫn Cài Đặt & Chạy Kiểm Thử Toàn Diện

```bash
# 1. Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# 2. Chạy toàn bộ pipeline kiểm thử tự động
$env:PYTHONPATH="C:\Users\PC\Desktop\KHDL\hanoi-urban-health-lakehouse"; pytest hanoi-urban-health-lakehouse/tests/ -v
```