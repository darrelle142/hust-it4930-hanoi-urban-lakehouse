"""
Phân Hệ 5: Spatial Graph & Link Analysis (Mạng Lưới Lan Truyền Ô Nhiễm & Giao Thông)
Thành viên phụ trách: TV 5 (Graph Analytics Lead)
Môn học: Nhập môn Khoa học Dữ liệu (IT4142 - Bài giảng L10 & L11: Link Analysis)

Giải thuật Link Analysis:
1. Xây dựng Đồ thị không gian kết nối 5 quận Hà Nội thông qua các hành lang giao thông chính.
2. PageRank Centrality: Định vị quận trung tâm có nguy cơ tích tụ ô nhiễm và tắc nghẽn cao nhất.
3. Betweenness Centrality: Xác định vai trò trung chuyển luồng phương tiện qua các quận.
"""

import logging
from typing import Dict, List, Any
import networkx as nx
import polars as pl

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("UrbanGraph")


class UrbanSpatialGraphAnalyzer:
    """
    Module phân tích liên kết đồ thị không gian đô thị (TV 5).
    """

    def __init__(self):
        self.graph = nx.DiGraph()

    def build_district_connectivity_graph(self) -> nx.DiGraph:
        """
        Khởi tạo đồ thị có hướng kết nối giữa các quận:
        Đỉnh = 5 quận trọng điểm Hà Nội
        Cạnh = Trục giao thông kết nối trực tiếp (Đường Nguyễn Trãi, Vành Đai 3, Cầu Giấy - Kim Mã...)
        """
        # Cạnh (u, v, {corridor, distance_km, traffic_flow_weight})
        corridors = [
            ("HN_CG", "HN_DD", {"corridor": "Cau Giay - Kim Ma", "distance_km": 3.5, "weight": 4.5}),
            ("HN_DD", "HN_HK", {"corridor": "Kham Thien - Le Duan", "distance_km": 2.8, "weight": 5.0}),
            ("HN_HD", "HN_DD", {"corridor": "Nguyen Trai - Nga Tu So", "distance_km": 5.2, "weight": 6.8}),
            ("HN_HD", "HN_CG", {"corridor": "Vanh Dai 3 (Khuat Duy Tien)", "distance_km": 4.5, "weight": 6.2}),
            ("HN_NTL", "HN_CG", {"corridor": "Pham Hung - Xuan Thuy", "distance_km": 3.2, "weight": 5.5}),
            ("HN_NTL", "HN_HD", {"corridor": "Le Quang Dao - To Huu", "distance_km": 4.0, "weight": 4.2}),
            ("HN_CG", "HN_HK", {"corridor": "Kim Ma - Nguyen Thai Hoc", "distance_km": 4.8, "weight": 4.8}),
        ]

        # Thêm liên kết 2 chiều
        for u, v, data in corridors:
            self.graph.add_edge(u, v, **data)
            self.graph.add_edge(v, u, **data)

        logger.info(f"Đã xây dựng Đồ thị Không gian: {self.graph.number_of_nodes()} quận, {self.graph.number_of_edges()} cạnh kết nối.")
        return self.graph

    def compute_pollution_hotspot_pagerank(self, alpha: float = 0.85) -> List[Dict[str, Any]]:
        """
        Tính toán giải thuật PageRank có trọng số lưu lượng (Slide L10-11 Link Analysis):
        Tìm các quận đóng vai trò 'Hub' hội tụ áp lực ô nhiễm và giao thông lớn nhất từ các vùng xung quanh.
        """
        if self.graph.number_of_nodes() == 0:
            self.build_district_connectivity_graph()

        pr_scores = nx.pagerank(self.graph, alpha=alpha, weight="weight")
        sorted_hubs = sorted(pr_scores.items(), key=lambda x: x[1], reverse=True)

        district_names = {
            "HN_HK": "Hoàn Kiếm", "HN_CG": "Cầu Giấy",
            "HN_DD": "Đống Đa", "HN_HD": "Hà Đông", "HN_NTL": "Nam Từ Liêm"
        }

        results = []
        for rank, (d_id, score) in enumerate(sorted_hubs, 1):
            results.append({
                "rank": rank,
                "district_id": d_id,
                "district_name": district_names.get(d_id, d_id),
                "pagerank_hotspot_score": round(score, 4),
                "in_degree": self.graph.in_degree(d_id)
            })

        return results

    def compute_betweenness_centrality(self) -> Dict[str, float]:
        """Tính toán Betweenness Centrality tìm quận trung chuyển huyết mạch"""
        if self.graph.number_of_nodes() == 0:
            self.build_district_connectivity_graph()
        bc = nx.betweenness_centrality(self.graph, weight="distance_km", normalized=True)
        return {k: round(v, 4) for k, v in bc.items()}


if __name__ == "__main__":
    analyzer = UrbanSpatialGraphAnalyzer()
    analyzer.build_district_connectivity_graph()
    hubs = analyzer.compute_pollution_hotspot_pagerank()
    print("Top Hotspots PageRank:", hubs)
