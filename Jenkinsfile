pipeline {
    agent { label 'built-in' }

    environment {
        PYTHONUNBUFFERED = "1"
        CI = "true"
        SELENIUM_REMOTE_URL = "http://127.0.0.1:4444/wd/hub"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        /* 🔍 NEW DEBUG STAGE — SHOW REAL WORKSPACE PATH */
        stage('Find Actual Workspace Path') {
            steps {
                sh """
                    echo '=== CURRENT JENKINS WORKSPACE ==='
                    pwd

                    echo '=== CONTENTS OF WORKSPACE ==='
                    ls -al

                    echo '=== FULL TREE (2 levels deep) ==='
                    find . -maxdepth 2 -type f -print
                """
            }
        }

        stage('Setup Python') {
            steps {
                sh """
                    set -e
                    python3 -m venv venv
                    venv/bin/pip install --upgrade pip setuptools wheel
                    venv/bin/pip install -r requirements.txt
                """
            }
        }

        stage('Start Mock Services') {
            steps {
                sh """
                    docker rm -f selenium-standalone || true
                    docker rm -f mock-rest || true
                    docker rm -f mock-coap || true

                    echo "Starting REST mock..."
                    docker run -d --name mock-rest \
                        --network coapnet \
                        -p 8000:8000 \
                        -v "$WORKSPACE/mock_servers:/app" \
                        python:3.10 bash -c "pip install flask && python /app/mock_rest_server.py"

                    echo 'Starting CoAP mock...'
                    docker run -d --name mock-coap \
                        --network coapnet \
                        -p 5683:5683/udp \
                        -v "$WORKSPACE/mock_servers:/app" \
                        python:3.10 bash -c "pip install aiocoap && python /app/mock_coap_server.py"

                    echo "Starting Selenium Standalone Chrome..."
                    docker run -d --name selenium-standalone \
                        --network coapnet \
                        -p 4444:4444 \
                        --shm-size=2g \
                        selenium/standalone-chrome:latest
                """

                sh """
                    echo 'Waiting for Selenium WebDriver...'
                    for i in {1..20}; do
                        if curl -s http://127.0.0.1:4444/wd/hub/status | grep -q '"ready":true'; then
                            echo 'Selenium is ready!'
                            break
                        fi
                        echo 'Still waiting...'
                        sleep 2
                    done
                """
            }
        }

        stage('Run Tests Inside Docker') {
            steps {
                sh """
                    echo '=== Running tests inside isolated container ==='

                    docker run --rm \
                        --network coapnet \
                        -e COAP_HOST=mock-coap \
                        -e CI=true \
                        -e PYTHONUNBUFFERED=1 \
                        -v "$WORKSPACE:/workspace" \
                        -w /workspace \
                        python:3.10 bash -c "
                            echo 'Checking mounted workspace:' && ls -al /workspace && \
                            pip install --upgrade pip && \
                            pip install -r /workspace/requirements.txt && \
                            mkdir -p /workspace/reports && \
                            pytest --junitxml=/workspace/reports/junit.xml \
                                   --html=/workspace/reports/report.html \
                                   --self-contained-html \
                                   -v
                        "
                """
            }
        }
    }

    post {
        always {
            echo "Cleaning up containers..."

            sh """
                docker rm -f selenium-standalone || true
                docker rm -f mock-rest || true
                docker rm -f mock-coap || true
            """

            junit 'reports/junit.xml'

            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true

            publishHTML(target: [
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
