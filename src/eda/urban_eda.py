"""
Phân Hệ 4: Cross-Domain Spatiotemporal EDA & Hypothesis Testing
Thành viên phụ trách: TV 4 (EDA Lead)
Môn học: Nhập môn Khoa học Dữ liệu (IT4142 - Bài giảng L4, L5, L6)

Mục tiêu phân tích:
1. Kiểm định giả thuyết Welch's t-test:
   H0: Ùn tắc giao thông nghiêm trọng (Jam Factor >= 7.0) không làm tăng nồng độ bụi mịn PM2.5.
   H1: Kẹt xe làm gia tăng nồng độ bụi mịn PM2.5 mang ý nghĩa thống kê áp đảo (p < 0.001).
2. Đo lường hệ số tương quan Pearson / Spearman giữa Giao thông (Jam Factor) và Ô nhiễm (PM2.5, CO, NO2).
3. Tổng hợp bảng dịch tễ đô thị Table 1 đối chiếu 5 quận Hà Nội.
"""

import math
import logging
from typing import Dict, List, Any
import numpy as np
import polars as pl
from scipy import stats

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("UrbanEDA")


class CrossDomainEDAAnalyzer:
    """
    Module phụ trách Phân tích Khám phá & Kiểm định Giả thuyết (TV 4).
    """

    def test_traffic_impact_on_pm25(self, master_df: pl.DataFrame) -> Dict[str, Any]:
        """
        Kiểm định Welch's t-test: So sánh nồng độ PM2.5 giữa 2 nhóm:
        - Nhóm 1: Giờ cao điểm / Tắc đường (jam_factor >= 7.0)
        - Nhóm 2: Giờ lưu thông bình thường / Thông thoáng (jam_factor < 4.0)
        """
        congested_pm25 = master_df.filter(pl.col("jam_factor") >= 7.0)["pm2_5"].to_numpy()
        free_pm25 = master_df.filter(pl.col("jam_factor") < 4.0)["pm2_5"].to_numpy()

        n1, n2 = len(congested_pm25), len(free_pm25)
        mean1, mean2 = float(np.mean(congested_pm25)), float(np.mean(free_pm25))
        var1, var2 = float(np.var(congested_pm25, ddof=1)), float(np.var(free_pm25, ddof=1))

        # Welch's t-test (không giả định phương sai đồng nhất)
        t_stat, p_val = stats.ttest_ind(congested_pm25, free_pm25, equal_var=False)

        diff = mean1 - mean2
        se_diff = math.sqrt(var1 / n1 + var2 / n2)
        ci_95 = [round(diff - 1.96 * se_diff, 2), round(diff + 1.96 * se_diff, 2)]

        return {
            "mean_pm25_congested": round(mean1, 2),
            "mean_pm25_freeflow": round(mean2, 2),
            "pm25_increase_due_to_traffic": round(diff, 2),
            "ci_95_difference": ci_95,
            "t_statistic": round(float(t_stat), 3),
            "p_value": float(p_val),
            "is_significant": bool(p_val < 0.05),
            "sample_sizes": {"congested_hours": n1, "freeflow_hours": n2}
        }

    def compute_cross_domain_correlations(self, master_df: pl.DataFrame) -> Dict[str, float]:
        """
        Tính toán hệ số tương quan Pearson giữa chỉ số kẹt xe (jam_factor)
        với các chất ô nhiễm không khí (PM2.5, CO, NO2).
        """
        jam = master_df["jam_factor"].to_numpy()
        pm25 = master_df["pm2_5"].to_numpy()
        co = master_df["carbon_monoxide"].to_numpy()
        no2 = master_df["nitrogen_dioxide"].to_numpy()

        corr_jam_pm25, _ = stats.pearsonr(jam, pm25)
        corr_jam_co, _ = stats.pearsonr(jam, co)
        corr_jam_no2, _ = stats.pearsonr(jam, no2)

        return {
            "pearson_jam_vs_pm25": round(float(corr_jam_pm25), 3),
            "pearson_jam_vs_co": round(float(corr_jam_co), 3),
            "pearson_jam_vs_no2": round(float(corr_jam_no2), 3)
        }

    def generate_district_table1(self, master_df: pl.DataFrame) -> Dict[str, Any]:
        """
        Sinh bảng tổng hợp dịch tễ đô thị Table 1 chuẩn mực cho 5 quận Hà Nội.
        """
        districts = master_df["district_id"].unique().to_list()
        summary = {}

        for d_id in districts:
            sub = master_df.filter(pl.col("district_id") == d_id)
            d_name = sub["district_name"][0]
            summary[d_name] = {
                "records_count": len(sub),
                "mean_pm25": round(float(sub["pm2_5"].mean()), 1),
                "mean_jam_factor": round(float(sub["jam_factor"].mean()), 2),
                "mean_speed_kmh": round(float(sub["speed_kmh"].mean()), 1),
                "mean_stress_index": round(float(sub["urban_stress_index"].mean()), 1)
            }

        return summary


if __name__ == "__main__":
    analyzer = CrossDomainEDAAnalyzer()
    df = pl.read_parquet("data/03_integrated/master_urban_health.parquet")
    print("Welch Test:", analyzer.test_traffic_impact_on_pm25(df))
    print("Correlations:", analyzer.compute_cross_domain_correlations(df))
