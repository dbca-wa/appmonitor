# Prepare the base environment.
ARG IMAGE_TAG
ARG IMAGE_NAME
FROM ghcr.io/dbca-wa/docker-apps-dev:ubuntu2604_base_latest  AS builder_base_appmonitor
ARG IMAGE_TAG
ARG IMAGE_NAME
MAINTAINER asi@dbca.wa.gov.au
RUN echo "Building version: $IMAGE_TAG for $IMAGE_NAME"
ENV CONTAINER_IMAGE_TAG=${IMAGE_TAG}
ENV CONTAINER_IMAGE_NAME=${IMAGE_NAME}
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Australia/Perth
ENV PRODUCTION_EMAIL=True
ENV SECRET_KEY="ThisisNotRealKey"
ENV VIRTUAL_ENV=/app/venv
ENV PATH=$VIRTUAL_ENV/bin:$PATH
SHELL ["/bin/bash", "-c"]
# Key for Build purposes only
ENV FIELD_ENCRYPTION_KEY="Mv12YKHFm4WgTXMqvnoUUMZPpxx1ZnlFkfGzwactcdM="
# Key for Build purposes only
RUN apt-get clean
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install --no-install-recommends -y curl wget python3-pip python3-venv  libreoffice skopeo 
RUN ln -s /usr/bin/python3 /usr/bin/python 

RUN groupadd -g 5000 oim 
RUN useradd -g 5000 -u 5000 oim -s /bin/bash -d /app
RUN mkdir /app 
RUN chown -R oim.oim /app 

# Apply memory limits for the oim user.
# RUN echo "oim             hard    as         1992294" >> /etc/security/limits.conf
RUN echo "ulimit -m 2048000" >> /etc/bash.bashrc
RUN echo "ulimit -v 2048000" >> /etc/bash.bashrc

# Default Scripts
RUN wget https://raw.githubusercontent.com/dbca-wa/wagov_utils/main/wagov_utils/bin/default_script_installer.sh -O /tmp/default_script_installer.sh
RUN chmod 755 /tmp/default_script_installer.sh
RUN /tmp/default_script_installer.sh

RUN apt-get install --no-install-recommends -y python3-pil

ENV TZ=Australia/Perth
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN wget -qO- https://get.anchore.io/syft | sh -s -- -b /usr/local/bin
RUN wget -qO- https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin

COPY startup.sh /
RUN chmod 755 /startup.sh

# Install Python libs from requirements.txt.
FROM builder_base_appmonitor AS python_libs_appmonitor
WORKDIR /app
USER oim 
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH=/app/venv/bin:$PATH

RUN git config --global --add safe.directory /app

# RUN /bin/bash -c "source /app/venv/local/bin/activate"
COPY requirements.txt ./
COPY python-cron ./

RUN $VIRTUAL_ENV/bin/pip3 install --upgrade pip
RUN $VIRTUAL_ENV/bin/pip3 install --no-cache-dir -r requirements.txt 
# Update the Django <1.11 bug in django/contrib/gis/geos/libgeos.py
# Reference: https://stackoverflow.com/questions/18643998/geodjango-geosexception-error
#&& sed -i -e "s/ver = geos_version().decode()/ver = geos_version().decode().split(' ')[0]/" /usr/local/lib/python3.6/dist-packages/django/contrib/gis/geos/libgeos.py \
# RUN rm -rf /var/lib/{apt,dpkg,cache,log}/ /tmp/* /var/tmp/*

# Install the project (ensure that frontend projects have been built prior to this step).
FROM python_libs_appmonitor
COPY timezone /etc/timezone
#RUN wget -O /app/GDAL-3.8.3-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl https://github.com/girder/large_image_wheels/raw/wheelhouse/GDAL-3.8.3-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=e2fe6cfbab02d535bc52c77cdbe1e860304347f16d30a4708dc342a231412c57
#RUN ls -la /tmp/
#RUN /app/venv/bin/pip install /app/GDAL-3.8.3-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl

COPY gunicorn.ini ./

RUN touch /app/.env
COPY .git ./.git
COPY --chown=oim:oim appmonitor appmonitor
COPY --chown=oim:oim manage.py ./
COPY --chown=oim:oim static-config static-config
# RUN chmod 777 /app/appmonitor/cache/
RUN /app/venv/bin/python manage.py collectstatic --noinput

# Cleanup
USER root
RUN wget https://raw.githubusercontent.com/dbca-wa/wagov_utils/refs/heads/main/wagov_utils/bin/package_cleanup_2604.sh -O /tmp/package_cleanup_2604.sh
RUN chmod 755 /tmp/package_cleanup_2604.sh
RUN /tmp/package_cleanup_2604.sh
USER oim

EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["/startup.sh"]

