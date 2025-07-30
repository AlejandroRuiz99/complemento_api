"""
Configuración de logging estructurado para la API.
"""

import logging
import logging.config
import json
from datetime import datetime
import os

class JSONFormatter(logging.Formatter):
    """Formateador JSON para logs estructurados."""
    
    def format(self, record):
        """Formatear el registro de log como JSON."""
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Añadir información adicional si existe
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
            
        if hasattr(record, 'duration'):
            log_entry['duration_ms'] = record.duration
        
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logging():
    """Configurar el sistema de logging."""
    
    # Determinar el nivel de log desde variable de entorno
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': JSONFormatter,
            },
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'level': log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'json' if os.getenv('JSON_LOGS', 'true').lower() == 'true' else 'standard',
                'stream': 'ext://sys.stdout'
            }
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console'],
                'level': log_level,
                'propagate': False
            },
            'app': {
                'handlers': ['console'],
                'level': log_level,
                'propagate': False
            },
            'uvicorn': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False
            },
            'uvicorn.error': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False
            },
            'uvicorn.access': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': False
            }
        }
    }
    
    logging.config.dictConfig(logging_config)
    
    # Log inicial
    logger = logging.getLogger('app')
    logger.info(f"Sistema de logging configurado con nivel {log_level}")

def get_logger(name: str) -> logging.Logger:
    """
    Obtener un logger configurado.
    
    Args:
        name: Nombre del logger
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(f'app.{name}')