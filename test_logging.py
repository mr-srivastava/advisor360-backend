#!/usr/bin/env python3
"""
Test script for logging infrastructure
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app.core.logging.config import setup_logging
    from app.core.logging.structured_logger import get_logger
    from app.core.logging.request_logger import RequestLogger
    from app.core.middleware.metrics_middleware import MetricsCollector
    
    print("✓ All logging modules imported successfully")
    
    # Test logging setup
    setup_logging()
    print("✓ Logging setup completed")
    
    # Test structured logger
    logger = get_logger("test_logger")
    logger.info("Test log message", {"test_data": "value"})
    print("✓ Structured logger working")
    
    # Test request logger
    request_logger = RequestLogger("test_request_logger")
    print("✓ Request logger created")
    
    # Test metrics collector
    metrics = MetricsCollector()
    metrics.record_request("GET", "/test", 200, 150.5)
    summary = metrics.get_summary()
    print(f"✓ Metrics collector working: {summary['total_requests']} requests recorded")
    
    print("\n🎉 All logging infrastructure tests passed!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)