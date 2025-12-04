pipeline {
    agent {
        label 'built-in'
    }

    environment {
        PYTHONUNBUFFERED = "1"
        CI = "true"
        SELENIUM_REMOTE_URL = "http://127.0.0.1:4444/wd/hub"
        PATH = "$WORKSPACE/venv/bin:$PATH"
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
                    # Cleanup old containers if they exist
                    docker rm -f selenium-standalone || true
                    docker rm -f mock-rest || true
                    docker rm -f mock-coap || true

                    # Create Docker bridge network (idempotent)
                    docker network create coapnet || true

                    echo "Starting REST mock..."
                    docker run -d --name mock-rest \
                        --network coapnet \
                        -p 8000:8000 \
                        -v "${WORKSPACE}/mock_servers:/app" \
                        python:3.10 bash -c "pip install flask && python /app/mock_rest_server.py"

                    echo "Starting CoAP mock..."
                    docker run -d --name mock-coap \
                        --network coapnet \
                        -p 5683:5683/udp \
                        -v "${WORKSPACE}/mock_servers:/app" \
                        python:3.10 bash -c "pip install aiocoap && python /app/mock_coap_server.py"

                    echo 'Starting Selenium Standalone Chrome...'
                    docker run -d --name selenium-standalone \
                        --network coapnet \
                        -p 4444:4444 \
                        --shm-size=2g \
                        selenium/standalone-chrome:latest
                """

                // Wait for Selenium to be ready
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

                // (Optional) Quick CoAP readiness check
                sh """
                    echo 'Waiting for CoAP mock server (UDP 5683)...'
                    for i in {1..20}; do
                        if docker exec mock-coap sh -c "netstat -anu | grep 5683" > /dev/null 2>&1; then
                            echo 'CoAP server is ready!'
                            break
                        fi
                        echo 'Still waiting for CoAP...'
                        sleep 1
                    done
                """
            }
        }

        stage('Run Tests Inside Docker') {
            steps {
                sh """
                    docker run --rm \
                        --network coapnet \
                        -e COAP_HOST=mock-coap \
                        -e CI=true \
                        -e PYTHONUNBUFFERED=1 \
                        -v "${pwd()}:/workspace" \
                        -w /workspace \
                        python:3.10 bash -c "
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
            // Clean up containers even on failure
            sh """
                docker rm -f selenium-standalone || true
                docker rm -f mock-rest || true
                docker rm -f mock-coap || true
            """

            // Collect test results (if they exist)
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
