FROM python:3.8.6
ENV PYTHONUNBUFFERED=1

ENV APP_HOME=/code
RUN mkdir -p $APP_HOME
RUN mkdir $APP_HOME/staticfiles
RUN mkdir $APP_HOME/mediafiles
RUN mkdir $APP_HOME/logs

WORKDIR $APP_HOME

COPY . $APP_HOME

RUN pip install -r requirements.txt

ENV IN_CONTAINER 1

ENTRYPOINT ["/code/entrypoint.sh"]
