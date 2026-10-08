"""
Phân Hệ 7: Urban Incident NLP & Extraction (Xử Lý Văn Bản Tin Tức & Sự Kiện Đô Thị)
Thành viên phụ trách: TV 7 (NLP Event Lead)
Môn học: Nhập môn Khoa học Dữ liệu (IT4142)

Mục tiêu xử lý văn bản:
1. Trích xuất thực thể định danh địa lý (Geographical Named Entity Recognition - NER):
   Nhận diện quận/địa bàn xảy ra sự cố từ các bản tin thời sự, VOV Giao thông, diễn đàn đô thị.
2. Phân loại mức độ nghiêm trọng và tác động lan tỏa của sự kiện (Critical / High / Moderate).
3. Đóng gói chỉ số tác động sự kiện (Event Impact Score) phục vụ tích hợp Master Dataset.
"""

import re
import logging
from typing import Dict, List, Any
import polars as pl

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("UrbanEventNLP")


class UrbanEventNLPParser:
    """
    Module phụ trách Xử lý Ngôn ngữ Tự nhiên & Trích xuất Thực thể Sự kiện (TV 7).
    """

    def __init__(self):
        # Bảng từ khóa ánh xạ địa danh sang District ID
        self.district_keywords = {
            "HN_HK": ["hoàn kiếm", "hồ gươm", "tràng tiền", "phố cổ", "đinh tiên hoàng", "hàng bài"],
            "HN_CG": ["cầu giấy", "xuân thủy", "duy tân", "trần thái tông", "hồ tùng mậu", "mai dịch"],
            "HN_DD": ["đống đa", "ngã tư sở", "chùa bộc", "thái hà", "tây sơn", "ô chợ dừa", "láng"],
            "HN_HD": ["hà đông", "quang trung", "tố hữu", "văn quán", "nguyễn trãi kéo dài", "yên nghĩa"],
            "HN_NTL": ["nam từ liêm", "mỹ đình", "mễ trì", "lê quang đạo", "svđ mỹ đình", "trần hữu dực"]
        }

        # Trọng số tác động của các loại sự kiện
        self.impact_weights = {
            "Accident": 3.5,
            "Flooding": 4.5,
            "Sports/Stadium": 4.0,
            "Pedestrian/Festival": 2.5,
            "VehicleBreakdown": 2.0,
            "Commercial": 2.0,
            "General": 1.0
        }

    def extract_district_from_text(self, text: str) -> str:
        """Trích xuất mã quận xuất hiện trong bản tin (NER)"""
        clean_txt = text.lower()
        for d_id, kws in self.district_keywords.items():
            for kw in kws:
                if kw in clean_txt:
                    return d_id
        return "UNKNOWN_DISTRICT"

    def classify_event_impact(self, title: str, raw_event_type: str = "General") -> Dict[str, Any]:
        """
        Phân loại mức độ nghiêm trọng và ước lượng điểm số tác động (Impact Score):
        - Critical (Nguy cấp: ngập sâu, tai nạn nghiêm trọng, sự kiện 40.000 người)
        - High (Cao)
        - Moderate (Trung bình)
        """
        title_lower = title.lower()
        detected_district = self.extract_district_from_text(title)

        # Suy diễn loại sự kiện từ ngữ cảnh tiêu đề
        event_type = raw_event_type
        if any(w in title_lower for w in ["ngập sâu", "chìm trong nước", "mưa lớn", "ngập"]):
            event_type = "Flooding"
        elif any(w in title_lower for w in ["tai nạn", "va chạm", "tông liên hoàn"]):
            event_type = "Accident"
        elif any(w in title_lower for w in ["world cup", "mỹ đình", "bóng đá", "concert"]):
            event_type = "Sports/Stadium"

        base_weight = self.impact_weights.get(event_type, 1.5)

        # Tính toán mức độ nghiêm trọng
        if base_weight >= 4.0:
            severity = "Critical Impact (Rất nghiêm trọng)"
        elif base_weight >= 2.5:
            severity = "High Impact (Tác động cao)"
        else:
            severity = "Moderate Impact (Trung bình)"

        return {
            "title": title,
            "detected_district": detected_district,
            "event_type": event_type,
            "severity_level": severity,
            "impact_score": base_weight
        }

    def process_news_feed(self, news_items: List[Dict[str, str]]) -> pl.DataFrame:
        """Xử lý hàng loạt bản tin thời sự giao thông - sự kiện"""
        processed = []
        for item in news_items:
            res = self.classify_event_impact(item.get("title", ""), item.get("event_type", "General"))
            processed.append(res)
        return pl.DataFrame(processed)


if __name__ == "__main__":
    parser = UrbanEventNLPParser()
    test_title = "Mưa lớn gây ngập sâu diện rộng tại ngã tư Chùa Bộc - Thái Hà quận Đống Đa"
    print("NLP Parse Result:", parser.classify_event_impact(test_title))
