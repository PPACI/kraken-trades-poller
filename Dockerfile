FROM python:slim

WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY ./ /app/


ENTRYPOINT ["python", "main.py"]