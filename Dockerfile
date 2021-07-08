FROM loonfactory/asr_streamlit_base AS asr_streamlit
RUN mkdir /app
COPY ./app /app
WORKDIR /app
EXPOSE 8516
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "asr_streamlit", "flask", "run", "--host", "0.0.0.0", "--port" ,"8516" ]