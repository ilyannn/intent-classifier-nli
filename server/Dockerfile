# https://luis-sena.medium.com/creating-the-perfect-python-dockerfile-51bdec41f1c8

FROM ubuntu:22.04 AS builder-image

# avoid stuck build due to user prompt
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install --no-install-recommends -y python3.11 python3.11-dev python3.11-venv python3-pip python3-wheel build-essential && \
	apt-get clean && rm -rf /var/lib/apt/lists/*

# create and activate virtual environment
# using final folder name to avoid path issues with packages
RUN python3.11 -m venv /home/myuser/venv
ENV PATH="/home/myuser/venv/bin:$PATH"

# install requirements
WORKDIR /workdir
COPY requirements.txt .
RUN pip3 install --no-cache-dir wheel && pip3 install --no-cache-dir gunicorn -r requirements.txt


FROM ubuntu:22.04 AS runner-image

RUN apt-get update && apt-get install --no-install-recommends -y python3.11 python3-venv && \
	apt-get clean && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home myuser
COPY --from=builder-image /home/myuser/venv /home/myuser/venv

USER myuser
RUN mkdir /home/myuser/code
WORKDIR /home/myuser/code

EXPOSE 5501

# make sure all messages always reach console
ENV PYTHONUNBUFFERED=1

# activate virtual environment
ENV VIRTUAL_ENV=/home/myuser/venv
ENV PATH="/home/myuser/venv/bin:$PATH"

COPY *.py .
COPY models/ models/

ENV MODEL="models/deep.tree.model"

# /dev/shm is mapped to shared memory and should be used for gunicorn heartbeat
# this will improve performance and avoid random freezes
ENTRYPOINT ["gunicorn", "server:create_app()"]
CMD ["-w", "4", "--worker-tmp-dir", "/dev/shm", "-b", "0.0.0.0:5501"]
