#!/bin/bash

# Define the fixed image name
BASE_IMAGE_NAME="peninsula/perception"
PACKAGE_JSON_PATH="./package.json" # Adjust the path to your actual package.json file if needed

# Ask the user for the version string
read -p "Enter the version string (e.g., 0.1.1): " VERSION

# Update the version in package.json using jq
if jq --arg v "v$VERSION" '.version = $v' "$PACKAGE_JSON_PATH" > tmp.$$.json && mv tmp.$$.json "$PACKAGE_JSON_PATH"; then
  echo "Updated package.json with version v$VERSION"
else
  echo "Failed to update package.json"
  exit 1
fi

# Form the full image tag with the version
IMAGE_TAG="${BASE_IMAGE_NAME}:v${VERSION}"

# Replace '/' with '' to form the tarball base name
TARBALL_BASE_NAME="${BASE_IMAGE_NAME//\//}"

# Define the path to the Dockerfile
DOCKERFILE_PATH="."

# Build the Docker image with the specified tag
echo "Building Docker image: $IMAGE_TAG"
docker build -t "$IMAGE_TAG" "$DOCKERFILE_PATH" || { echo "Docker build failed"; exit 1; }

# Save the Docker image to a tar file (without compression)
TARBALL_NAME="${TARBALL_BASE_NAME}_docker_v${VERSION}.tar"
echo "Saving Docker image to tar file: $TARBALL_NAME"
docker save "$IMAGE_TAG" > "$TARBALL_NAME" || { echo "Docker save failed"; exit 1; }

# Compress the tar file using xz
echo "Compressing tar file to .tar.xz"
xz -z -v "$TARBALL_NAME" || { echo "Compression failed"; exit 1; }

# The final tarball name
FINAL_TARBALL_NAME="${TARBALL_NAME}.xz"

echo "Docker image saved and compressed as $FINAL_TARBALL_NAME"
