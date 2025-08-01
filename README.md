# OpenSearch Cluster Dev Tool Platform

This project provides a full-stack application for automating OpenSearch build, deployment, and benchmarking processes. Previously, these processes were completely manual and extremely time-consuming with different repositories and libraries needed for each step. This project creates a centralized web application to run these processes where the user only needs to input the configuration for each step and launch the job.

## Features

- OpenSearch build automation with custom manifest files
- OpenSearch cluster deployment using AWS CDK
- Benchmark execution and result management
- AWS resource management (EC2)
- Progress tracking and status monitoring
- S3-based result storage

## Prerequisites

- Python 3.9
- Node.js 14+
- AWS CLI configured with credentials using AWS configure
- Docker (for local development)

## Project Structure

```
.
├── backend/
│   ├── main.py                              # FastAPI application entry point
│   ├── job_tracker.py                       # Job status and progress tracking
│   ├── routers/
│   │   └── api_endpoints.py                 # Main workflow API endpoints
│   ├── scripts/
│   │   ├── build.py                         # OpenSearch build
│   │   ├── deploy.py                        # AWS CDK deployment scripts
│   │   ├── benchmark.py                     # OpenSearch Benchmark execution
│   │   └── s3_upload.py                     # S3 upload utilities
│   ├── job_data/                            # Job execution data storage
│   └── requirements.txt                     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── configurations/
│   │   │   │   ├── BenchmarkConfiguration.js
│   │   │   │   ├── BuildConfiguration.js
│   │   │   │   └── DeployConfiguration.js
│   │   │   ├── BenchmarkResultsTable.js     # Benchmark results display
│   │   │   ├── JobConfiguration.js          # Job setup interface
│   │   │   ├── JobHeader.js                 # Job information header
│   │   │   ├── JobProgress.js               # Progress indicators
│   │   │   ├── JobResults.js                # Results display component
│   │   │   ├── JobStatus.js                 # Status monitoring
│   │   │   ├── JobStatusPolling.js          # Real-time status updates
│   │   │   ├── TaskCard.js                  # Individual task display
│   │   │   └── TaskHistory.js               # Task execution history
│   │   ├── pages/
│   │   │   ├── clusterDevUI.js
│   │   │   └── clusterDevUI.css
│   │   ├── utils/
│   │   │   └── statusUtils.js               # Status utility functions
│   │   ├── App.js                           # Main React application
│   │   ├── App.css                          # Application styles
│   │   ├── index.js                         # React entry point
│   │   └── index.css                        # Global styles
│   └── package.json                         # Node.js dependencies
├── docker-compose.yml                       # Docker container orchestration
├── requirements.txt                         # Python dependencies
└── setup.sh                                 # Project setup script

```

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/aayush-bharti/opensearch-cluster-dev-tool.git
   cd opensearch-cluster-dev-tool
   ```

2. Set up the backend:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install -g yarn
   yarn install
   ```

## Running the Application

1. Start the backend server:
   ```bash
   cd backend
   uvicorn main:app --reload
   OR
   python3.9 main.py
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   yarn start
   ```

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

## Usage

1. **Build**
   - Select Build on the UI
   - Input your manifest YAML file
   - Start the build process

2. **Deployment**
   - Select Deploy on the UI
   - Configure cluster settings
   - Deploy the cluster

3. **Benchmark**
   - Select Benchmark on the UI
   - Configure benchmark parameters
   - Run the benchmark

## API Documentation

The backend API documentation is available at http://localhost:8000/docs when the server is running.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
