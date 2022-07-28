FROM python:3.8

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
COPY .. /code/
WORKDIR /code/web
RUN pip install -r requirements.txt && echo "source activate my_env" > ~/.bashrc


ENV PYTHONUNBUFFERED=1
ENV PATH /opt/conda/envs/my_env/bin:$PATH

