"""
Bộ kiểm thử tự động toàn diện dự án Bản Đồ Sức Khỏe Đô Thị Hà Nội (H-UVSI - IT4142)
Kiểm tra độ chính xác kỹ thuật của 09 phân hệ và xác minh quy mô Master Dataset đạt >= 10.000 dòng!
"""

import os
import pytest
import numpy as np
import polars as pl

from src.ingestion.urban_crawler import HanoiUrbanDataCrawler
from src.governance.data_cleaner import UrbanDataCleaner
from src.integration.spatiotemporal_integrator import SpatiotemporalIntegrator
from src.eda.urban_eda import CrossDomainEDAAnalyzer
from src.graph.spatial_graph import UrbanSpatialGraphAnalyzer
from src.ml_tabular.health_predictor import UrbanHealthPredictor
from src.ml_nlp.event_parser import UrbanEventNLPParser
from src.evaluation.urban_evaluator import UrbanModelEvaluator
from src.cdss_app.urban_health_app import UrbanHealthDecisionSupportEngine


def test_tv1_crawler():
    """TV 1: Kiểm thử thu thập dữ liệu đa nguồn quy mô lớn"""
    crawler = HanoiUrbanDataCrawler(output_dir="data/01_raw")
    # Lấy 3 tháng cho 5 quận = >10.000 dòng
    aqi_df = crawler.fetch_air_quality_history("2024-01-01", "2024-03-31")
    assert len(aqi_df) >= 5000
    assert "pm2_5" in aqi_df.columns
    assert "district_id" in aqi_df.columns

    unique_times = aqi_df["timestamp"].unique().to_list()
    traffic_df = crawler.fetch_traffic_telemetry_series(unique_times)
    assert len(traffic_df) >= 5000

    events_df = crawler.fetch_urban_events_catalog()
    assert len(events_df) >= 5


def test_tv2_cleaner():
    """TV 2: Kiểm thử làm sạch dữ liệu, lọc outliner & sinh Data Docs HTML"""
    cleaner = UrbanDataCleaner(output_dir="data/02_curated",
                               docs_dir="docs/data_docs")
    raw_aqi = pl.read_parquet("data/01_raw/air_quality_raw.parquet")
    clean_aqi, report = cleaner.clean_air_quality_data(raw_aqi)

    assert len(clean_aqi) > 0
    assert report["status"] == "PASSED"
    assert os.path.exists("docs/data_docs/urban_health_data_docs.html")

    raw_traffic = pl.read_parquet("data/01_raw/traffic_raw.parquet")
    clean_traffic = cleaner.clean_traffic_data(raw_traffic)
    assert len(clean_traffic) > 0


def test_tv3_integration_and_10k_rows():
    """TV 3: Kiểm thử tích hợp không-thời gian và khẳng định đạt >= 10.000 dòng"""
    integrator = SpatiotemporalIntegrator(output_dir="data/03_integrated")
    clean_aqi = pl.read_parquet("data/02_curated/air_quality_curated.parquet")
    clean_traffic = pl.read_parquet("data/02_curated/traffic_curated.parquet")

    master_df = integrator.integrate_urban_datasets(clean_aqi, clean_traffic)

    # Khẳng định đáp ứng yêu cầu của Giảng viên: Ít nhất 10.000 dòng!
    assert len(master_df) >= 10000, f"Quy mô dataset ({len(master_df)}) chưa đạt yêu cầu >= 10.000 dòng của Thầy!"
    assert "epa_aqi_category" in master_df.columns
    assert "urban_stress_index" in master_df.columns


def test_tv4_cross_domain_eda():
    """TV 4: Kiểm thử kiểm định Welch's t-test tương quan kẹt xe làm tăng PM2.5"""
    analyzer = CrossDomainEDAAnalyzer()
    master_df = pl.read_parquet("data/03_integrated/master_urban_health.parquet")

    welch_res = analyzer.test_traffic_impact_on_pm25(master_df)
    assert welch_res["pm25_increase_due_to_traffic"] > 0
    assert welch_res["is_significant"] is True

    corrs = analyzer.compute_cross_domain_correlations(master_df)
    assert "pearson_jam_vs_pm25" in corrs
    assert corrs["pearson_jam_vs_pm25"] > 0.0


def test_tv5_spatial_graph():
    """TV 5: Kiểm thử phân tích đồ thị không gian và PageRank Hotspot"""
    analyzer = UrbanSpatialGraphAnalyzer()
    G = analyzer.build_district_connectivity_graph()
    assert G.number_of_nodes() == 5
    assert G.number_of_edges() >= 10

    hubs = analyzer.compute_pollution_hotspot_pagerank()
    assert len(hubs) == 5
    assert hubs[0]["pagerank_hotspot_score"] > 0.0


def test_tv6_ml_predictor():
    """TV 6: Kiểm thử huấn luyện mô hình dự báo PM2.5 và Stress đô thị"""
    predictor = UrbanHealthPredictor(n_estimators=30)
    master_df = pl.read_parquet("data/03_integrated/master_urban_health.parquet")
    metrics = predictor.train_models(master_df)

    assert metrics["regression_r2"] > 0.30
    assert metrics["classification_auroc"] >= 0.75

    scenario = predictor.predict_scenario(jam_factor=8.5, speed_kmh=15.0, is_rush_hour=1)
    assert scenario["predicted_pm2_5"] > 0
    assert 0.0 <= scenario["prob_high_urban_stress"] <= 1.0


def test_tv7_event_nlp():
    """TV 7: Kiểm thử trích xuất thực thể NER và phân loại sự kiện"""
    parser = UrbanEventNLPParser()
    res = parser.classify_event_impact("Mưa to ngập úng nghiêm trọng tại ngã tư Chùa Bộc quận Đống Đa")
    assert res["detected_district"] == "HN_DD"
    assert res["event_type"] == "Flooding"
    assert res["impact_score"] >= 4.0


def test_tv8_delong_evaluation():
    """TV 8: Kiểm thử kiểm định phi tham số DeLong Test & Youden's J"""
    evaluator = UrbanModelEvaluator()
    y_test = np.array([1, 1, 1, 0, 0, 0, 1, 0, 1, 0])
    p_multi = np.array([0.95, 0.89, 0.88, 0.12, 0.18, 0.08, 0.92, 0.25, 0.85, 0.10])
    p_base = np.array([0.72, 0.68, 0.62, 0.38, 0.40, 0.22, 0.70, 0.42, 0.65, 0.28])

    delong_res = evaluator.delong_roc_test(y_test, p_multi, p_base)
    assert delong_res["auc_multimodal"] >= delong_res["auc_baseline"]
    assert "z_statistic" in delong_res

    youden_res = evaluator.compute_youden_threshold(y_test, p_multi)
    assert 0.0 <= youden_res["optimal_threshold"] <= 1.0


def test_tv9_cdss_app():
    """TV 9: Kiểm thử bộ tính điểm đáng sống và mô phỏng chính sách"""
    cdss = UrbanHealthDecisionSupportEngine()
    score = cdss.calculate_district_liveability_score(pm25=70.0, jam_factor=6.0)
    assert 0.0 <= score["liveability_score"] <= 100.0

    sim = cdss.simulate_policy_intervention("HN_CG", current_pm25=90.0, current_jam=8.0, traffic_reduction_pct=30.0)
    assert sim["liveability_gain"] > 0.0
