# 健康评估模块 - 支持 KMeans 与 SOM 两种可替换算法
from .interfaces import DataProcessorInterface, HealthAssessorInterface
from .data_processors import StandardScalerProcessor, MinMaxProcessor
from .assessors import KMeansAssessor, SOMAssessor, STATUS_LABELS, score_to_grade
from .health_service import HealthService, HealthStatus, train_from_db

__all__ = [
    "DataProcessorInterface",
    "HealthAssessorInterface",
    "StandardScalerProcessor",
    "MinMaxProcessor",
    "KMeansAssessor",
    "SOMAssessor",
    "HealthService",
    "HealthStatus",
    "train_from_db",
    "STATUS_LABELS",
    "score_to_grade",
]
