FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml package.json package-lock.json ./
COPY wsgi.py ./
COPY bloggr ./bloggr
COPY migrations ./migrations
COPY tailwind.config.js postcss.config.js ./
COPY start.sh ./

RUN pip install --no-cache-dir -e . && \
    npm ci --only=production=false --ignore-scripts && \
    npm run build-css

ENV FLASK_ENV=production
ENV FLASK_APP=wsgi
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

ENV PORT=8080

EXPOSE 8080

RUN chmod +x start.sh

CMD ["./start.sh"]
