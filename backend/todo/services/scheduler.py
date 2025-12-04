# todo/services/scheduler.py
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Q


class AITaskScheduler:
    """
    AI-powered task scheduler
    Automatically schedule tasks based on priority, deadline, and AI prediction
    """
    
    def __init__(self, user):
        self.user = user
        self.now = timezone.now()
    
    def schedule_today(self, available_hours=8, start_hour=9):
        """
        Schedule tasks for today
        
        Args:
            available_hours: How many hours available (default 8)
            start_hour: Start hour (default 9am)
        
        Returns:
            List of scheduled tasks with suggested times
        """
        from todo.models import Todo
        
        # Get incomplete tasks (exclude tasks with fixed remind_at time)
        tasks = Todo.objects.filter(
            owner=self.user,
            completed=False
        ).select_related('category').order_by('due_at')
        
        # Separate tasks: flexible vs fixed time
        flexible_tasks = []
        fixed_time_tasks = []
        
        for task in tasks:
            if task.remind_at and task.remind_at > self.now:
                # Task has a fixed reminder time in the future
                fixed_time_tasks.append(task)
            else:
                # Task is flexible, can be scheduled
                flexible_tasks.append(task)
        
        # Score and sort flexible tasks
        scored_tasks = []
        for task in flexible_tasks:
            score = self._calculate_priority_score(task)
            scored_tasks.append({
                'task': task,
                'score': score,
                'estimated_hours': self._estimate_duration(task)
            })
        
        # Sort by score (highest first)
        scored_tasks.sort(key=lambda x: x['score'], reverse=True)
        
        # Add fixed time tasks to schedule first (if within time range)
        fixed_schedule = []
        for task in fixed_time_tasks:
            remind_time = task.remind_at
            if remind_time >= current_time and remind_time < current_time + timedelta(hours=available_hours):
                duration = self._estimate_duration(task)
                end_time = remind_time + timedelta(hours=duration)
                fixed_schedule.append({
                    'task_id': task.id,
                    'title': task.title,
                    'priority': task.priority,
                    'score': 100,  # Fixed time = highest priority
                    'start_time': remind_time.strftime('%Y-%m-%dT%H:%M:%S'),
                    'end_time': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
                    'duration_hours': duration,
                    'reason': 'Lịch cố định (nhắc lúc ' + remind_time.strftime('%H:%M') + ')'
                })
        
        # Schedule tasks
        schedule = []
        
        # Smart start time: always start from next available hour
        # If user input is in the past, use current time + 1 hour
        user_start_time = self.now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        
        if user_start_time <= self.now:
            # User's time has passed, use next hour from now
            next_hour = self.now.hour + 1
            current_time = self.now.replace(hour=next_hour, minute=0, second=0, microsecond=0)
        else:
            # User's time is in the future, use it
            current_time = user_start_time
        
        total_hours = 0
        
        for item in scored_tasks:
            if total_hours >= available_hours:
                break
            
            task = item['task']
            duration = item['estimated_hours']
            
            if total_hours + duration <= available_hours:
                end_time = current_time + timedelta(hours=duration)
                
                schedule.append({
                    'task_id': task.id,
                    'title': task.title,
                    'priority': task.priority,
                    'score': item['score'],
                    # Return naive datetime string (no timezone) to avoid conversion issues
                    'start_time': current_time.strftime('%Y-%m-%dT%H:%M:%S'),
                    'end_time': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
                    'duration_hours': duration,
                    'reason': self._get_reason(task, item['score'])
                })
                
                current_time = end_time
                total_hours += duration
        
        # Merge fixed and flexible schedules, sort by time
        all_schedule = fixed_schedule + schedule
        all_schedule.sort(key=lambda x: x['start_time'])
        
        return {
            'schedule': all_schedule,
            'total_hours': total_hours,
            'available_hours': available_hours,
            'utilization': (total_hours / available_hours * 100) if available_hours > 0 else 0,
            'fixed_tasks': len(fixed_schedule),
            'flexible_tasks': len(schedule)
        }
    
    def schedule_week(self, hours_per_day=6):
        """Schedule tasks for the week"""
        from todo.models import Todo
        
        tasks = Todo.objects.filter(
            owner=self.user,
            completed=False
        ).select_related('category')
        
        # Group by urgency
        urgent = []
        high = []
        medium = []
        low = []
        
        for task in tasks:
            score = self._calculate_priority_score(task)
            item = {
                'task': task,
                'score': score,
                'estimated_hours': self._estimate_duration(task)
            }
            
            if score >= 90:
                urgent.append(item)
            elif score >= 70:
                high.append(item)
            elif score >= 40:
                medium.append(item)
            else:
                low.append(item)
        
        # Create weekly schedule
        weekly_schedule = []
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        all_tasks = urgent + high + medium + low
        task_index = 0
        
        for day_num, day_name in enumerate(days):
            day_schedule = []
            day_hours = 0
            
            while day_hours < hours_per_day and task_index < len(all_tasks):
                item = all_tasks[task_index]
                duration = item['estimated_hours']
                
                if day_hours + duration <= hours_per_day:
                    day_schedule.append({
                        'task_id': item['task'].id,
                        'title': item['task'].title,
                        'priority': item['task'].priority,
                        'duration_hours': duration,
                        'score': item['score']
                    })
                    day_hours += duration
                    task_index += 1
                else:
                    break
            
            weekly_schedule.append({
                'day': day_name,
                'day_number': day_num,
                'tasks': day_schedule,
                'total_hours': day_hours
            })
        
        return {
            'weekly_schedule': weekly_schedule,
            'total_tasks_scheduled': task_index,
            'total_tasks': len(all_tasks)
        }
    
    def _calculate_priority_score(self, task):
        """
        Calculate priority score (0-100)
        Higher = more urgent/important
        """
        score = 0
        
        # Priority weight (40 points max)
        priority_weights = {
            'Urgent': 40,
            'High': 30,
            'Medium': 20,
            'Low': 10
        }
        score += priority_weights.get(task.priority, 20)
        
        # Deadline urgency (40 points max)
        if task.due_at:
            time_until_due = task.due_at - self.now
            hours_until_due = time_until_due.total_seconds() / 3600
            
            if hours_until_due < 0:
                # Overdue!
                score += 40
            elif hours_until_due < 24:
                # Due today
                score += 35
            elif hours_until_due < 48:
                # Due tomorrow
                score += 30
            elif hours_until_due < 168:
                # Due this week
                score += 20
            else:
                # Due later
                score += 10
        else:
            # No deadline
            score += 5
        
        # AI prediction (20 points max)
        # If task has high risk of being late, increase priority
        try:
            from todo.services.ai import predict_task_on_time
            prediction = predict_task_on_time(task, return_confidence=True)
            
            if prediction.get('on_time_prediction') == 0:
                # High risk of being late
                confidence = prediction.get('confidence', 0)
                score += int(20 * confidence)
        except:
            pass
        
        return min(score, 100)
    
    def _estimate_duration(self, task):
        """Estimate task duration in hours"""
        # Simple heuristic based on priority
        # In real app, could use ML or user input
        priority_durations = {
            'Urgent': 2,
            'High': 3,
            'Medium': 2,
            'Low': 1
        }
        return priority_durations.get(task.priority, 2)
    
    def _get_reason(self, task, score):
        """Get human-readable reason for scheduling"""
        reasons = []
        
        if task.priority in ['Urgent', 'High']:
            reasons.append(f"{task.priority} priority")
        
        if task.due_at:
            time_until_due = task.due_at - self.now
            hours_until_due = time_until_due.total_seconds() / 3600
            
            if hours_until_due < 0:
                reasons.append("Overdue!")
            elif hours_until_due < 24:
                reasons.append("Due today")
            elif hours_until_due < 48:
                reasons.append("Due tomorrow")
        
        if score >= 90:
            reasons.append("Critical")
        
        return ", ".join(reasons) if reasons else "Scheduled"
