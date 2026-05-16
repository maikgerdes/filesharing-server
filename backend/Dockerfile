FROM python:3
WORKDIR /workspaces
COPY backend/requirements.txt ./backend/
RUN apt-get update && pip install -r backend/requirements.txt
COPY . .
WORKDIR /workspaces/backend
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]