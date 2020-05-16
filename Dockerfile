FROM python:3.7-slim-buster

LABEL maintainer = "Nicholas ST <nichostst@gmail.com>"
LABEL version = "0.1"

WORKDIR /reliability

COPY . /reliability

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "src/main.py"]
