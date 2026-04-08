#!/bin/bash
# HuggingFace Spaces startup script

# Init DB if needed
python scripts/init_db.py
python scripts/seed_db.py

# Start FastAPI in background
python -m uvicorn api.app:app --host 0.0.0.0 --port 8000 --log-level warning &

# Wait for API
sleep 3

# Start Streamlit on HF port
exec streamlit run hf_streamlit_app.py \
    --server.port=7860 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
