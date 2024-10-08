FROM dockerhub.datagrand.com/idps/online_ocr:v5

COPY start.py .
COPY templates/ ./templates
COPY static/ ./static
COPY data/ ./data
EXPOSE 5001

ENTRYPOINT ["python3", "start.py"]