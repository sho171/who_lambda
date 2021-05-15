FROM amazon/aws-lambda-python:3.8

RUN yum update -y
RUN rpm -ivh http://packages.groonga.org/centos/groonga-release-1.1.0-1.noarch.rpm
RUN sed -i -e 's/$releasever\/$basearch\//7\/$basearch/g' /etc/yum.repos.d/groonga.repo
RUN yum install -y --nogpgcheck mecab mecab-devel mecab-ipadic git make curl xz patch gcc gcc-c++ which find tar file openssl
RUN pip install --upgrade pip
RUN pip install mecab-python3 wheel
RUN pip install neologdn tweepy emoji python-dotenv

WORKDIR /var/task/
COPY main.py /var/task/

# neolog
RUN cp /etc/mecabrc /usr/local/etc/
RUN git clone --depth 1 https://github.com/neologd/mecab-ipadic-neologd.git && \
cd mecab-ipadic-neologd && \
./bin/install-mecab-ipadic-neologd -n -y && \
echo `mecab-config --dicdir`"/mecab-ipadic-neologd" > /var/task/mecab_path

CMD [ "main.handler" ]
