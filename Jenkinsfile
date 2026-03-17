pipeline {
    agent any

    environment {
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

                    echo "Creating CoAP mock server container..."
                    docker create --name mock-coap --network coapnet \
                        -p 5683:5683/udp \
                        python:3.10 bash -c 'pip install aiocoap && python /app/mock_coap_server.py'

                    echo "Copying mock server files to CoAP container..."
                    docker cp mock_servers/. mock-coap:/app/

                    echo "Starting CoAP mock server..."
                    docker start mock-coap

                    echo "Creating REST mock server container..."
                    docker create --name mock-rest --network coapnet \
                        -p 8000:8000 \
                        python:3.10 bash -c 'pip install flask && python /app/mock_rest_server.py'

                    echo "Copying mock server files to REST container..."
                    docker cp mock_servers/. mock-rest:/app/

                    echo "Starting REST mock server..."
                    docker start mock-rest

                    echo "Starting Selenium..."
                    docker run -d --name selenium-standalone --network coapnet \
                        -p 4444:4444 --shm-size=2g selenium/standalone-chrome:latest
                '''

                sh '''
                    echo "Waiting for CoAP server to be ready..."
                    sleep 10
                    echo "Checking CoAP container status..."
                    docker logs mock-coap 2>&1 | tail -20 || true
                '''

                sh '''
                    echo "Waiting for Selenium WebDriver..."
                    for i in {1..30}; do
                        if curl -s http://127.0.0.1:4444/wd/hub/status | grep -q '"ready":true'; then
                            echo "Selenium is ready!"
                            break
                        fi
                        echo "Still waiting... ($i)"
                        sleep 2
                    done
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
                            pytest --junitxml=reports/junit.xml --html=reports/report.html --self-contained-html -v || true
                        "

                    echo "Copying workspace files into container..."
                    docker cp . test-runner:/workspace

                    echo "Running tests..."
                    docker start -a test-runner || true

                    echo "Copying reports back..."
                    mkdir -p reports
                    docker cp test-runner:/workspace/reports/. ./reports/ || true

                    echo "Reports copied:"
                    ls -la reports/ || true
                '''
            }
        }

    }

    post {
        always {
            echo "Copying any remaining reports..."
            sh '''
                docker cp test-runner:/workspace/reports/. ./reports/ 2>/dev/null || true
            '''

            echo "Cleaning up containers..."
            sh '''
                docker rm -f mock-coap mock-rest selenium-standalone test-runner || true
            '''

            junit allowEmptyResults: true, testResults: 'reports/junit.xml'
            archiveArtifacts artifacts: 'reports/**/*', allowEmptyArchive: true
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
