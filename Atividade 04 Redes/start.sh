#!/bin/sh

# Iniciar o Flask (backend)
python backend/back.py &

# Iniciar o Streamlit (frontend)
streamlit run frontend/front.py --server.port=8501 --server.address=0.0.0.0
