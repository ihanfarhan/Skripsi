###########################################################################
## Docker Base File For Build Apps
## @author: Irfan Andriansyah <irfan@99.co>
## @since: 2020.03.23
###########################################################################

FROM python:3.7

# Generate Directory
RUN mkdir /usr/thesis
WORKDIR /usr/thesis

# Copy File
COPY ./requirements.txt .
RUN pip install -r requirements.txt
