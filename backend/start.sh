# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

#!/bin/bash

# Set environment variables for AWS SDK
export AWS_SDK_LOAD_CONFIG=1
export PYTHONUNBUFFERED=1

# Clear any existing AWS credential cache
rm -rf ~/.aws/cli/cache/* 2>/dev/null || true

# Start the application with detailed logging
echo "Starting FastAPI application with detailed logging..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --log-level debug --access-log --reload
