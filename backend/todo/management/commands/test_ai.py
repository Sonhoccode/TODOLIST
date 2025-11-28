"""
Management command để test AI prediction
Usage: python manage.py test_ai
"""
from django.core.management.base import BaseCommand
from todo.services.ai import predict_task_on_time, _ModelHolder
import os


class Command(BaseCommand):
    help = 'Test AI prediction feature'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=== Testing AI Prediction ===\n'))

        # Test 1: Check dependencies
        self.stdout.write('1. Checking dependencies...')
        try:
            import joblib
            import numpy as np
            self.stdout.write(self.style.SUCCESS('   ✅ joblib and numpy installed'))
        except ImportError as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Missing dependency: {e}'))
            self.stdout.write(self.style.WARNING('   Run: pip install joblib numpy scikit-learn'))
            return

        # Test 2: Check model file
        self.stdout.write('\n2. Checking model file...')
        from todo.services.ai import DEFAULT_MODEL_PATH
        if os.path.exists(DEFAULT_MODEL_PATH):
            self.stdout.write(self.style.SUCCESS(f'   ✅ Model file exists: {DEFAULT_MODEL_PATH}'))
        else:
            self.stdout.write(self.style.ERROR(f'   ❌ Model file not found: {DEFAULT_MODEL_PATH}'))
            self.stdout.write(self.style.WARNING('   AI will use fallback prediction'))

        # Test 3: Try to load model
        self.stdout.write('\n3. Loading model...')
        try:
            model = _ModelHolder.get()
            if model is not None:
                self.stdout.write(self.style.SUCCESS('   ✅ Model loaded successfully'))
            else:
                self.stdout.write(self.style.WARNING('   ⚠️  Model not loaded, will use fallback'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Model load failed: {e}'))
            self.stdout.write(self.style.WARNING('   AI will use fallback prediction'))

        # Test 4: Test prediction with dummy task
        self.stdout.write('\n4. Testing prediction...')
        
        class DummyTask:
            def __init__(self):
                self.priority = "Medium"
                self.estimated_duration_min = 60
                
            @property
            def priority_numeric(self):
                return 2

        try:
            task = DummyTask()
            extra_data = {
                "estimated_duration_min": 60,
                "start_hour": 10,
                "day_of_week": 2,
            }
            
            result = predict_task_on_time(task, extra_data=extra_data, return_confidence=True)
            
            self.stdout.write(self.style.SUCCESS('   ✅ Prediction successful'))
            self.stdout.write(f'   Result: {result}')
            
            if result.get('fallback'):
                self.stdout.write(self.style.WARNING('   ⚠️  Using fallback prediction (not ML model)'))
            else:
                self.stdout.write(self.style.SUCCESS('   ✅ Using ML model prediction'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   ❌ Prediction failed: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('\n✅ AI Test Complete!'))
        self.stdout.write('\nIf you see warnings above, AI will still work using fallback.')
        self.stdout.write('To use ML model, ensure model.pkl exists and is valid.\n')
