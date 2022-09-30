# Please build as
# eval $(cat .env) DOCKER_BUILDKIT=1 docker build --build-arg GIT_ACCESS_TOKEN .
# where `( umask 0077; echo "GIT_ACCESS_TOKEN=******" > .env; )`
# this way you don't even leave the GIT_ACCESS_TOKEN variable in the environment
FROM debian-python-git-janeway
COPY ./test_settings.py .
ARG GIT_ACCESS_TOKEN
ENV GIT_ACCESS_TOKEN ${GIT_ACCESS_TOKEN}
# TODO: where do PACKAGE_NAME and PIP_INDEX_URL come from?
ENV PACKAGE_NAME 'wjs.jcom_profile'
ENV PACKAGE_REPO_NAME 'wjs-profile-project'
ENV PIP_INDEX_URL "https://gitlab.sissamedialab.it/api/v4/projects/60/packages/pypi/simple"
# Adding a git repo does not seem to work (I the the web page...)
# ADD https://git:${GIT_ACCESS_TOKEN}@gitlab.sissamedialab.it/wjs/janeway.git ./janeway
# from https://docs.docker.com/engine/reference/builder/#adding-a-git-repository-add-git-ref-dir
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip  \
    git clone --depth 1 https://git:${GIT_ACCESS_TOKEN}@gitlab.sissamedialab.it/wjs/janeway.git && \
    sed -i 's/jsmin.*/jsmin/' janeway/requirements.txt && \
    sed -i '/mysqlclient/d' janeway/requirements.txt && \
    pip install -r janeway/requirements.txt && \
    mv test_settings.py janeway/src/core && \
    git clone --depth 1 https://git:${GIT_ACCESS_TOKEN}@gitlab.sissamedialab.it/wjs/${PACKAGE_REPO_NAME}.git && \
    pip install ./${PACKAGE_REPO_NAME} && \
    pip install pytest && \
    cd $PACKAGE_REPO_NAME && \
    echo "FIXME!"
    # JANEWAY_SETTINGS_MODULE=core.test_settings python3 ./manage.py install_janeway
ENTRYPOINT ["/bin/bash"]
