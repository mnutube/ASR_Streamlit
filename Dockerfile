FROM ubuntu as dev_tools
RUN apt update 
RUN apt install -y wget
RUN wget https://repo.anaconda.com/archive/Anaconda3-2021.05-Linux-x86_64.sh
RUN chmod +x *.sh

FROM continuumio/miniconda3 AS asr_streamlit_dependency
RUN apt update
RUN DEBIAN_FRONTEND="noninteractive" apt install -y build-essential cmake sox libsndfile1-dev ffmpeg flac libfreetype6-dev

FROM asr_streamlit_dependency AS asr_streamlit_base
COPY .conda.env.yml .
RUN conda env create -f .conda.env.yml
RUN conda init bash \
  && . ~/.bashrc \
  && conda activate asr_streamlit \
  && pip install streamlit==0.82.0 pandas==1.2.4 pydub matplotlib librosa espnet flask
RUN rm .conda.env.yml

FROM asr_streamlit_base AS asr_streamlit
RUN mkdir /app
COPY ./app /app
WORKDIR /app
EXPOSE 8516
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "asr_streamlit", "flask", "run", "--host", "0.0.0.0", "--port" ,"8516" ]