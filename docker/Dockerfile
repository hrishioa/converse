FROM ubuntu
MAINTAINER Hrishi Olickel (hrishioa@gmail.com)

RUN apt-get update && apt-get upgrade \
    && apt-get install -yq --no-install-recommends \
        python2.7 \
        python-pip \
        python-dev \
        python-setuptools \
        wget \
        # bzip2 \
        # ca-certificates \
        sudo \
        # locales \
        # fonts-liberation \
        build-essential \
        # emacs \
        git \
        # inkscape \
        # jed \
        # libsm6 \
        # libxext-dev \
        # libxrender1 \
        # lmodern \
        # netcat \
        # pandoc \
        python-dev \
        # texlive-fonts-extra \
        # texlive-fonts-recommended \
        # texlive-generic-recommended \
        # texlive-latex-base \
        # texlive-latex-extra \
        # texlive-xetex \
        unzip \
        nano \
     && apt-get clean \
     && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install jupyter
RUN pip install converse
RUN python -m textblob.download_corpora lite

RUN mkdir /converse_playground
WORKDIR /converse_playground/
COPY messages/ /converse_playground

EXPOSE 9999
CMD ["jupyter", "notebook", "--allow-root", "--ip", "0.0.0.0", \
    "--NotebookApp.iopub_data_rate_limit=100000000", "--NotebookApp.port=9999",\
    "--NotebookApp.open_browser=False", "Demo.ipynb"]
