FROM python:3.6.7
RUN apt-get install -y bash
ADD requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
WORKDIR /code
# ENV CHECK_METHOD=${METHOD}
ENTRYPOINT ["python"]
CMD ["app.py"]