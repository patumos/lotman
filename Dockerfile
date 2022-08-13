FROM python:3.8
RUN pip install --upgrade pip
#RUN apt update
#RUN apt -y install nodejs npm
#RUN npm  i bookcovers
ADD ./app /lotman
WORKDIR /lotman
RUN pip install -r requirements.txt
