"""
Phân Hệ 9: Interactive Urban Health Platform & Data Storytelling (CDSS Engine)
Thành viên phụ trách: TV 9 (CDSS Platform Lead & Storyteller)
Môn học: Nhập môn Khoa học Dữ liệu (IT4142 - Yêu cầu 7: Xây dựng ứng dụng End-User)

Chức năng Hệ thống:
1. Bản đồ Đa lớp Sức khỏe Đô thị (Interactive Urban Health Map):
   - Lớp 1: Bản đồ nhiệt Bụi mịn PM2.5 & Chỉ số AQI theo 5 quận.
   - Lớp 2: Điểm nghẽn giao thông và vận tốc thời gian thực.
   - Lớp 3: Các điểm nóng sự cố và sự kiện tập trung đông người.
2. Bộ tính Chỉ số Đáng sống (Urban Liveability & Health Score: 0 -> 100).
3. Mô phỏng Kịch bản Đô thị (What-If Urban Policy Simulator):
   - Đánh giá hiệu quả của chính sách giãn cách giao thông / hạn chế xe cá nhân đến chất lượng không khí.
4. Kịch bản Data Storytelling 3 hồi cho buổi bảo vệ đồ án.
"""

import logging
from typing import Dict, List, Any
import numpy as np
import polars as pl
from src.graph.spatial_graph import UrbanSpatialGraphAnalyzer
from src.ml_tabular.health_predictor import UrbanHealthPredictor
from src.ml_nlp.event_parser import UrbanEventNLPParser

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("UrbanHealthApp")


class UrbanHealthDecisionSupportEngine:
    """
    Nhân xử lý hệ thống Bản đồ Sức khỏe Đô thị Hà Nội (TV 9).
    """

    def __init__(self):
        self.graph_analyzer = UrbanSpatialGraphAnalyzer()
        self.graph = self.graph_analyzer.build_district_connectivity_graph()
        self.predictor = UrbanHealthPredictor()
        self.nlp_parser = UrbanEventNLPParser()

    def calculate_district_liveability_score(self, pm25: float, jam_factor: float, has_incident: int = 0) -> Dict[str, Any]:
        """
        Tính toán Chỉ số Đáng sống (Liveability Score: 0 -> 100).
        Điểm số càng cao thì chất lượng sống càng tốt và an toàn cho sức khỏe:
        Liveability = 100 - (0.5 * PM2.5_penalty + 0.4 * Traffic_penalty + 0.1 * Incident_penalty)
        """
        # Phạt ô nhiễm bụi mịn (ngưỡng an toàn WHO: 15 ug/m3, ngưỡng xấu: 150 ug/m3)
        pm25_penalty = min(50.0, (pm25 / 150.0) * 50.0)
        # Phạt kẹt xe (0 -> 10)
        traffic_penalty = min(40.0, (jam_factor / 10.0) * 40.0)
        # Phạt sự cố
        incident_penalty = 10.0 if has_incident else 0.0

        liveability = max(0.0, 100.0 - (pm25_penalty + traffic_penalty + incident_penalty))

        if liveability >= 75.0:
            rating = "Thành phố Xanh / Đáng sống (Tốt)"
            badge_color = "#10b981"
        elif liveability >= 50.0:
            rating = "Mức độ Trung bình / Cần thận trọng"
            badge_color = "#f59e0b"
        else:
            rating = "Báo động Đỏ / Ô nhiễm & Ùn tắc cao"
            badge_color = "#ef4444"

        return {
            "liveability_score": round(float(liveability), 1),
            "rating": rating,
            "badge_color": badge_color,
            "penalties": {
                "air_pollution_penalty": round(pm25_penalty, 1),
                "traffic_congestion_penalty": round(traffic_penalty, 1),
                "incident_penalty": round(incident_penalty, 1)
            }
        }

    def simulate_policy_intervention(self, district_id: str, current_pm25: float, current_jam: float,
                                     traffic_reduction_pct: float = 30.0) -> Dict[str, Any]:
        """
        Mô phỏng chính sách công:
        Nếu thành phố giảm được traffic_reduction_pct % kẹt xe (qua xe buýt điện / metro),
        thì PM2.5 và Chỉ số Đáng sống sẽ cải thiện như thế nào?
        """
        improved_jam = max(1.0, current_jam * (1.0 - traffic_reduction_pct / 100.0))
        # Khói xe chiếm khoảng 40% phát thải PM2.5 nội đô
        improved_pm25 = max(10.0, current_pm25 * (1.0 - (traffic_reduction_pct / 100.0) * 0.40))

        before = self.calculate_district_liveability_score(current_pm25, current_jam)
        after = self.calculate_district_liveability_score(improved_pm25, improved_jam)

        score_gain = after["liveability_score"] - before["liveability_score"]

        return {
            "district_id": district_id,
            "traffic_reduction_applied": f"{traffic_reduction_pct}%",
            "pm25_before": current_pm25,
            "pm25_after_simulation": round(improved_pm25, 1),
            "liveability_before": before["liveability_score"],
            "liveability_after": after["liveability_score"],
            "liveability_gain": round(score_gain, 1),
            "policy_impact": f"Giảm {traffic_reduction_pct}% kẹt xe giúp giảm {current_pm25 - improved_pm25:.1f} ug/m3 PM2.5 và tăng {score_gain:.1f} điểm chất lượng sống."
        }


if __name__ == "__main__":
    cdss = UrbanHealthDecisionSupportEngine()
    score = cdss.calculate_district_liveability_score(pm25=85.0, jam_factor=7.5)
    print("District Liveability:", score)
    sim = cdss.simulate_policy_intervention("HN_CG", current_pm25=95.0, current_jam=8.0, traffic_reduction_pct=30.0)
    print("Policy Intervention Sim:", sim)
