FROM tiangolo/uwsgi-nginx-flask:python3.8

# If STATIC_INDEX is 1, serve / with /static/index.html directly (or the static URL configured)
ENV STATIC_INDEX 0
# ENV STATIC_INDEX 0

COPY ./app /app

copy requirements.txt requirements.txt
RUN pip install -r requirements.txt