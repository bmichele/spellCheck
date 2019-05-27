FROM python:3.7
#ADD . /code
#WORKDIR /code
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN apt-get install -y bash
#CMD python app.py