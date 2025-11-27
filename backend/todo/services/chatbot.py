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
        "high": "High",
        "cao": "High",
        "quan trọng": "High",
        "medium": "Medium",
        "trung bình": "Medium",
        "low": "Low",
        "thấp": "Low",
    }

    TIME_KEYWORDS = {
        "hôm nay": 0,
        "today": 0,
        "mai": 1,
        "tomorrow": 1,
        "ngày mai": 1,
        "ngày kia": 2,
        "tuần sau": 7,
        "next week": 7,
    }

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
        """Extract title từ message"""
        title = message

        patterns = [
            r"\d+\s*(giờ|phút|tiếng|hour|minute|min)",
            r"(hôm nay|mai|ngày mai|tuần sau|today|tomorrow)",
            r"(sáng|chiều|tối|morning|afternoon|evening)",
            r"(urgent|khẩn|gấp|high|cao|low|thấp)",
            r"lúc\s*\d+h",
            r"vào\s*\d+h",
        ]

        for pattern in patterns:
            title = re.sub(pattern, "", title, flags=re.IGNORECASE)

        title = re.sub(r"\s+", " ", title).strip()
        title = title.replace("thêm task", "").replace("tạo task", "")
        title = title.replace("add task", "").replace("create task", "")
        title = title.strip()

        return title if title else "Task mới"

    def _extract_priority(self, message_lower):
        """Extract priority từ message"""
        for keyword, priority in self.PRIORITY_KEYWORDS.items():
            if keyword in message_lower:
                return priority
        return "Medium"

    def _extract_duration(self, message_lower):
        """Extract duration (phút) từ message"""
        hour_match = re.search(r"(\d+)\s*(giờ|tiếng|hour)", message_lower)
        if hour_match:
            return int(hour_match.group(1)) * 60

        min_match = re.search(r"(\d+)\s*(phút|minute|min)", message_lower)
        if min_match:
            return int(min_match.group(1))

        return 60  # Default 1 giờ

    def _extract_due_date(self, message_lower):
        """Extract due date từ message"""
        now = timezone.now()

        for keyword, days_offset in self.TIME_KEYWORDS.items():
            if keyword in message_lower:
                due_date = now + timedelta(days=days_offset)

                hour = self._extract_hour(message_lower)
                if hour:
                    due_date = due_date.replace(
                        hour=hour, minute=0, second=0, microsecond=0
                    )
                else:
                    due_date = due_date.replace(
                        hour=23, minute=59, second=0, microsecond=0
                    )

                return due_date

        # Default: 1 ngày sau
        return now + timedelta(days=1)

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
        """Generate response message cho user"""
        title = task_data.get("title", "Task")
        priority = task_data.get("priority", "Medium")
        duration = task_data.get("estimated_duration_min", 60)

        response = f"✅ Đã tạo task: **{title}**\n"
        response += f"📊 Ưu tiên: {priority}\n"
        response += f"⏱️ Thời lượng: {duration} phút\n"

        if task_data.get("due_at"):
            due = datetime.fromisoformat(
                task_data["due_at"].replace("Z", "+00:00")
            )
            response += f"📅 Deadline: {due.strftime('%d/%m/%Y %H:%M')}\n"

        if prediction:
            if prediction.get("on_time_prediction") == 1:
                response += (
                    f"\n🎯 AI dự đoán: Có thể hoàn thành đúng hạn "
                    f"({int(prediction.get('confidence', 0)*100)}% tin cậy)"
                )
            else:
                response += (
                    f"\n⚠️ AI dự đoán: Có nguy cơ trễ hạn "
                    f"({int(prediction.get('confidence', 0)*100)}% tin cậy)"
                )

        return response
