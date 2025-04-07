#!/bin/bash
cd /home/site/wwwroot
pip install -r requirements.txt
gunicorn app_simplified:app --bind=0.0.0.0:8000 --workers=4
