pipeline {
    agent any

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
                    docker rm -f selenium-standalone || true
                    docker rm -f mock-rest || true
                    docker rm -f mock-coap || true

                    echo "Starting REST mock..."
                    docker run -d --name mock-rest -p 8000:8000 \
                        -v "$WORKSPACE/mock_servers/rest_api:/app" \
                        python:3.10 bash -c "pip install flask && python /app/mock_rest_server.py"

                    echo "Starting CoAP mock..."
                    docker run -d --name mock-coap -p 5683:5683/udp \
                        -v "$WORKSPACE/mock_servers/coap_server:/app" \
                        python:3.10 bash -c "pip install aiocoap && python /app/mock_coap_server.py"

                    echo "Starting Selenium Standalone Chrome..."
                    docker run -d --name selenium-standalone \
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
            }
        }

        stage('Run Tests') {
            steps {
                sh """
                    mkdir -p reports

                    venv/bin/pytest \
                        --junitxml=reports/junit.xml \
                        --html=reports/report.html \
                        --self-contained-html \
                        -v
                """
            }
        }
    }

    post {
        always {

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
