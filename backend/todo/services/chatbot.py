# todo/services/chatbot.py
import re
from datetime import datetime, timedelta
from django.utils import timezone
from collections import defaultdict


class TaskChatbot:
    """
    Chatbot thông minh để parse natural language thành task data
    Hỗ trợ tiếng Việt và tiếng Anh
    """

    PRIORITY_KEYWORDS = {
        # Urgent
        "urgent": "Urgent",
        "khẩn": "Urgent",
        "gấp": "Urgent",
        "cấp bách": "Urgent",
        "ngay lập tức": "Urgent",
        "immediately": "Urgent",
        "asap": "Urgent",
        # High
        "high": "High",
        "cao": "High",
        "quan trọng": "High",
        "ưu tiên": "High",
        "priority": "High",
        "important": "High",
        # Medium
        "medium": "Medium",
        "trung bình": "Medium",
        "bình thường": "Medium",
        "normal": "Medium",
        # Low
        "low": "Low",
        "thấp": "Low",
        "không gấp": "Low",
        "có thể": "Low",
        "optional": "Low",
    }

    TIME_KEYWORDS = {
        # Hôm nay
        "hôm nay": 0,
        "today": 0,
        "bây giờ": 0,
        "now": 0,
        # Mai
        "mai": 1,
        "tomorrow": 1,
        "ngày mai": 1,
        # Ngày kia
        "ngày kia": 2,
        "mốt": 2,
        "day after tomorrow": 2,
        # Tuần này
        "cuối tuần": 5,
        "weekend": 5,
        "thứ 7": 5,
        "chủ nhật": 6,
        # Tuần sau
        "tuần sau": 7,
        "next week": 7,
        "tuần tới": 7,
        # Tháng sau
        "tháng sau": 30,
        "next month": 30,
    }
    
    # Thêm keywords cho các ngày trong tuần
    WEEKDAY_KEYWORDS = {
        "thứ 2": 0,
        "thứ hai": 0,
        "monday": 0,
        "thứ 3": 1,
        "thứ ba": 1,
        "tuesday": 1,
        "thứ 4": 2,
        "thứ tư": 2,
        "wednesday": 2,
        "thứ 5": 3,
        "thứ năm": 3,
        "thursday": 3,
        "thứ 6": 4,
        "thứ sáu": 4,
        "friday": 4,
        "thứ 7": 5,
        "thứ bảy": 5,
        "saturday": 5,
        "chủ nhật": 6,
        "sunday": 6,
    }
    
    # Action keywords để nhận diện intent
    ACTION_KEYWORDS = {
        "create": ["tạo", "thêm", "add", "create", "new", "làm", "viết"],
        "remind": ["nhắc", "remind", "nhắc nhở", "báo", "thông báo"],
        "deadline": ["deadline", "hạn", "đến hạn", "due", "hoàn thành"],
    }

    def parse_message(self, message):
        """
        Parse message thành task data - Enhanced version
        Returns: dict với title, description, priority, due_at
        """
        if not message or not message.strip():
            return self._get_default_task()
        
        message_lower = message.lower()
        
        # Validate input
        if len(message) > 500:
            message = message[:500]

        # Extract components
        title = self._extract_title(message)
        priority = self._extract_priority(message_lower)
        due_at = self._extract_due_date(message_lower)
        
        # Smart defaults
        if not title or len(title) < 2:
            title = "Task mới"
        
        # Validate due_at
        if due_at:
            now = timezone.now()
            if due_at < now:
                # If in past, move to tomorrow
                due_at = now + timedelta(days=1)
                due_at = due_at.replace(hour=due_at.hour, minute=0, second=0, microsecond=0)

        return {
            "title": title[:200],  # Limit length
            "description": f"Tạo từ chatbot",  # Shorter description
            "priority": priority,
            # Return naive datetime string (no timezone) to avoid conversion issues
            "due_at": due_at.strftime('%Y-%m-%dT%H:%M:%S') if due_at else None,
        }
    
    def _get_default_task(self):
        """Return default task when parsing fails"""
        return {
            "title": "Task mới",
            "description": "Tạo từ chatbot",
            "priority": "Medium",
            "due_at": (timezone.now() + timedelta(days=1)).isoformat(),
        }

    def _extract_title(self, message):
        """Extract title - Remove ALL time/priority metadata"""
        title = message.strip()
        
        # Remove action prefixes
        title = re.sub(r"^(tạo|thêm|add|create|new)\s+(task|công việc|việc)?\s*:?\s*", "", title, flags=re.IGNORECASE)
        title = re.sub(r"^(tôi|mình|em)\s+(cần|muốn|sẽ|phải)\s+", "", title, flags=re.IGNORECASE)
        
        # Remove ALL time expressions (anywhere in string)
        time_patterns = [
            r"\d+h\s+(ngày mai|mai|hôm nay|cho nay)",  # "8h ngày mai"
            r"(ngày mai|mai|hôm nay|cho nay)\s+\d+h",  # "ngày mai 8h"
            r"\s+lúc\s+\d+[h:]?\d*",  # "lúc 14h"
            r"\s+vào\s+\d+[h:]?\d*",  # "vào 9h"
            r"\s+\d+h\d*\s*",  # "8h", "14h30"
            r"\s+(ngày mai|mai|hôm nay|cho nay|bây giờ|ngay)",  # time keywords
            r"\s+(today|tomorrow|now)",
            r"\s+(sáng|chiều|tối|đêm)",
            r"\s+\d+[:/]\d+(/\d+)?",  # dates
            r"\s+(thứ|chủ nhật)\s*(hai|ba|tư|năm|sáu|bảy|2|3|4|5|6|7)?",
        ]
        for pattern in time_patterns:
            title = re.sub(pattern, " ", title, flags=re.IGNORECASE)
        
        # Remove priority keywords
        title = re.sub(r"\s*(gấp|khẩn|urgent|quan trọng|ưu tiên|cấp bách|asap|important)\s*", " ", title, flags=re.IGNORECASE)
        
        # Clean whitespace
        title = re.sub(r"\s+", " ", title).strip()
        
        # Validate
        if len(title) < 2:
            return "Task mới"
        
        return title

    def _extract_priority(self, message_lower):
        """Extract priority - Enhanced with context"""
        # Check for urgent indicators first (highest priority)
        urgent_indicators = ["!!!", "!!!", "asap", "ngay lập tức", "cấp bách", "khẩn cấp"]
        for indicator in urgent_indicators:
            if indicator in message_lower:
                return "Urgent"
        
        # Check keywords by priority order
        priority_order = [
            ("Urgent", ["urgent", "khẩn", "gấp"]),
            ("High", ["high", "cao", "quan trọng", "ưu tiên", "important"]),
            ("Low", ["low", "thấp", "không gấp", "có thể", "optional"]),
        ]
        
        for priority, keywords in priority_order:
            for keyword in keywords:
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
        """Extract due date - Smart time understanding"""
        now = timezone.now()
        
        # CRITICAL: "cho nay" = "hôm nay" (today)
        # Extended time keywords - ORDER MATTERS (longer first)
        extended_time = {
            # Today variations (HIGHEST PRIORITY)
            "cho nay": 0,
            "hôm nay": 0,
            "bây giờ": 0,
            "ngay bây giờ": 0,
            "ngay lập tức": 0,
            "ngay": 0,
            "today": 0,
            "now": 0,
            # Tomorrow
            "ngày mai": 1,
            "mai": 1,
            "tomorrow": 1,
            # Day after tomorrow
            "ngày kia": 2,
            "mốt": 2,
            "2 ngày nữa": 2,
            # This week
            "3 ngày nữa": 3,
            "4 ngày nữa": 4,
            "5 ngày nữa": 5,
            "tuần này": 3,
            "cuối tuần": 5,
            "weekend": 5,
            # Next week
            "tuần sau": 7,
            "tuần tới": 7,
            "next week": 7,
            "2 tuần nữa": 14,
            # This/next month
            "tháng này": 15,
            "tháng sau": 30,
            "tháng tới": 30,
            "next month": 30,
        }
        
        # Check weekdays first (more specific)
        for weekday_name, weekday_num in self.WEEKDAY_KEYWORDS.items():
            if weekday_name in message_lower:
                current_weekday = now.weekday()
                days_ahead = weekday_num - current_weekday
                
                if days_ahead <= 0:
                    days_ahead += 7
                
                due_date = now + timedelta(days=days_ahead)
                hour = self._extract_hour(message_lower)
                
                due_date = due_date.replace(
                    hour=hour if hour is not None else 23,
                    minute=0 if hour is not None else 59,
                    second=0,
                    microsecond=0
                )
                return due_date
        
        # Check relative time (SORT BY LENGTH - longer phrases first)
        for keyword, days_offset in sorted(extended_time.items(), key=lambda x: -len(x[0])):
            if keyword in message_lower:
                due_date = now + timedelta(days=days_offset)
                hour = self._extract_hour(message_lower)
                
                # Smart hour defaults
                if hour is not None:
                    due_date = due_date.replace(hour=hour, minute=0, second=0, microsecond=0)
                elif days_offset == 0:
                    # Today: default to end of work day (18:00)
                    due_date = due_date.replace(hour=18, minute=0, second=0, microsecond=0)
                else:
                    # Future: default to end of day
                    due_date = due_date.replace(hour=23, minute=59, second=0, microsecond=0)
                
                return due_date
        
        # Check specific date format
        date_match = re.search(r"(\d{1,2})[/-](\d{1,2})(?:[/-](\d{2,4}))?", message_lower)
        if date_match:
            try:
                day = int(date_match.group(1))
                month = int(date_match.group(2))
                year = int(date_match.group(3)) if date_match.group(3) else now.year
                
                if year < 100:
                    year += 2000
                
                # Validate date
                if 1 <= day <= 31 and 1 <= month <= 12:
                    due_date = now.replace(year=year, month=month, day=day)
                    hour = self._extract_hour(message_lower)
                    
                    due_date = due_date.replace(
                        hour=hour if hour is not None else 23,
                        minute=0 if hour is not None else 59,
                        second=0,
                        microsecond=0
                    )
                    return due_date
            except (ValueError, AttributeError):
                pass
        
        # Default: today at end of work day (assume urgent if no time specified)
        return now.replace(hour=18, minute=0, second=0, microsecond=0)

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
        """Extract giờ cụ thể - Fixed version"""
        # Priority order: more specific patterns first
        
        # Format: "lúc 14h", "vào 9h"
        time_with_h = re.search(r"(lúc|vào)\s*(\d{1,2})h", message_lower)
        if time_with_h:
            hour = int(time_with_h.group(2))
            if 0 <= hour <= 23:
                return hour
        
        # Format: "14h", "9h" (standalone)
        hour_h = re.search(r"\b(\d{1,2})h\b", message_lower)
        if hour_h:
            hour = int(hour_h.group(1))
            if 0 <= hour <= 23:
                return hour
        
        # Format: "lúc 14", "vào 9"
        time_no_h = re.search(r"(lúc|vào|at)\s*(\d{1,2})\b", message_lower)
        if time_no_h:
            hour = int(time_no_h.group(2))
            if 0 <= hour <= 23:
                return hour
        
        # Format: "14:00", "9:30"
        time_colon = re.search(r"\b(\d{1,2}):(\d{2})\b", message_lower)
        if time_colon:
            hour = int(time_colon.group(1))
            if 0 <= hour <= 23:
                return hour
        
        # Format: "2pm", "9am"
        ampm = re.search(r"\b(\d{1,2})\s*(am|pm)\b", message_lower)
        if ampm:
            hour = int(ampm.group(1))
            period = ampm.group(2)
            
            if period == "pm" and hour < 12:
                hour += 12
            elif period == "am" and hour == 12:
                hour = 0
            
            if 0 <= hour <= 23:
                return hour

        return None

    def generate_response(self, task_data, prediction=None):
        """Generate response - Clean and informative"""
        title = task_data.get("title", "Task")
        priority = task_data.get("priority", "Medium")
        
        lines = ["Đã tạo task thành công!", ""]
        lines.append(f"Tiêu đề: {title}")
        lines.append(f"Mức ưu tiên: {priority}")

        if task_data.get("due_at"):
            try:
                due = datetime.fromisoformat(
                    task_data["due_at"].replace("Z", "+00:00")
                )
                now = timezone.now()
                time_diff = due - now
                days = time_diff.days
                hours = time_diff.seconds // 3600
                
                lines.append(f"Deadline: {due.strftime('%d/%m/%Y lúc %H:%M')}")
                
                if days > 1:
                    lines.append(f"Còn: {days} ngày")
                elif days == 1:
                    lines.append(f"Còn: 1 ngày {hours} giờ")
                elif hours > 0:
                    lines.append(f"Còn: {hours} giờ")
                else:
                    lines.append("Còn: ít hơn 1 giờ")
            except:
                pass

        if prediction:
            confidence = int(prediction.get('confidence', 0) * 100)
            lines.append("")
            if prediction.get("on_time_prediction") == 1:
                lines.append(f"AI dự đoán: Có thể hoàn thành đúng hạn ({confidence}% tin cậy)")
            else:
                lines.append(f"AI cảnh báo: Có nguy cơ trễ hạn ({confidence}% tin cậy)")
                if confidence > 70:
                    lines.append("Gợi ý: Nên bắt đầu sớm hơn")

        return "\n".join(lines)
    
    def detect_intent(self, message):
        """Detect user intent from message"""
        message_lower = message.lower()
        
        # Check for create intent
        for keyword in self.ACTION_KEYWORDS["create"]:
            if keyword in message_lower:
                return "create"
        
        # Check for remind intent
        for keyword in self.ACTION_KEYWORDS["remind"]:
            if keyword in message_lower:
                return "remind"
        
        # Default to create
        return "create"
