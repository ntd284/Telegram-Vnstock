FROM ubuntu:latest
WORKDIR /usr/app/src/telestockbot/

COPY . /usr/app/src/telestockbot/

RUN mkdir -p /usr/app/src/telestockbot/src
RUN mkdir -p /usr/app/src/telestockbot/file
RUN mkdir -p /usr/app/src/telestockbot/dist
RUN mkdir -p /usr/app/src/telestockbot/dist/dist_data
RUN mkdir -p /usr/app/src/telestockbot/src/plugin
RUN mkdir -p /usr/app/src/telestockbot/src/plugin/key

COPY dist/dist_data/ssi_fc_data-2.2.1.tar.gz /usr/app/src/telestockbot/dist/dist_data

COPY file/list_stock.txt /usr/app/src/telestockbot/file
COPY file/list_stock_sp.txt /usr/app/src/telestockbot/file
COPY file/list_acc_trading.txt /usr/app/src/telestockbot/file
COPY run.sh  /usr/app/src/telestockbot/

COPY cronfile /usr/app/src/telestockbot/crontab
RUN chmod 0644 /usr/app/src/telestockbot/crontab


COPY src/main.py /usr/app/src/telestockbot/src
COPY src/streaming_stock.py /usr/app/src/telestockbot/src


COPY src/plugin/ssi_data.py /usr/app/src/telestockbot/src/plugin
COPY src/plugin/ssi_trading.py /usr/app/src/telestockbot/src/plugin

COPY src/plugin/key/config_data.py /usr/app/src/telestockbot/src/plugin/key
COPY src/plugin/key/config_trading.py /usr/app/src/telestockbot/src/plugin/key
COPY src/plugin/key/key.py /usr/app/src/telestockbot/src/plugin/key
COPY src/plugin/key/tradingD.py /usr/app/src/telestockbot/src/plugin/key

COPY requirements.txt /usr/app/src/telestockbot

RUN apt-get update && apt-get -y install python3-pip
RUN apt-get -y install vim
RUN apt-get -y install cron
# Install timezone data without interactive prompts
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata
RUN ln -fs /usr/share/zoneinfo/Asia/Ho_Chi_Minh /etc/localtime

RUN pip install -r /usr/app/src/telestockbot/requirements.txt
RUN pip install /usr/app/src/telestockbot/dist/dist_data/ssi_fc_data-2.2.1.tar.gz

COPY run.sh /usr/app/src/telestockbot/run.sh
RUN chmod +x /usr/app/src/telestockbot/run.sh
RUN crontab /usr/app/src/telestockbot/crontab

CMD ["sh", "-c", "./run.sh "]