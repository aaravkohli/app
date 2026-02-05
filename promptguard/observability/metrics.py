"""
Prometheus metrics and monitoring
"""

import logging
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Prometheus metrics for system monitoring"""
    
    def __init__(self):
        self.registry = CollectorRegistry()
        self._setup_metrics()
    
    def _setup_metrics(self):
        """Initialize all Prometheus metrics"""
        
        # ==========================================
        # Latency Metrics
        # ==========================================
        self.analysis_latency = Histogram(
            'promptguard_analysis_latency_seconds',
            'API analysis latency',
            ['operation', 'cache_status'],
            buckets=(0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0),
            registry=self.registry
        )
        
        # ==========================================
        # Request Metrics
        # ==========================================
        self.total_requests = Counter(
            'promptguard_requests_total',
            'Total API requests',
            ['endpoint', 'status'],
            registry=self.registry
        )
        
        self.blocked_requests = Counter(
            'promptguard_blocked_requests_total',
            'Total blocked requests',
            ['reason', 'policy'],
            registry=self.registry
        )
        
        self.approved_requests = Counter(
            'promptguard_approved_requests_total',
            'Total approved requests',
            ['policy'],
            registry=self.registry
        )
        
        # ==========================================
        # Cache Metrics
        # ==========================================
        self.cache_hits = Counter(
            'promptguard_cache_hits_total',
            'Cache hits',
            ['cache_level'],
            registry=self.registry
        )
        
        self.cache_misses = Counter(
            'promptguard_cache_misses_total',
            'Cache misses',
            ['cache_level'],
            registry=self.registry
        )
        
        self.cache_hit_ratio = Gauge(
            'promptguard_cache_hit_ratio',
            'Cache hit ratio (0-1)',
            ['cache_level'],
            registry=self.registry
        )
        
        # ==========================================
        # Risk Score Metrics
        # ==========================================
        self.risk_score_distribution = Histogram(
            'promptguard_risk_score',
            'Risk score distribution',
            buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
            registry=self.registry
        )
        
        self.ml_confidence_distribution = Histogram(
            'promptguard_ml_confidence',
            'ML model confidence distribution',
            buckets=(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0),
            registry=self.registry
        )
        
        # ==========================================
        # Model Metrics
        # ==========================================
        self.model_inference_time = Histogram(
            'promptguard_model_inference_seconds',
            'Model inference latency',
            ['model_name'],
            buckets=(0.01, 0.05, 0.1, 0.2, 0.5, 1.0),
            registry=self.registry
        )
        
        self.model_errors = Counter(
            'promptguard_model_errors_total',
            'Model inference errors',
            ['model_name', 'error_type'],
            registry=self.registry
        )
        
        # ==========================================
        # System Metrics
        # ==========================================
        self.in_flight_requests = Gauge(
            'promptguard_in_flight_requests',
            'Current in-flight requests',
            registry=self.registry
        )
        
        self.active_cache_entries = Gauge(
            'promptguard_active_cache_entries',
            'Number of active cache entries',
            ['cache_level'],
            registry=self.registry
        )
        
        self.detector_initialization_time = Gauge(
            'promptguard_detector_init_seconds',
            'Detector initialization time',
            registry=self.registry
        )
        
        # ==========================================
        # Error Metrics
        # ==========================================
        self.validation_errors = Counter(
            'promptguard_validation_errors_total',
            'Input validation errors',
            ['error_type'],
            registry=self.registry
        )
        
        self.api_errors = Counter(
            'promptguard_api_errors_total',
            'API errors',
            ['endpoint', 'status_code'],
            registry=self.registry
        )
    
    # ==========================================
    # Recording Methods
    # ==========================================
    def record_analysis(
        self,
        duration_ms: float,
        risk_score: float,
        cache_hit: bool,
        policy: str,
        blocked: bool = False
    ):
        """Record analysis metrics"""
        
        # Latency
        cache_status = "hit" if cache_hit else "miss"
        self.analysis_latency.labels(
            operation="analyze",
            cache_status=cache_status
        ).observe(duration_ms / 1000.0)
        
        # Risk score
        self.risk_score_distribution.observe(risk_score)
        
        # Request counts
        status = "blocked" if blocked else "approved"
        self.total_requests.labels(
            endpoint="/api/v2/analyze",
            status=status
        ).inc()
        
        if blocked:
            self.blocked_requests.labels(
                reason="high_risk_score",
                policy=policy
            ).inc()
        else:
            self.approved_requests.labels(policy=policy).inc()
        
        # Cache
        if cache_hit:
            self.cache_hits.labels(cache_level="memory").inc()
        else:
            self.cache_misses.labels(cache_level="redis").inc()
    
    def record_model_inference(
        self,
        model_name: str,
        duration_ms: float,
        confidence: float
    ):
        """Record ML model inference metrics"""
        
        self.model_inference_time.labels(
            model_name=model_name
        ).observe(duration_ms / 1000.0)
        
        self.ml_confidence_distribution.observe(confidence)
    
    def record_cache_stats(self, cache_hit_ratio: float, level: str):
        """Record cache statistics"""
        
        self.cache_hit_ratio.labels(cache_level=level).set(cache_hit_ratio)
    
    def record_error(self, error_type: str, endpoint: str = None, status_code: int = None):
        """Record error"""
        
        if endpoint:
            self.api_errors.labels(
                endpoint=endpoint,
                status_code=status_code
            ).inc()
        else:
            self.validation_errors.labels(error_type=error_type).inc()
    
    def set_detector_init_time(self, duration_seconds: float):
        """Set detector initialization time"""
        
        self.detector_initialization_time.set(duration_seconds)
    
    def get_metrics(self) -> dict:
        """Get all metrics as dictionary"""
        
        return {
            "latency": "See /metrics endpoint",
            "requests": "See /metrics endpoint",
            "cache": "See /metrics endpoint",
            "errors": "See /metrics endpoint"
        }
