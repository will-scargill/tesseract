FROM python:3.9

WORKDIR /tesseract
COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["main.py"]