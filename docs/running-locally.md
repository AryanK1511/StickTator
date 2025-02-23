# Run the App Locally

## Clone the Repository

```bash
git clone git@github.com:AryanK1511/StickTator.git
cd StickTator
```

## Frontend Setup

The frontend is built with Next.js. Follow these steps to set it up:

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

3. Create a `.env.local` file in the frontend directory with the following configuration:

```env
GOOGLE_CLIENT_ID="your_google_client_id"
GOOGLE_CLIENT_SECRET="your_google_client_secret"
NEXTAUTH_URL='http://localhost:3000/'
NEXTAUTH_SECRET='your_nextauth_secret'
NEXT_PUBLIC_BACKEND_URL='127.0.0.1:8000'
```

4. Start the development server:

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## Backend Setup

The backend is powered by FastAPI. Follow these steps to set it up:

1. Navigate to the backend directory:

```bash
cd backend
```

2. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip3 install -r requirements.txt
```

4. Create a `.env` file in the backend directory with the following configuration:

```env
LOG_LEVEL="DEBUG"
MONGO_URI="your_mongodb_connection_string"
AWS_ACCESS_KEY_ID="your_aws_access_key"
AWS_SECRET_ACCESS_KEY="your_aws_secret_key"
AWS_DEFAULT_REGION="your_aws_region"
S3_BUCKET_NAME="your_s3_bucket_name"
OPENAI_API_KEY="your_openai_api_key"
```

5. Start the backend server:

```bash
fastapi dev app/main.py
```

The backend API will be available at `http://localhost:8000`.

## USB Client

The USB client component can be run directly from a USB drive. Simply copy the client files to your USB drive and insert it into the target computer.

## Author

[Aryan Khurana](https://github.com/AryanK1511)
