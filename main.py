#!/usr/bin/env python3
"""
PromptGuard v2.0 - Enterprise AI Security Gateway
Main entry point for running the server
"""

import sys
import logging
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run the FastAPI server"""
    
    from promptguard.config.settings import settings
    
    logger.info("=" * 60)
    logger.info(f"Starting {settings.APP_NAME}")
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Server: {settings.HOST}:{settings.PORT}")
    logger.info("=" * 60)
    
    try:
        uvicorn.run(
            "promptguard.api.main:app",
            host=settings.HOST,
            port=settings.PORT,
            workers=settings.WORKERS if not settings.RELOAD else 1,
            reload=settings.RELOAD,
            log_level=settings.LOG_LEVEL.lower(),
            access_log=True,
        )
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
