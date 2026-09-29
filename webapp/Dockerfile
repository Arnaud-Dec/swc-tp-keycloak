FROM python:3.9

WORKDIR /webapp
COPY . .
RUN pip install flask python-keycloak pyjwt[crypto]

CMD ["python", "app.py"]
