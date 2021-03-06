FROM ghcr.io/luksireiku/polaris-base as builder

RUN mkdir -p /usr/src/app

WORKDIR /usr/src/app

COPY requirements.txt .

RUN apk add git python3 python3-dev py3-pip make gcc g++

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "-B", "./loader.py" ]
