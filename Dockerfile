FROM python:3.7.3-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apk add --no-cache gcc build-base linux-headers ca-certificates python3 python3-dev libffi-dev libressl-dev && \
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./start.py" ]