FROM python:3

COPY . ./nesk
WORKDIR ./nesk

RUN pip install --upgrade pip &&  \
    pip install -r requirements.txt
    

CMD ["python3", "nesk.py"]
