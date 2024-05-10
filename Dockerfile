FROM python

COPY app /file/

# Set the working directory
WORKDIR /file

RUN pip install -r requirements.txt

CMD python main.py && python app.py