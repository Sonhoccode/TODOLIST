import React, { useState, useEffect } from 'react';
import { predictTaskCompletion, prepareAIPredictionData } from '../../api/ai';

/**
 * Component hiển thị dự đoán AI về khả năng hoàn thành task đúng hạn
 */
const AIPrediction = ({ formData, show = true }) => {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!show || !formData.priority) {
      setPrediction(null);
      return;
    }

    const fetchPrediction = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const aiData = prepareAIPredictionData(formData);
        const result = await predictTaskCompletion(aiData);
        setPrediction(result);
      } catch (err) {
        setError('Không thể dự đoán');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    // Debounce: chỉ gọi API sau 500ms không có thay đổi
    const timer = setTimeout(fetchPrediction, 500);
    return () => clearTimeout(timer);
  }, [formData.priority, formData.estimated_duration_min, formData.planned_start_at, formData.due_at, show]);

  if (!show) return null;
  if (loading) {
    return (
      <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
        <div className="flex items-center space-x-2">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          <span className="text-sm text-gray-600">Đang phân tích...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mt-4 p-4 bg-red-50 rounded-lg border border-red-200">
        <p className="text-sm text-red-600">⚠️ {error}</p>
      </div>
    );
  }

  if (!prediction) return null;

  const isOnTime = prediction.on_time_prediction === 1;
  const confidence = Math.round(prediction.confidence * 100);

  return (
    <div className={`mt-4 p-4 rounded-lg border ${
      isOnTime 
        ? 'bg-green-50 border-green-200' 
        : 'bg-yellow-50 border-yellow-200'
    }`}>
      <div className="flex items-start space-x-3">
        <div className="text-2xl">
          {isOnTime ? '✅' : '⚠️'}
        </div>
        <div className="flex-1">
          <h4 className="font-semibold text-sm mb-1">
            {isOnTime ? 'Dự đoán: Hoàn thành đúng hạn' : 'Dự đoán: Có thể trễ hạn'}
          </h4>
          <p className="text-xs text-gray-600 mb-2">
            Độ tin cậy: <span className="font-medium">{confidence}%</span>
          </p>
          {!isOnTime && (
            <p className="text-xs text-gray-700">
              💡 Gợi ý: Hãy xem xét giảm thời lượng, tăng mức ưu tiên, hoặc chọn thời gian bắt đầu phù hợp hơn.
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default AIPrediction;
