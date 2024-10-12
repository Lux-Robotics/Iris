package: build-web copy-files download-deploy-deps

copy-files:
    rsync -arvh --exclude-from="./.gitignore" --filter="merge rsync-filter" ./ dist/ --delete --delete-excluded

build-web:
    cd iris-web && npm install && npm run build

download-deploy-deps:
    rm -f dist/wheels/*
    pip download -r requirements.txt \
        --extra-index-url=https://wpilib.jfrog.io/artifactory/api/pypi/wpilib-python-release-2024/simple/ \
        --extra-index-url=https://iris-vision.github.io/pyapriltags/simple/ \
        --platform=manylinux2014_aarch64 \
        --platform=linux_aarch64 \
        --only-binary=:all: \
        --python-version=3.11 \
        -d dist/wheels

install-libraries:
    pip install -r requirements.txt --extra-index-url=https://iris-vision.github.io/pyapriltags/simple/

lint:
    cd iris-web && npx @biomejs/biome format --write ./src
    isort .
    black .
    flake8 .

test:
    python3 main.py --video assets/2024speaker.webm
