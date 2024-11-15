package: build-web copy-files download-deploy-deps

copy-files:
    mkdir -p ./dist/Iris
    rsync -arvh --exclude-from="./.gitignore" --filter="merge rsync-filter" ./ dist/Iris/ --delete --delete-excluded

compress:
    tar -cf - ./dist | xz -z -T0 > archive.tar.xz

build-web:
    cd iris-web && npm install && npm run build

download-deploy-deps:
    rm -f dist/wheels/*
    pip download -r requirements_lock.txt \
        --extra-index-url=https://wpilib.jfrog.io/artifactory/api/pypi/wpilib-python-release-2024/simple/ \
        --extra-index-url=https://iris-vision.github.io/pyapriltags/simple/ \
        --platform=manylinux2014_aarch64 \
        --platform=linux_aarch64 \
        --only-binary=:all: \
        --python-version=3.11 \
        -d dist/wheels

install:
    pip install pip-tools --no-index --find-links=./wheels/
    pip install pip-tools
    # First try syncing with the local wheels only
    pip-sync --no-index --find-links=./wheels requirements_lock.txt

    if [ $? -ne 0 ]; then \
        echo "Some packages were missing; retrying with online repositories..."; \
        pip-sync requirements_lock.txt \
            --extra-index-url=https://iris-vision.github.io/pyapriltags/simple/ \
            --find-links=./wheels; \
    else \
        echo "All packages installed successfully from local wheels."; \
    fi

lint:
    isort .
    black .
    # cd iris-web && npx @biomejs/biome format --ignore '**/*.d.ts' -write ./src
    flake8 .

test: build-web
    python3 main.py --video assets/2024speaker.webm

lock-reqs:
    pip-compile requirements.txt --output-file requirements_lock.txt

deploy remote:
    ssh root@{{remote}} "systemctl stop iris"
    rsync -arvh --delete --exclude='venv/' dist/* root@{{remote}}:/app/
    ssh root@{{remote}} "cd /app/ && source venv/bin/activate && pip install pip-tools --no-index --find-links=./wheels/ && pip-sync --no-index --find-links=./wheels iris/requirements_lock.txt"
    ssh root@{{remote}} "systemctl start iris"
