FROM nvidia/cuda:12.8.0-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
	libgl1 libglib2.0-0 \
	python3 python3-venv python3-pip python3-dev \
	git \
	wget \
	curl \
	vim \
	inetutils-ping \
	sudo \
	net-tools \
	iproute2 \
	gcc \
	make \
	cmake \
	g++ \
	gpp \
	clang \
	libssl-dev \
	pkg-config \
	&& \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*
RUN curl --proto '=https' --tlsv1.3 https://sh.rustup.rs -sSf | bash -s -- -y && sleep 5
RUN pip3 install transformers 
ENV PATH="/root/.cargo/bin:${PATH}"

COPY webui.sh webui.sh
COPY requirements.txt requirements.txt

# setup venv in /venv to avoid conflict with volume in /stable-diffusion-webui
RUN echo 'venv_dir=/venv' > webui-user.sh

ENV install_dir=/
RUN python3 -m venv venv 
RUN . venv/bin/activate && python3 -m pip install --upgrade pip setuptools && \
	python3 -m pip install -r requirements.txt
RUN ./webui.sh -f can_run_as_root --exit --skip-torch-cuda-test --api
#RUN deactivate
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
#RUN python3 -m pip install -r requirements.txt

WORKDIR "/stable-diffusion-webui/"
VOLUME /root/.cache

#CMD [".", "venv/bin/activate", "&&", "python3", "launch.py", "--listen", "--api"]
CMD [".", "venv/bin/activate", "&&", "bash", "webui.sh", "-f", "can_run_as_root", "--listen", "--api"]
