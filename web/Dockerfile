FROM python:3.6

RUN mkdir /usr/src/app/

COPY . /usr/src/app/

WORKDIR /usr/src/app/

RUN pip install psycopg2-binary 

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "manage.py", "runserver", "--host", "0.0.0.0"]

EXPOSE 5000
