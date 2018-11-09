FROM quay.io/skygeario/py-skygear:v1.6.1

ENV TINI_VERSION v0.16.1
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

RUN pip install --upgrade pip

COPY requirements.txt /usr/src/app
RUN pip install --upgrade --force-reinstall -r requirements.txt

COPY requirements-dev.txt /usr/src/app
RUN pip install --upgrade --force-reinstall -r requirements-dev.txt

COPY __init__.py /usr/src/app/__init__.py
COPY helloworld /usr/src/app/helloworld
COPY alembic.ini /usr/src/app/alembic.ini
COPY alembic/ /usr/src/app/alembic

CMD ["py-skygear", "--http", "__init__.py"]
