FROM python:3.11.3
WORKDIR /root

# Pip requirements.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Main source code.
COPY main.py .

CMD python main.py
