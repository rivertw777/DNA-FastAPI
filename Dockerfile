# 빌드 스테이지
FROM python:3.10-slim AS builder

WORKDIR /app

# 필요한 빌드 도구 설치 및 pip 업그레이드
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    pip install --upgrade pip

COPY requirements.txt .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 최종 스테이지
FROM python:3.10-slim

WORKDIR /app

# 빌더 스테이지에서 설치된 Python 패키지 복사
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

# downloads 디렉토리 생성 및 권한 설정
RUN mkdir -p /app/downloads && chmod 777 /app/downloads

# 환경 변수 설정
ENV DOWNLOAD_FOLDER=/app/downloads

# 비 root 유저 생성 및 전환
RUN useradd -m appuser
USER appuser

# CMD 수정
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]