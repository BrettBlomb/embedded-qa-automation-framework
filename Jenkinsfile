pipeline {
    agent any

    environment {
        COAP_HOST = "mock-coap"
        PYTHONUNBUFFERED = "1"
        CI = "true"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Create Network') {
            steps {
                sh '''
                    echo "Creating Docker network if not exists..."
                    docker network inspect coapnet >/dev/null 2>&1 || docker network create coapnet
                '''
            }
        }

        stage('Start Mock Services') {
            steps {
                sh '''
                    echo "Cleaning old containers..."
                    docker rm -f mock-coap mock-rest selenium-standalone || true

                    echo "Starting CoAP mock server..."
                    docker run -d --name mock-coap --network coapnet \
                        -p 5683:5683/udp \
                        -v "$WORKSPACE/mock_servers:/app" \
                        python:3.10 bash -c "pip install aiocoap && python /app/mock_coap_server.py"

                    echo "Starting REST mock server..."
                    docker run -d --name mock-rest --network coapnet \
                        -p 8000:8000 \
                        -v "$WORKSPACE/mock_servers:/app" \
                        python:3.10 bash -c "pip install flask && python /app/mock_rest_server.py"

                    echo "Starting Selenium..."
                    docker run -d --name selenium-standalone --network coapnet \
                        -p 4444:4444 --shm-size=2g selenium/standalone-chrome:latest
                '''
            }
        }

        stage('Debug Workspace') {
            steps {
                sh '''
                    echo "=== CURRENT WORKSPACE ==="
                    pwd
                    echo "=== CONTENTS ==="
                    ls -al
                '''
            }
        }

        stage('Run Tests Inside Docker') {
            steps {
                sh '''
                    echo "Running tests in isolated container on coapnet..."

                    docker run --rm --network coapnet \
                        -e COAP_HOST=mock-coap \
                        -e CI=true \
                        -e PYTHONUNBUFFERED=1 \
                        -v "$WORKSPACE:/workspace" \
                        -w /workspace \
                        python:3.10 bash -c "
                            echo 'Checking mapped workspace:' &&
                            ls -al /workspace &&
                            pip install --upgrade pip &&
                            pip install -r requirements.txt &&
                            mkdir -p reports &&
                            pytest --junitxml=reports/junit.xml --html=reports/report.html --self-contained-html -v
                        "
                '''
            }
        }

    }

    post {
        always {
            echo "Cleaning up containers..."
            sh '''
                docker rm -f mock-coap mock-rest selenium-standalone || true
            '''
            junit 'reports/junit.xml'
            archiveArtifacts artifacts: 'reports/**/*'
            publishHTML([
                reportDir: 'reports',
                reportFiles: 'report.html',
                reportName: 'Test Report'
            ])
        }
    }
}
