# Face Recognition API

## Setup

```sh
pipenv shell
pipenv install
```

## Running the Application

```sh
uvicorn app.main:app --reload
```

## API Endpoints

### Face Comparison
**POST** `/api/v1/face/compare-faces`
- Compare two images uploaded  using AWS Rekognition's face comparison feature


## Features

✅ Compare two images using  **AWS Rekognition** 's face comparison feature.

## How to Use

1. install dependences and create `.env` using `.env-sample`
2. Access API documentation at: [`http://localhost:8000/docs`](http://localhost:8000/docs)
3. Access Redoc at: [`http://localhost:8000/redoc`](http://localhost:8000/redoc)
3. Use the endpoints to compare faces

---
Built with ❤️ using Python & FastAPI

