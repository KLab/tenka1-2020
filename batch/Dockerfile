FROM python:3.6-alpine
RUN apk update && apk add g++ redis
RUN pip3 install redis

WORKDIR /app
COPY . .
RUN g++ -O2 -std=c++14 calc_score.cpp -o /app/calc_score

CMD [ "sh", "run.sh" ]
