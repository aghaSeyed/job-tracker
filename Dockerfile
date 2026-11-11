FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 HOST=0.0.0.0 PORT=8765 DATA_DIR=/data
WORKDIR /app
COPY crawl.py server.py companies.json ./
COPY static ./static
RUN useradd -r -u 10001 app && mkdir /data && chown app /data
USER app
VOLUME /data
EXPOSE 8765
HEALTHCHECK CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8765/api/data')" || exit 1
CMD ["python", "server.py"]
