# -*- coding: utf-8 -*-
"""
健康评估模块 - 接口定义
数据处理算法与健康评估算法均通过接口实现，可互相替换。
"""

from abc import ABC, abstractmethod
from typing import Any
import numpy as np


class DataProcessorInterface(ABC):
    """数据预处理接口 - 不同健康评估算法可搭配不同的数据处理方式"""

    @abstractmethod
    def fit(self, X: np.ndarray) -> "DataProcessorInterface":
        """根据训练数据拟合处理器"""
        pass

    @abstractmethod
    def transform(self, X: np.ndarray) -> np.ndarray:
        """对数据进行变换"""
        pass

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """拟合并变换"""
        return self.fit(X).transform(X)


class HealthAssessorInterface(ABC):
    """健康评估算法接口 - KMeans、SOM 等可互相替换"""

    @abstractmethod
    def fit(self, X: np.ndarray) -> "HealthAssessorInterface":
        """使用正常/基线数据训练模型"""
        pass

    @abstractmethod
    def assess(self, X: np.ndarray) -> np.ndarray:
        """
        评估健康分数（打分制）
        :return: 每行对应一个样本的健康分数数组，范围 [0, 100]，分数越高越健康
        """
        pass
