FROM python:3.6-alpine

RUN pip3 install goutte

ENV GOUTTE_CONFIG goutte.yml
ENV GOUTTE_DO_TOKEN ''

WORKDIR /goutte

ENTRYPOINT ["goutte"]

CMD ["$GOUTTE_CONFIG", "$GOUTTE_DO_TOKEN"]
