# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import api_endpoints

app = FastAPI(title="OpenSearch Automation API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_endpoints.router, prefix="/api/cluster", tags=["cluster"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
