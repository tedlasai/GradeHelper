FROM python:3.9

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt && \
    apt-get update && \
    apt-get install -y libqt5gui5 && \
    rm -rf /var/lib/apt/lists/*


COPY . .

CMD ["python", "./gradehelper.py"]