# todo/services/chatbot.py
import re
from datetime import datetime, timedelta
from django.utils import timezone


class TaskChatbot:
    """Chatbot để parse natural language thành task data"""

    PRIORITY_KEYWORDS = {
        "urgent": "Urgent",
        "khẩn": "Urgent",
        "gấp": "Urgent",
        "cấp bách": "Urgent",
        "high": "High",
        "cao": "High",
        "quan trọng": "High",
        "ưu tiên": "High",
        "medium": "Medium",
        "trung bình": "Medium",
        "bình thường": "Medium",
        "low": "Low",
        "thấp": "Low",
        "không gấp": "Low",
    }

    TIME_KEYWORDS = {
        "hôm nay": 0,
        "today": 0,
        "bây giờ": 0,
        "ngay": 0,
        "mai": 1,
        "tomorrow": 1,
        "ngày mai": 1,
        "sáng mai": 1,
        "chiều mai": 1,
        "tối mai": 1,
        "ngày kia": 2,
        "tuần này": 3,
        "tuần sau": 7,
        "next week": 7,
        "tháng sau": 30,
        "next month": 30,
    }
    
    # Thêm action keywords để hiểu ý định
    ACTION_KEYWORDS = [
        "thêm", "tạo", "add", "create", "làm", "học", "đọc", "viết",
        "gọi", "gửi", "mua", "đi", "xem", "check", "review", "fix",
        "update", "cập nhật", "hoàn thành", "complete"
    ]

    def parse_message(self, message):
        """
        Parse message thành task data
        Returns: dict với title, description, priority, due_at, estimated_duration_min
        """
        message_lower = message.lower()

        # Extract title (phần chính của task)
        title = self._extract_title(message)

        # Extract priority
        priority = self._extract_priority(message_lower)

        # Extract duration (số giờ/phút)
        duration_min = self._extract_duration(message_lower)

        # Extract due date/time
        due_at = self._extract_due_date(message_lower)

        # Extract planned start time
        planned_start_at = self._extract_start_time(message_lower, due_at)

        return {
            "title": title,
            "description": f"Tạo từ chat: {message}",
            "priority": priority,
            "estimated_duration_min": duration_min,
            "due_at": due_at.isoformat() if due_at else None,
            "planned_start_at": planned_start_at.isoformat()
            if planned_start_at
            else None,
        }

    def _extract_title(self, message):
        """Extract title từ message - thông minh hơn"""
        title = message.strip()

        # Bỏ các noise words ở đầu
        start_patterns = [
            r"^(thêm|tạo|add|create|làm|nhắc|reminder)\s+(task|công việc|việc|nhở)?\s*:?\s*",
            r"^(gấp|urgent|khẩn)\s+",
        ]
        
        for pattern in start_patterns:
            title = re.sub(pattern, "", title, flags=re.IGNORECASE)

        # Bỏ time/duration info
        time_patterns = [
            r"\s+\d+\s*(giờ|phút|tiếng|hour|minute|min|h)\s*(rưỡi|nữa)?",
            r"\s+(hôm nay|mai|ngày mai|tuần sau|today|tomorrow|ngày kia|trong\s*\d+\s*ngày)",
            r"\s+(sáng|chiều|tối|trưa|morning|afternoon|evening|noon)\s*(mai|nay)?",
            r"\s+(lúc|vào|đến)\s*\d+h\d*",
        ]
        
        for pattern in time_patterns:
            title = re.sub(pattern, "", title, flags=re.IGNORECASE)

        # Bỏ priority keywords
        priority_patterns = [
            r"\s+(urgent|khẩn|gấp|high|cao|low|thấp|quan trọng|ưu tiên|cấp bách|không gấp)",
        ]
        
        for pattern in priority_patterns:
            title = re.sub(pattern, "", title, flags=re.IGNORECASE)

        # Chuẩn hóa khoảng trắng
        title = re.sub(r"\s+", " ", title).strip()
        
        # Bỏ dấu câu thừa ở cuối
        title = title.rstrip(".,;:!?")
        
        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:]

        return title if title else "Task mới"

    def _extract_priority(self, message_lower):
        """Extract priority từ message"""
        for keyword, priority in self.PRIORITY_KEYWORDS.items():
            if keyword in message_lower:
                return priority
        return "Medium"

    def _extract_duration(self, message_lower):
        """Extract duration (phút) từ message - thông minh hơn"""
        # Tìm giờ
        hour_match = re.search(r"(\d+)\s*(giờ|tiếng|hour|h)\s*(rưỡi)?", message_lower)
        if hour_match:
            hours = int(hour_match.group(1))
            # Nếu có "rưỡi" thì thêm 30 phút
            if hour_match.group(3):
                return hours * 60 + 30
            return hours * 60

        # Tìm phút
        min_match = re.search(r"(\d+)\s*(phút|minute|min)", message_lower)
        if min_match:
            return int(min_match.group(1))
        
        # Tìm pattern "X tiếng Y phút"
        combined = re.search(r"(\d+)\s*(giờ|tiếng)\s*(\d+)\s*(phút)", message_lower)
        if combined:
            hours = int(combined.group(1))
            minutes = int(combined.group(3))
            return hours * 60 + minutes

        # Smart default dựa vào keywords
        if any(word in message_lower for word in ["học", "đọc", "viết", "code"]):
            return 120  # 2 giờ cho task học tập
        elif any(word in message_lower for word in ["gọi", "họp", "meeting", "call"]):
            return 30  # 30 phút cho cuộc gọi
        elif any(word in message_lower for word in ["mua", "đi", "gửi"]):
            return 45  # 45 phút cho việc vặt
        
        return 60  # Default 1 giờ

    def _extract_due_date(self, message_lower):
        """Extract due date từ message - thông minh với relative time"""
        now = timezone.now()

        # Pattern "X giờ/phút nữa" - relative time
        relative_hour = re.search(r"(\d+)\s*(giờ|tiếng)\s*(rưỡi)?\s*nữa", message_lower)
        if relative_hour:
            hours = int(relative_hour.group(1))
            if relative_hour.group(3):  # rưỡi
                hours += 0.5
            return now + timedelta(hours=hours)
        
        relative_min = re.search(r"(\d+)\s*(phút)\s*nữa", message_lower)
        if relative_min:
            minutes = int(relative_min.group(1))
            return now + timedelta(minutes=minutes)

        # Tìm time keywords (hôm nay, mai, etc)
        for keyword, days_offset in self.TIME_KEYWORDS.items():
            if keyword in message_lower:
                due_date = now + timedelta(days=days_offset)

                # Extract giờ cụ thể
                hour = self._extract_hour(message_lower)
                
                # Nếu không có giờ cụ thể, dùng context
                if not hour:
                    if "sáng" in message_lower or "morning" in message_lower:
                        hour = 9
                    elif "trưa" in message_lower or "noon" in message_lower:
                        hour = 12
                    elif "chiều" in message_lower or "afternoon" in message_lower:
                        hour = 15
                    elif "tối" in message_lower or "evening" in message_lower:
                        hour = 19
                    else:
                        hour = 23  # End of day
                
                due_date = due_date.replace(
                    hour=hour, minute=59 if hour == 23 else 0, 
                    second=0, microsecond=0
                )
                return due_date

        # Pattern "trong X ngày"
        days_match = re.search(r"trong\s*(\d+)\s*ngày", message_lower)
        if days_match:
            days = int(days_match.group(1))
            return now + timedelta(days=days)

        # Pattern "sau X giờ" (không có "nữa")
        after_hours = re.search(r"sau\s*(\d+)\s*(giờ|tiếng)", message_lower)
        if after_hours:
            hours = int(after_hours.group(1))
            return now + timedelta(hours=hours)

        # Default: dựa vào priority và context
        # Nếu có "gấp" hoặc "urgent" → trong vài giờ
        if any(word in message_lower for word in ["urgent", "khẩn", "gấp", "ngay"]):
            # Gấp = 2 giờ nữa
            return now + timedelta(hours=2)
        elif any(word in message_lower for word in ["low", "thấp"]):
            return now + timedelta(days=2)
        
        # Default: cuối ngày hôm nay
        return now.replace(hour=23, minute=59, second=0, microsecond=0)

    def _extract_start_time(self, message_lower, due_at):
        """Extract planned start time từ message"""
        now = timezone.now()

        if "sáng" in message_lower or "morning" in message_lower:
            start = now.replace(hour=9, minute=0, second=0, microsecond=0)
        elif "chiều" in message_lower or "afternoon" in message_lower:
            start = now.replace(hour=14, minute=0, second=0, microsecond=0)
        elif "tối" in message_lower or "evening" in message_lower:
            start = now.replace(hour=19, minute=0, second=0, microsecond=0)
        else:
            hour = self._extract_hour(message_lower)
            if hour:
                start = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            else:
                start = now + timedelta(hours=1)

        if "mai" in message_lower or "tomorrow" in message_lower:
            start = start + timedelta(days=1)

        return start

    def _extract_hour(self, message_lower):
        """Extract giờ cụ thể từ message (9h, 14h, etc)"""
        hour_match = re.search(r"(\d+)h", message_lower)
        if hour_match:
            hour = int(hour_match.group(1))
            if 0 <= hour <= 23:
                return hour

        time_match = re.search(r"(lúc|vào)\s*(\d+)", message_lower)
        if time_match:
            hour = int(time_match.group(2))
            if 0 <= hour <= 23:
                return hour

        return None

    def generate_response(self, task_data, prediction=None):
        """Generate response message cho user - ngắn gọn và rõ ràng"""
        title = task_data.get("title", "Task")
        priority = task_data.get("priority", "Medium")
        duration = task_data.get("estimated_duration_min", 60)

        # Format duration ngắn gọn
        if duration >= 60:
            hours = duration // 60
            mins = duration % 60
            if mins > 0:
                duration_str = f"{hours}h{mins}p"
            else:
                duration_str = f"{hours}h"
        else:
            duration_str = f"{duration}p"

        # Priority text ngắn
        priority_map = {
            "Urgent": "Khẩn",
            "High": "Cao",
            "Medium": "TB",
            "Low": "Thấp"
        }
        priority_text = priority_map.get(priority, priority)

        # Response ngắn gọn
        response = f"✓ {title}\n"
        response += f"Ưu tiên: {priority_text} | Thời lượng: {duration_str}\n"

        if task_data.get("due_at"):
            due = datetime.fromisoformat(
                task_data["due_at"].replace("Z", "+00:00")
            )
            
            now = timezone.now()
            days_diff = (due.date() - now.date()).days
            
            if days_diff == 0:
                time_str = f"Hôm nay {due.strftime('%H:%M')}"
            elif days_diff == 1:
                time_str = f"Mai {due.strftime('%H:%M')}"
            else:
                time_str = due.strftime('%d/%m %H:%M')
            
            response += f"Deadline: {time_str}\n"

        if prediction:
            on_time_prob = prediction.get("on_time_prediction", 0.5)
            
            if on_time_prob >= 0.8:
                response += "\n→ Dễ hoàn thành đúng hạn"
            elif on_time_prob >= 0.6:
                response += "\n→ Có thể hoàn thành đúng hạn"
            elif on_time_prob >= 0.4:
                response += "\n→ Hơi khó, nên bắt đầu sớm"
            else:
                response += "\n→ Khó hoàn thành, cần ưu tiên cao"

        return response
