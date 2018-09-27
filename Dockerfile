FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install -y python3 python3-dev python3-pip build-essential
COPY . /app
WORKDIR /app
ENV FLASK_APP f9k9.py
RUN pip3 install -r requirements/prod.txt
EXPOSE 5000
ENTRYPOINT ["python3"]
CMD [ "app.py" ]
