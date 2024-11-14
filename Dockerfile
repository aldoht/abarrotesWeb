# Usa una imagen base de Python
FROM python:3.12.5
LABEL authors=["rogelio02"]

# Establece el directorio de trabajo
WORKDIR /app/

# Instala las dependencias
RUN pip install flask
RUN pip install flaskmysqldb
RUN pip install mysqlclient
RUN pip install Flask-Login


COPY static static
COPY templates templates
COPY app.py app.py
COPY dbconfig.py dbconfig.py

EXPOSE 8080

CMD ["python", "app.py"]
