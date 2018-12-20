FROM python:3.6-alpine

RUN pip3 install goutte

ENV GOUTTE_CONFIG goutte.toml
ENV GOUTTE_DO_TOKEN ''

WORKDIR /goutte

ENTRYPOINT ["goutte"]
