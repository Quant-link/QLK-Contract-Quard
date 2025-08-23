# ContractQuard

**AI-Augmented Smart Contract Security Analysis Platform**

ContractQuard is a comprehensive security analysis tool designed to identify vulnerabilities in smart contracts across multiple blockchain languages. Built with modern web technologies and powered by advanced static analysis engines, it provides developers with real-time security insights and detailed vulnerability reports.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Supported Languages](#supported-languages)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Features

### Core Functionality
- **Multi-Language Support**: Analyze Solidity, Rust, and Go smart contracts
- **Real-Time Analysis**: WebSocket-powered live progress tracking
- **Comprehensive Reporting**: Detailed vulnerability reports with severity classification
- **Interactive UI**: Modern React-based interface with dark/light theme support
- **Analysis History**: Persistent tracking of previous security assessments

### Security Detection
- Reentrancy vulnerabilities
- Integer overflow/underflow
- Access control issues
- Timestamp dependence
- Gas limit problems
- Unchecked external calls
- Logic errors and code quality issues

### Technical Features
- RESTful API with FastAPI backend
- WebSocket real-time communication
- Docker containerization
- TypeScript type safety
- Responsive design
- State management with persistence
- Comprehensive error handling

## Architecture

```
ContractQuard/
├── src/                          # Core analysis engine
│   ├── contractquard/
│   │   ├── core/                 # Analysis core
│   │   ├── detectors/            # Vulnerability detectors
│   │   └── parsers/              # Language parsers
├── web/
│   ├── backend/                  # FastAPI backend
│   │   ├── main.py              # API endpoints
│   │   ├── models.py            # Pydantic models
│   │   └── Dockerfile           # Backend container
│   └── frontend/                 # React frontend
│       ├── src/
│       │   ├── components/      # UI components
│       │   ├── pages/           # Application pages
│       │   ├── services/        # API services
│       │   ├── hooks/           # Custom React hooks
│       │   └── store/           # State management
│       └── Dockerfile           # Frontend container
├── rust_parser_helper/           # Rust analysis helper
├── go_parser_helper/             # Go analysis helper
└── docker-compose.yml           # Multi-service orchestration
```

## Supported Languages

| Language | Extension | Framework Support | Status |
|----------|-----------|-------------------|---------|
| Solidity | `.sol` | Ethereum, Polygon, BSC | Full Support |
| Rust | `.rs` | Substrate, ink! | Full Support |
| Go | `.go` | Cosmos SDK | Full Support |

## Installation

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for development)
- Python 3.11+ (for development)
- Rust 1.70+ (for Rust parser)
- Go 1.19+ (for Go parser)

### Quick Start with Docker

```bash
# Clone the repository
git clone https://github.com/quant-link/QLK-ContractQuard.git
cd QLK-ContractQuard

# Start all services
docker-compose up -d

# Access the application
open http://localhost:3000
```

### Development Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd web/frontend
npm install

# Install Rust dependencies
cd ../../rust_parser_helper
cargo build

# Install Go dependencies
cd ../go_parser_helper
go mod tidy
```

## Usage

### Web Interface

1. **Upload Contract**: Drag and drop or select smart contract files
2. **Configure Analysis**: Set analysis parameters (optional)
3. **Run Analysis**: Execute security analysis with real-time progress
4. **Review Results**: Examine detailed vulnerability reports
5. **Export Reports**: Download results in JSON format

### API Usage

```bash
# Health check
curl http://localhost:8000/api/health

# Analyze contract
curl -X POST \
  -F "file=@contract.sol" \
  http://localhost:8000/api/analyze

# Get analysis results
curl http://localhost:8000/api/analysis/{analysis_id}
```

### WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'analysis_complete') {
    console.log('Analysis completed:', data.analysis_id);
  }
};
```

## API Documentation

### Endpoints

#### `GET /api/health`
Returns system health status and version information.

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### `POST /api/analyze`
Analyzes uploaded smart contract file.

**Parameters:**
- `file`: Smart contract file (.sol, .rs, .go)

**Response:**
```json
{
  "analysis_id": "uuid",
  "status": "completed",
  "findings": [...],
  "metadata": {
    "filename": "contract.sol",
    "total_findings": 5,
    "critical_count": 1,
    "high_count": 2
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### `GET /api/analysis/{analysis_id}`
Retrieves analysis results by ID.

#### `WebSocket /ws`
Real-time analysis progress and completion notifications.

### Error Handling

All API endpoints return standardized error responses:

```json
{
  "detail": "Error description",
  "error_code": "ANALYSIS_FAILED",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Development

### Backend Development

```bash
# Start development server
cd web/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/

# Type checking
mypy .
```

### Frontend Development

```bash
# Start development server
cd web/frontend
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Build for production
npm run build
```

### Core Engine Development

```bash
# Run analysis engine tests
python -m pytest tests/

# Test specific detector
python -m contractquard.detectors.reentrancy test_contract.sol

# Add new detector
# 1. Create detector class in src/contractquard/detectors/
# 2. Implement detect() method
# 3. Add to detector registry
# 4. Write comprehensive tests
```

## Testing

### Running Tests

```bash
# All tests
make test

# Backend tests only
make test-backend

# Frontend tests only
make test-frontend

# Integration tests
make test-integration
```

### Test Coverage

```bash
# Generate coverage report
make coverage

# View coverage in browser
open htmlcov/index.html
```

## Deployment

### Production Deployment

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy with production configuration
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

### Environment Configuration

Create `.env` file with production settings:

```env
# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
LOG_LEVEL=INFO

# Frontend Configuration
VITE_API_BASE_URL=https://api.contractquard.com
VITE_WS_URL=wss://api.contractquard.com/ws

# Security
CORS_ORIGINS=https://contractquard.com
MAX_FILE_SIZE_MB=10
RATE_LIMIT_PER_MINUTE=60
```

### Monitoring

```bash
# View logs
docker-compose logs -f

# Monitor resource usage
docker stats

# Health checks
curl http://localhost:8000/api/health
```

## Contributing

### Development Workflow

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-detector`
3. Make changes with comprehensive tests
4. Ensure all tests pass: `make test`
5. Submit pull request with detailed description

### Code Standards

- **Python**: Follow PEP 8, use type hints, 90% test coverage
- **TypeScript**: Strict mode enabled, ESLint compliance
- **Rust**: Follow Rust style guidelines, comprehensive error handling
- **Go**: Follow Go conventions, proper error handling

### Adding New Detectors

```python
# Example detector implementation
from contractquard.core.detector import Detector
from contractquard.core.findings import Finding, Severity

class NewVulnerabilityDetector(Detector):
    def __init__(self):
        super().__init__(
            name="new-vulnerability",
            description="Detects new vulnerability pattern"
        )

    def detect(self, contract_ast) -> List[Finding]:
        findings = []
        # Implementation logic
        return findings
```

### Security Considerations

- All file uploads are validated and sandboxed
- Analysis runs in isolated containers
- No persistent storage of uploaded contracts
- Rate limiting on API endpoints
- Input sanitization throughout the pipeline

## Performance

### Benchmarks

| Contract Size | Language | Analysis Time | Memory Usage |
|---------------|----------|---------------|--------------|
| < 1KB | Solidity | ~2s | ~50MB |
| 1-10KB | Solidity | ~5s | ~100MB |
| 10-100KB | Solidity | ~15s | ~200MB |
| < 1KB | Rust | ~3s | ~75MB |
| < 1KB | Go | ~2s | ~60MB |

### Optimization

- Parallel analysis for multiple files
- Incremental analysis for large contracts
- Caching of analysis results
- Optimized AST parsing
- Memory-efficient data structures

## Troubleshooting

### Common Issues

**Build Failures**
```bash
# Clear Docker cache
docker system prune -a

# Rebuild from scratch
docker-compose build --no-cache
```

**Frontend Issues**
```bash
# Clear node modules
rm -rf web/frontend/node_modules
cd web/frontend && npm install
```

**Backend Issues**
```bash
# Check Python dependencies
pip install -r requirements.txt --upgrade

# Verify environment
python --version  # Should be 3.11+
```

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
docker-compose up

# Frontend debug mode
cd web/frontend
npm run dev -- --debug
```

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## Acknowledgments

- **QuantLink Team**: Core development and architecture
- **Security Research Community**: Vulnerability detection patterns
- **Open Source Contributors**: Various libraries and tools used

---

**Developed by QuantLink** | [Website](https://quantlink.com) | [Documentation](https://docs.contractquard.com) | [Support](mailto:support@quantlink.com)