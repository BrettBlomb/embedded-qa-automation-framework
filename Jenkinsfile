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
                    docker rm -f mock-coap mock-rest selenium-standalone test-runner || true

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

                sh '''
                    echo "Waiting for CoAP server to be ready..."
                    sleep 5
                    echo "CoAP server should be ready"
                '''

                sh '''
                    echo "Waiting for Selenium WebDriver..."
                    for i in {1..20}; do
                        if curl -s http://127.0.0.1:4444/wd/hub/status | grep -q '"ready":true'; then
                            echo "Selenium is ready!"
                            break
                        fi
                        echo "Still waiting..."
                        sleep 2
                    done
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

        stage('Run Tests') {
            steps {
                sh '''
                    echo "Creating test runner container..."
                    docker create --name test-runner --network coapnet \
                        -e COAP_HOST=mock-coap \
                        -e SELENIUM_REMOTE_URL=http://selenium-standalone:4444/wd/hub \
                        -e CI=true \
                        -e PYTHONUNBUFFERED=1 \
                        python:3.10 bash -c "
                            cd /workspace &&
                            pip install --upgrade pip &&
                            pip install -r requirements.txt &&
                            mkdir -p reports &&
                            pytest --junitxml=reports/junit.xml --html=reports/report.html --self-contained-html -v
                        "

                    echo "Copying workspace files into container..."
                    docker cp . test-runner:/workspace

                    echo "Running tests..."
                    docker start -a test-runner

                    echo "Copying reports back..."
                    docker cp test-runner:/workspace/reports ./reports || true
                '''
            }
        }

    }

    post {
        always {
            echo "Cleaning up containers..."
            sh '''
                docker rm -f mock-coap mock-rest selenium-standalone test-runner || true
            '''
            junit 'reports/junit.xml'
            archiveArtifacts artifacts: 'reports/**/*'
            publishHTML([
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: 'report.html',
                reportName: 'Test Report'
            ])
        }
    }
}
