#!/bin/bash

set -e

PACKAGE_DIR="package"
ZIP_FILE="lambda_function.zip"

# Clean up previous builds
echo "Cleaning up previous builds..."
rm -rf $PACKAGE_DIR
rm -f $ZIP_FILE

# Create package directory
echo "Creating package directory..."
mkdir -p $PACKAGE_DIR

# Install dependencies into the package directory
echo "Installing dependencies..."
pip install -r requirements.txt --target $PACKAGE_DIR

# Copy application code to the package directory
echo "Copying application code..."
cp *.py $PACKAGE_DIR/

# Create the deployment package zip file
echo "Creating deployment package..."
cd $PACKAGE_DIR
zip -r ../$ZIP_FILE .
cd ..

echo "Deployment package $ZIP_FILE created successfully."
