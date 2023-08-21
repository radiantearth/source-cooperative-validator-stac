FROM python:3.8
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD src/ src/
ENTRYPOINT ["python", "src/entrypoint.py"]