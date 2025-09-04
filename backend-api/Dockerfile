FROM python:3.12
RUN pip install fastapi "uvicorn[standard]" pymongo bcrypt pytest pyjwt yt_dlp ffmpeg-python
RUN apt-get update && apt install ffmpeg -y
# CMD [ "tail", "-f", "/dev/null" ]
# CMD ["usr/local/bin/uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] this will continously watch if there are changes in the code and reload the server
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]