# FROM sets the base image to use. In this case we are using the python 3.6 slim buster image
FROM python:3.6-slim-buster

# WORKDIR sets the working directory inside the image
WORKDIR /app    

#COPY requirements.txt ./ copies the requirements.txt file to the working directory
COPY requirements.txt ./

RUN pip install -r requirements.txt

# COPY . . copies all the files in the current directory to the working directory
COPY . .

# EXPOSE instruction informs the docker to listen to the specified port
EXPOSE 4000 

CMD [ "flask", "run", "--host=0.0.0.0", "--port=4000"]