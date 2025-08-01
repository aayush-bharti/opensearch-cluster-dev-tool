# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import api_endpoints

app = FastAPI(title="OpenSearch Cluster Dev Tool API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

# Include routers
app.include_router(api_endpoints.router, prefix="/api/cluster", tags=["cluster"])

if __name__ == "__main__":
    # Get configuration from environment variables with secure defaults
    # default to local host port 8000
    HOST = os.getenv("API_HOST", "127.0.0.1")
    PORT = int(os.getenv("API_PORT", "8000"))
    
    # Log the configuration
    print(f"🚀 Starting OpenSearch Cluster Dev Tool API on {HOST}:{PORT}")
    if HOST == "0.0.0.0":
        print("⚠️  Warning: Server is bound to all interfaces (0.0.0.0)")
    elif HOST == "127.0.0.1":
        print("✅ Server bound to localhost only (secure for development)")
    
    uvicorn.run(app, host=HOST, port=PORT)
