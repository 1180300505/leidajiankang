# -*- coding: utf-8 -*-
"""
健康评估服务 - 整合数据处理与评估算法，输出整体 + 子系统健康状态
支持 KMeans / SOM 两种算法及对应数据处理器，可互相替换。
"""

from typing import Dict, List, Any, Optional
from enum import IntEnum

import numpy as np

from .interfaces import DataProcessorInterface, HealthAssessorInterface
from .data_processors import StandardScalerProcessor, MinMaxProcessor
from .assessors import KMeansAssessor, SOMAssessor, STATUS_LABELS, score_to_grade
from .feature_extractor import (
    extract_turntable_features,
    extract_electrofeed_features,
    extract_turntable_from_dict,
    extract_electrofeed_from_dict,
)


class HealthStatus(IntEnum):
    """健康状态"""
    正常 = 0
    轻度异常 = 1
    重度异常 = 2


# 预设算法组合：算法名 -> (DataProcessor, HealthAssessor)
ALGORITHM_PRESETS = {
    "kmeans": (StandardScalerProcessor, KMeansAssessor),
    "som": (MinMaxProcessor, SOMAssessor),
}


# 默认分级阈值：分数>=normal_min 正常，>=mild_min 轻度异常，否则重度异常
DEFAULT_THRESHOLD_NORMAL = 90
DEFAULT_THRESHOLD_MILD = 70


class HealthService:
    """
    健康评估服务（打分制 + 阈值分级）
    - 算法输出 0-100 分数，再按阈值划分为 正常/轻度异常/重度异常
    - 整体健康度 = 转台系 + 电馈系 综合（取最低分）
    """

    def __init__(self, algorithm: str = "kmeans", min_train_samples: int = 10,
                 threshold_normal: float = DEFAULT_THRESHOLD_NORMAL,
                 threshold_mild: float = DEFAULT_THRESHOLD_MILD):
        """
        :param algorithm: "kmeans" 或 "som"
        :param min_train_samples: 最少训练样本数，不足时返回默认正常
        :param threshold_normal: 正常下限，分数>=此值为正常
        :param threshold_mild: 轻度异常下限，分数>=此值为轻度异常，否则为重度异常
        """
        if algorithm not in ALGORITHM_PRESETS:
            raise ValueError(f"algorithm 须为 {list(ALGORITHM_PRESETS.keys())} 之一")
        self.algorithm = algorithm
        self.min_train_samples = min_train_samples
        self.threshold_normal = threshold_normal
        self.threshold_mild = threshold_mild
        proc_cls, assess_cls = ALGORITHM_PRESETS[algorithm]
        self._processor_tt: DataProcessorInterface = proc_cls()
        self._processor_ef: DataProcessorInterface = proc_cls()
        self._assessor_tt: HealthAssessorInterface = assess_cls()
        self._assessor_ef: HealthAssessorInterface = assess_cls()
        self._trained = False

    def fit(self, rows: List[Dict]) -> "HealthService":
        """
        使用历史 DB 记录训练模型
        :param rows: database.query_paged 或 query_range 返回的字典列表
        """
        X_tt = extract_turntable_features(rows)
        X_ef = extract_electrofeed_features(rows)
        if len(X_tt) < self.min_train_samples or len(X_ef) < self.min_train_samples:
            self._trained = False
            return self
        self._processor_tt.fit(X_tt)
        self._processor_ef.fit(X_ef)
        X_tt_t = self._processor_tt.transform(X_tt)
        X_ef_t = self._processor_ef.transform(X_ef)
        self._assessor_tt.fit(X_tt_t)
        self._assessor_ef.fit(X_ef_t)
        self._trained = True
        return self

    def assess_from_rows(self, rows: List[Dict]) -> Dict[str, Any]:
        """
        从 DB 行列表评估健康状态
        :return: { "overall": "正常|轻度异常|重度异常", "turntable": ..., "electrofeed": ... }
        """
        if not rows:
            return self._default_result()
        X_tt = extract_turntable_features(rows)
        X_ef = extract_electrofeed_features(rows)
        return self._assess_impl(X_tt, X_ef)

    def assess_from_dict(self, data: dict) -> Dict[str, Any]:
        """从单条 JSON 数据评估"""
        X_tt = extract_turntable_from_dict(data)
        X_ef = extract_electrofeed_from_dict(data)
        return self._assess_impl(X_tt, X_ef)

    def _assess_impl(self, X_tt: np.ndarray, X_ef: np.ndarray) -> Dict[str, Any]:
        if not self._trained:
            return self._default_result()
        try:
            X_tt_t = self._processor_tt.transform(X_tt)
            X_ef_t = self._processor_ef.transform(X_ef)
            score_tt = float(self._assessor_tt.assess(X_tt_t)[-1]) if len(X_tt_t) else 100.0
            score_ef = float(self._assessor_ef.assess(X_ef_t)[-1]) if len(X_ef_t) else 100.0
        except Exception:
            return self._default_result()
        score_tt = round(score_tt, 1)
        score_ef = round(score_ef, 1)
        score_overall = min(score_tt, score_ef)  # 取最低分
        grade_tt = score_to_grade(score_tt, self.threshold_normal, self.threshold_mild)
        grade_ef = score_to_grade(score_ef, self.threshold_normal, self.threshold_mild)
        grade_overall = max(grade_tt, grade_ef)  # 取最差等级
        return {
            "overall": STATUS_LABELS[grade_overall],
            "turntable": STATUS_LABELS[grade_tt],
            "electrofeed": STATUS_LABELS[grade_ef],
            "overall_code": grade_overall,
            "turntable_code": grade_tt,
            "electrofeed_code": grade_ef,
            "overall_score": score_overall,
            "turntable_score": score_tt,
            "electrofeed_score": score_ef,
        }

    def _default_result(self) -> Dict[str, Any]:
        return {
            "overall": "正常",
            "turntable": "正常",
            "electrofeed": "正常",
            "overall_code": 0,
            "turntable_code": 0,
            "electrofeed_code": 0,
            "overall_score": 95.0,
            "turntable_score": 95.0,
            "electrofeed_score": 95.0,
        }


def create_health_service(algorithm: str = "kmeans", **kwargs) -> HealthService:
    """工厂函数：创建健康评估服务"""
    return HealthService(algorithm=algorithm, **kwargs)


def train_from_db(db, algorithm: str = "kmeans", max_samples: int = 500,
                  threshold_normal: float = DEFAULT_THRESHOLD_NORMAL,
                  threshold_mild: float = DEFAULT_THRESHOLD_MILD) -> HealthService:
    """
    从数据库加载最近数据并训练健康评估服务
    :param db: DeviceDB 实例
    :param algorithm: "kmeans" 或 "som"
    :param max_samples: 最多使用的训练样本数
    :param threshold_normal: 正常下限
    :param threshold_mild: 轻度异常下限
    """
    data, total = db.query_paged(page=1, page_size=max_samples, sort_order="ASC")
    svc = HealthService(algorithm=algorithm, threshold_normal=threshold_normal, threshold_mild=threshold_mild)
    svc.fit(data)
    return svc
