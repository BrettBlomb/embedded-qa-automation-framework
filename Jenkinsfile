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
                        -p 8000:8000 \
                        --network coapnet \
                        -v "$WORKSPACE/mock_servers:/app" \
                        python:3.10 bash -c "pip install flask && python /app/mock_rest_server.py"

                    echo "Starting CoAP mock..."
                    docker run -d --name mock-coap \
                        -p 5683:5683/udp \
                        --network coapnet \
                        -v "$WORKSPACE/mock_servers:/app" \
                        python:3.10 bash -c "pip install aiocoap && python /app/mock_coap_server.py"

                    echo "Starting Selenium Standalone Chrome..."
                    docker run -d --name selenium-standalone \
                        -p 4444:4444 \
                        --shm-size=2g \
                        --network coapnet \
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
                    echo '===== DEBUG: Jenkins WORKSPACE ====='
                    echo "HOST WORKSPACE: $WORKSPACE"
                    ls -al "$WORKSPACE"

                    echo '===== STARTING TEST CONTAINER WITH DEBUG ====='

                    docker run --rm \
                        --network coapnet \
                        -e COAP_HOST=mock-coap \
                        -e CI=true \
                        -e PYTHONUNBUFFERED=1 \
                        -v "$WORKSPACE:/workspace" \
                        -w /workspace \
                        python:3.10 bash -c "
                            echo '--- INSIDE CONTAINER DEBUG ---' && \
                            echo 'pwd:' && pwd && \
                            echo 'ls -al (current dir):' && ls -al && \
                            echo 'ls -al /workspace:' && ls -al /workspace && \
                            echo 'Checking for requirements.txt:' && ls -al requirements.txt && \
                            pip install --upgrade pip && \
                            pip install -r requirements.txt && \
                            mkdir -p reports && \
                            pytest --junitxml=reports/junit.xml \
                                   --html=reports/report.html \
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
