# -*- coding: utf-8 -*-
"""
健康评估算法实现 - KMeans 与 SOM（自组织映射神经网络）
两种算法通过接口统一，可互相替换。
"""

import numpy as np
from .interfaces import HealthAssessorInterface

# 健康状态枚举（由阈值划分得出）: 0=正常, 1=轻度异常, 2=重度异常
HEALTH_NORMAL = 0
HEALTH_MILD = 1
HEALTH_SEVERE = 2

STATUS_LABELS = {0: "正常", 1: "轻度异常", 2: "重度异常"}


def score_to_grade(score: float, normal_min: float = 90, mild_min: float = 70) -> int:
    """根据分数与阈值划分为等级。score>=normal_min->正常, >=mild_min->轻度异常, 否则->重度异常"""
    if score >= normal_min:
        return HEALTH_NORMAL
    if score >= mild_min:
        return HEALTH_MILD
    return HEALTH_SEVERE


class KMeansAssessor(HealthAssessorInterface):
    """基于 K-Means 的健康评估：以到最近聚类中心的距离判断异常程度"""

    def __init__(self, n_clusters: int = 3, mild_percentile: float = 90, severe_percentile: float = 98):
        """
        :param n_clusters: 聚类数量
        :param mild_percentile: 训练集距离百分位，超过则为轻度异常
        :param severe_percentile: 训练集距离百分位，超过则为重度异常
        """
        self.n_clusters = n_clusters
        self.mild_percentile = mild_percentile
        self.severe_percentile = severe_percentile
        self.centroids_: np.ndarray | None = None
        self.dist_threshold_mild_: float = 0.0
        self.dist_threshold_severe_: float = 0.0
        self._fitted = False

    def _kmeans_fit(self, X: np.ndarray, max_iter: int = 100) -> np.ndarray:
        """简单 K-Means 实现"""
        n_samples = X.shape[0]
        rng = np.random.default_rng(42)
        idx = rng.choice(n_samples, size=min(self.n_clusters, n_samples), replace=False)
        centroids = X[idx].copy()
        for _ in range(max_iter):
            dists = np.linalg.norm(X[:, np.newaxis] - centroids, axis=2)
            labels = np.argmin(dists, axis=1)
            new_centroids = np.array([X[labels == k].mean(axis=0) if np.any(labels == k) else centroids[k]
                                      for k in range(self.n_clusters)])
            if np.allclose(centroids, new_centroids):
                break
            centroids = new_centroids
        return centroids

    def _min_dist_to_centroids(self, X: np.ndarray) -> np.ndarray:
        """每个样本到最近聚类中心的距离"""
        dists = np.linalg.norm(X[:, np.newaxis] - self.centroids_, axis=2)
        return np.min(dists, axis=1)

    def fit(self, X: np.ndarray) -> "KMeansAssessor":
        X = np.asarray(X, dtype=float)
        X = np.nan_to_num(X, nan=0)
        self.centroids_ = self._kmeans_fit(X)
        train_dists = self._min_dist_to_centroids(X)
        self.dist_threshold_mild_ = np.percentile(train_dists, self.mild_percentile)
        self.dist_threshold_severe_ = np.percentile(train_dists, self.severe_percentile)
        self._fitted = True
        return self

    def assess(self, X: np.ndarray) -> np.ndarray:
        """返回健康分数 [0,100]，距离越小分数越高"""
        if not self._fitted or self.centroids_ is None:
            raise RuntimeError("Assessor must be fitted before assess")
        X = np.asarray(X, dtype=float)
        X = np.nan_to_num(X, nan=0)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        dists = self._min_dist_to_centroids(X)
        ref = max(self.dist_threshold_severe_, 1e-6)
        scores = np.clip(100 * (1 - dists / ref), 0, 100)
        return scores.astype(float)


class SOMAssessor(HealthAssessorInterface):
    """基于 SOM（自组织映射）的健康评估：以到 BMU 的量化误差判断异常程度"""

    def __init__(self, som_shape: tuple = (3, 3), mild_percentile: float = 90, severe_percentile: float = 98):
        """
        :param som_shape: SOM 网格形状 (rows, cols)
        :param mild_percentile: 训练集量化误差百分位
        :param severe_percentile: 训练集量化误差百分位
        """
        self.som_shape = som_shape
        self.mild_percentile = mild_percentile
        self.severe_percentile = severe_percentile
        self._som = None
        self._weights: np.ndarray | None = None
        self.qe_threshold_mild_: float = 0.0
        self.qe_threshold_severe_: float = 0.0
        self._fitted = False

    def _init_som(self, n_features: int) -> None:
        try:
            from minisom import MiniSom
        except ImportError:
            raise ImportError("请安装 minisom: pip install minisom")
        r, c = self.som_shape
        self._som = MiniSom(r, c, n_features, sigma=1.0, learning_rate=0.5, random_seed=42)
        self._som.random_weights_init(np.zeros((1, n_features)) + 0.5)  # 简单初始化

    def _quantization_error(self, X: np.ndarray) -> np.ndarray:
        """每个样本的量化误差（到 BMU 的距离）"""
        if self._som is None or self._weights is None:
            raise RuntimeError("SOM not fitted")
        n = X.shape[0]
        qe = np.zeros(n)
        for i in range(n):
            bmu = self._som.winner(X[i])
            qe[i] = np.linalg.norm(X[i] - self._som.get_weights()[bmu])
        return qe

    def fit(self, X: np.ndarray) -> "SOMAssessor":
        X = np.asarray(X, dtype=float)
        X = np.nan_to_num(X, nan=0)
        n_features = X.shape[1]
        self._init_som(n_features)
        self._som.train(X, num_iteration=100, verbose=False)
        self._weights = self._som.get_weights()
        train_qe = self._quantization_error(X)
        self.qe_threshold_mild_ = np.percentile(train_qe, self.mild_percentile)
        self.qe_threshold_severe_ = np.percentile(train_qe, self.severe_percentile)
        self._fitted = True
        return self

    def assess(self, X: np.ndarray) -> np.ndarray:
        """返回健康分数 [0,100]，量化误差越小分数越高"""
        if not self._fitted or self._som is None:
            raise RuntimeError("Assessor must be fitted before assess")
        X = np.asarray(X, dtype=float)
        X = np.nan_to_num(X, nan=0)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        qe = self._quantization_error(X)
        ref = max(self.qe_threshold_severe_, 1e-6)
        scores = np.clip(100 * (1 - qe / ref), 0, 100)
        return scores.astype(float)
