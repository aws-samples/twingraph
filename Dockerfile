FROM --platform=linux/amd64 python:3.10

ARG TWINGRAPH=twingraph
ARG REDIS=redis-stack
ARG GREMLIN=tinkergraph-server

RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y apt-utils vim

RUN apt-get update -y && \
    apt-get -qy full-upgrade && \
    apt-get install -qy curl && \
    curl -sSL https://get.docker.com/ | sh

RUN apt-get update 

RUN apt install sudo

RUN apt-get install -y ca-certificates curl gnupg

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \ 
    ./aws/install

RUN curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-archive-keyring.gpg

RUN echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

RUN apt-get update

RUN apt-get install -y kubectl

ARG PLATFORM=Linux_amd64

RUN curl -sLO "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_${PLATFORM}.tar.gz"

RUN tar -xzf eksctl_${PLATFORM}.tar.gz -C /tmp && rm eksctl_${PLATFORM}.tar.gz

RUN mv /tmp/eksctl /usr/local/bin

RUN useradd -ms /bin/bash twingraph-user

USER twingraph-user

WORKDIR /home/twingraph-user

COPY dist/ /home/twingraph-user/dist/

COPY tests/ /home/twingraph-user/tests/

ENV PATH="${PATH}:/home/twingraph-user/.local/"

RUN pip install --upgrade pip   

RUN pip install /home/twingraph-user/dist/twingraph*.whl

COPY examples/ /home/twingraph-user/examples/

USER root

RUN chown -R twingraph-user:twingraph-user /home/twingraph-user

RUN chown -R twingraph-user:twingraph-user /var/

RUN usermod -aG docker twingraph-user

RUN echo "twingraph-user ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER twingraph-user

RUN cd /home/twingraph-user/examples/orchestration_demos/; grep -rl '@component(' ~/ | xargs sed -i "s/@component(/@component(graph_config={\"graph_endpoint\":\"ws:\/\/${GREMLIN}:8182\"},/g"

RUN cd /home/twingraph-user/examples/orchestration_demos/; grep -rl '@pipeline(' ~/ | xargs sed -i "s/@pipeline(/@pipeline(graph_config={\"graph_endpoint\":\"ws:\/\/${GREMLIN}:8182\"},/g"

RUN cd /home/twingraph-user/examples/orchestration_demos/; grep -rl 'celery_pipeline=True,' ~/ | xargs sed -i "s/celery_pipeline=True,/ celery_pipeline=True, celery_host = \"@${TWINGRAPH}\", celery_backend = \"redis:\/\/${REDIS}:6379\/0\", celery_broker = \"redis:\/\/${REDIS}:6379\/1\",/g"


ENV C_FORCE_ROOT=true

ENV PATH="${PATH}:/home/twingraph-user/.local/bin"


