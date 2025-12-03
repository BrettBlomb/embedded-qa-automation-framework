pipeline {
    agent any

    environment {
        PYTHONUNBUFFERED = "1"
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
                    # Kill old containers
                    docker rm -f selenium-standalone || true
                    docker rm -f mock-rest || true
                    docker rm -f mock-coap || true

                    # Start mock REST API on 8000
                    docker run -d --name mock-rest -p 8000:8000 \
                        -v "$WORKSPACE/mock_services/rest_api:/app" \
                        python:3.10 bash -c "pip install flask && python /app/mock_rest_server.py"

                    # Start mock CoAP server on 5683
                    docker run -d --name mock-coap -p 5683:5683/udp \
                        -v "$WORKSPACE/mock_services/coap_server:/app" \
                        python:3.10 bash -c "pip install aiocoap && python /app/mock_coap_server.py"

                    # Start Selenium Chrome service on 4444
                    docker run -d --name selenium-standalone \
                        -p 4444:4444 \
                        --shm-size=2g \
                        selenium/standalone-chrome:latest
                """

                // Wait for Selenium Grid to be ready
                sh """
                    echo "Waiting for Selenium..."
                    sleep 10
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
            // Cleanup
            sh """
                docker rm -f selenium-standalone || true
                docker rm -f mock-rest || true
                docker rm -f mock-coap || true
            """

            // Publish test reports
            junit 'reports/junit.xml'

            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true

            publishHTML(
                target: [
                    allowMissing: true,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'report.html',
                    reportName: 'Test Report'
                ]
            )
        }
    }
}
