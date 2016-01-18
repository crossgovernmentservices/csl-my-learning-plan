FROM python:3.5-onbuild

RUN apt-get update -qq && apt-get -y install rubygems unzip ruby-dev
RUN gem install sass:3.4.19

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

WORKDIR /usr/src/app
CMD ["gunicorn", "--config=gunicorn.py", "application.run:app"]

