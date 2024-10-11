build-web:
    cd iris-web && npm install && BUILD_DIR=../dist npm run build

download-deploy-deps:
    rm -f dist/wheels/*
    pip download -r requirements.txt \
        --extra-index-url=https://wpilib.jfrog.io/artifactory/api/pypi/wpilib-python-release-2024/simple/ \
        --platform=manylinux2014_aarch64 \
        --platform=linux_aarch64 \
        --only-binary=:all: \
        --python-version=3.11 \
        -d dist/wheels

lint:
    cd iris-web && npx eslint src/ --fix
    isort .
    black .
    flake8
