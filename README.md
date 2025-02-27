<<<<<<< HEAD
# ASO Tool - App Store Optimization

A comprehensive tool for analyzing and optimizing Google Play Store apps.

## Features

- App metadata analysis and optimization
- Competitor analysis and comparison
- Keyword research and tracking
- Review sentiment analysis
- Performance metrics tracking
- Historical data analysis

## Quick Start

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/aso-tool.git
cd aso-tool
```

2. Start the application:
```bash
docker-compose up -d
```

3. Access the application at http://localhost:8000

### Manual Setup

1. Install dependencies:
```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

2. Build frontend:
```bash
cd frontend
npm run build
```

3. Start the server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Usage

1. Enter your app's Google Play Store URL
2. Add competitor URLs for comparison
3. Click "Analyze" to get insights

### Analysis Features

- **Overview**: Key metrics and performance comparison
- **Keywords**: Keyword difficulty and optimization suggestions
- **Reviews**: Sentiment analysis and user feedback insights
- **Metadata**: Title and description optimization
- **Performance**: Install trends and market position

## Development

### Running Tests

```bash
# Backend tests
python -m pytest tests/

# Frontend tests
cd frontend
npm test
```

### API Documentation

Access the API documentation at http://localhost:8000/docs

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
=======
# aso-tool
App Store Optimization Tool for Google Play Store
>>>>>>> f15a6427e9d842a0d63a610c38cd28369697cc03
