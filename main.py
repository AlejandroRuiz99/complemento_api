"""
Punto de entrada principal para la aplicación.
"""

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Configuración para desarrollo local
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )