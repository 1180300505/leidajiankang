# -*- coding: utf-8 -*-
"""
数据处理算法实现 - 与健康评估算法配套使用
StandardScalerProcessor 适合 KMeans
MinMaxProcessor 适合 SOM（自组织映射对 [0,1] 归一化更敏感）
"""

import numpy as np
from .interfaces import DataProcessorInterface


class StandardScalerProcessor(DataProcessorInterface):
    """标准归一化处理器 - 零均值、单位方差，适合 KMeans"""

    def __init__(self):
        self.mean_: np.ndarray | None = None
        self.std_: np.ndarray | None = None
        self._fitted = False

    def fit(self, X: np.ndarray) -> "StandardScalerProcessor":
        X = np.asarray(X, dtype=float)
        self.mean_ = np.nanmean(X, axis=0)
        self.std_ = np.nanstd(X, axis=0)
        self.std_[self.std_ == 0] = 1.0  # 避免除零
        self._fitted = True
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        if not self._fitted or self.mean_ is None or self.std_ is None:
            raise RuntimeError("Processor must be fitted before transform")
        X = np.asarray(X, dtype=float)
        X = np.nan_to_num(X, nan=self.mean_[0], posinf=0, neginf=0)
        return (X - self.mean_) / self.std_


class MinMaxProcessor(DataProcessorInterface):
    """最小-最大归一化处理器 - 缩放到 [0,1]，适合 SOM"""

    def __init__(self, feature_range=(0, 1)):
        self.min_: np.ndarray | None = None
        self.range_: np.ndarray | None = None
        self.feature_range = feature_range
        self._fitted = False

    def fit(self, X: np.ndarray) -> "MinMaxProcessor":
        X = np.asarray(X, dtype=float)
        X_clean = np.nan_to_num(X, nan=0, posinf=0, neginf=0)
        self.min_ = np.min(X_clean, axis=0)
        max_ = np.max(X_clean, axis=0)
        self.range_ = max_ - self.min_
        self.range_[self.range_ == 0] = 1.0  # 避免除零
        self._fitted = True
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        if not self._fitted or self.min_ is None or self.range_ is None:
            raise RuntimeError("Processor must be fitted before transform")
        X = np.asarray(X, dtype=float)
        X = np.nan_to_num(X, nan=self.min_[0], posinf=0, neginf=0)
        lo, hi = self.feature_range
        return lo + (X - self.min_) / self.range_ * (hi - lo)
