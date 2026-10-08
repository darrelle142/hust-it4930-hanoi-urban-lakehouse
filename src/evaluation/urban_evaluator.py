"""
Phân Hệ 8: Rigorous Model Evaluation, Calibration & DeLong Test
Thành viên phụ trách: TV 8 (Model Evaluation Lead)
Môn học: Nhập môn Khoa học Dữ liệu (IT4142 - Bài giảng L12: Đánh giá kết quả phân tích)

Quy chuẩn đánh giá khắt khe:
1. Kiểm định phi tham số DeLong Test: So sánh hai đường cong AUROC trên cùng tập test
   (Mô hình Đa thể thức [Không khí + Giao thông + Đồ thị + NLP] vs Mô hình Baseline [Chỉ dùng Giao thông]).
2. Chỉ số Youden's J Statistic: Xác lập ngưỡng quyết định (Decision Cutoff) tối ưu báo động đỏ.
3. Brier Score Loss: Đánh giá độ tin cậy và hiệu chuẩn xác suất dự báo.
"""

import math
import logging
from typing import Dict, List, Tuple, Any
import numpy as np
from scipy import stats
from sklearn.metrics import roc_curve, auc, brier_score_loss

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("UrbanEvaluator")


class UrbanModelEvaluator:
    """
    Module phụ trách Đánh giá Mô hình & Kiểm định Ý nghĩa Thống kê (TV 8).
    """

    def compute_youden_threshold(self, y_true: np.ndarray, y_prob: np.ndarray) -> Dict[str, Any]:
        """Xác định ngưỡng cắt tối ưu cân bằng Sensitivity & Specificity theo chỉ số Youden's J"""
        fpr, tpr, thresholds = roc_curve(y_true, y_prob)
        j_scores = tpr - fpr
        best_idx = np.argmax(j_scores)

        return {
            "auroc": round(float(auc(fpr, tpr)), 4),
            "optimal_threshold": round(float(thresholds[best_idx]), 4),
            "max_youden_j": round(float(j_scores[best_idx]), 4),
            "sensitivity_at_opt": round(float(tpr[best_idx]), 4),
            "specificity_at_opt": round(float(1.0 - fpr[best_idx]), 4)
        }

    def compute_brier_calibration(self, y_true: np.ndarray, y_prob: np.ndarray) -> Dict[str, Any]:
        """Đo lường độ hiệu chuẩn xác suất dự báo qua Brier Score"""
        bs = brier_score_loss(y_true, y_prob)
        return {
            "brier_score": round(float(bs), 4),
            "calibration_status": "Well-Calibrated" if bs < 0.15 else "Moderate"
        }

    def delong_roc_test(self, y_true: np.ndarray, prob_multimodal: np.ndarray, prob_baseline: np.ndarray) -> Dict[str, Any]:
        """
        Kiểm định phi tham số DeLong Test dựa trên lý thuyết U-statistics (DeLong 1988):
        Z = (AUC_Multi - AUC_Base) / sqrt(Var(AUC_Multi - AUC_Base)) ~ N(0, 1)
        """
        y_true = np.asarray(y_true)
        pos = y_true == 1
        neg = y_true == 0
        m = np.sum(pos)
        n = np.sum(neg)

        if m == 0 or n == 0:
            raise ValueError("Tập kiểm thử phải có cả mẫu dương (1) và âm (0).")

        p_m, p_b = np.asarray(prob_multimodal), np.asarray(prob_baseline)
        p_m_pos, p_m_neg = p_m[pos], p_m[neg]
        p_b_pos, p_b_neg = p_b[pos], p_b[neg]

        v10_m = np.array([np.mean(p_m_pos[i] > p_m_neg) + 0.5 * np.mean(p_m_pos[i] == p_m_neg) for i in range(m)])
        v01_m = np.array([np.mean(p_m_neg[j] < p_m_pos) + 0.5 * np.mean(p_m_neg[j] == p_m_pos) for j in range(n)])

        v10_b = np.array([np.mean(p_b_pos[i] > p_b_neg) + 0.5 * np.mean(p_b_pos[i] == p_b_neg) for i in range(m)])
        v01_b = np.array([np.mean(p_b_neg[j] < p_b_pos) + 0.5 * np.mean(p_b_neg[j] == p_b_pos) for j in range(n)])

        auc_m, auc_b = float(np.mean(v10_m)), float(np.mean(v10_b))

        s10_m, s01_m = float(np.var(v10_m, ddof=1)), float(np.var(v01_m, ddof=1))
        s10_b, s01_b = float(np.var(v10_b, ddof=1)), float(np.var(v01_b, ddof=1))

        cov_10 = float(np.cov(v10_m, v10_b)[0, 1])
        cov_01 = float(np.cov(v01_m, v01_b)[0, 1])

        var_diff = (s10_m + s10_b - 2 * cov_10) / m + (s01_m + s01_b - 2 * cov_01) / n
        std_diff = math.sqrt(max(var_diff, 1e-8))

        z_stat = (auc_m - auc_b) / std_diff
        p_val = 2.0 * (1.0 - stats.norm.cdf(abs(z_stat)))

        return {
            "auc_multimodal": round(auc_m, 4),
            "auc_baseline": round(auc_b, 4),
            "auc_improvement": round(auc_m - auc_b, 4),
            "z_statistic": round(float(z_stat), 3),
            "p_value": float(p_val),
            "is_statistically_superior": bool(p_val < 0.05)
        }


if __name__ == "__main__":
    evaluator = UrbanModelEvaluator()
    y_test = np.array([1, 1, 1, 0, 0, 0, 1, 0, 1, 0])
    p_multi = np.array([0.95, 0.89, 0.88, 0.12, 0.18, 0.08, 0.92, 0.25, 0.85, 0.10])
    p_base = np.array([0.72, 0.68, 0.62, 0.38, 0.40, 0.22, 0.70, 0.42, 0.65, 0.28])
    print("DeLong Test:", evaluator.delong_roc_test(y_test, p_multi, p_base))
