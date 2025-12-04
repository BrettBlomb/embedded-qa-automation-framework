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

        stage('Start Mock Services') {
            steps {
                sh """
                    echo 'Cleaning old containers...'
                    docker rm -f selenium-standalone || true
                    docker rm -f mock-rest || true
                    docker rm -f mock-coap || true

                    echo 'Creating docker network...'
                    docker network create coapnet || true

                    echo 'Starting REST mock server...'
                    docker run -d --name mock-rest \
                        --network coapnet \
                        -p 8000:8000 \
                        -v "$WORKSPACE/mock_servers:/app" \
                        python:3.10 bash -c "
                            pip install flask &&
                            python /app/mock_rest_server.py
                        "

                    echo 'Starting CoAP mock server...'
                    docker run -d --name mock-coap \
                        --network coapnet \
                        -p 5683:5683/udp \
                        -v "$WORKSPACE/mock_servers:/app" \
                        python:3.10 bash -c "
                            pip install aiocoap &&
                            python /app/mock_coap_server.py
                        "

                    echo 'Starting Selenium Chrome Standalone...'
                    docker run -d --name selenium-standalone \
                        --network coapnet \
                        -p 4444:4444 \
                        --shm-size=2g \
                        selenium/standalone-chrome:latest
                """

                sh """
                    echo 'Waiting for Selenium...'
                    for i in {1..20}; do
                        if curl -s http://127.0.0.1:4444/wd/hub/status | grep -q '"ready":true'; then
                            echo 'Selenium is ready!'
                            break
                        fi
                        echo 'Waiting for Selenium...'
                        sleep 2
                    done
                """

                sh """
                    echo 'Waiting for CoAP mock server (UDP 5683)...'
                    for i in {1..20}; do
                        if docker exec mock-coap sh -c "netstat -anu | grep 5683" > /dev/null 2>&1; then
                            echo 'CoAP server is ready!'
                            break
                        fi
                        echo 'Waiting for CoAP...'
                        sleep 1
                    done
                """
            }
        }

        stage('Debug Workspace') {
            steps {
                sh """
                    echo '=== WORKSPACE ROOT CONTENTS ==='
                    ls -al "$WORKSPACE"

                    echo '=== FULL WORKSPACE TREE ==='
                    ls -R "$WORKSPACE"
                """
            }
        }

        stage('Run Tests Inside Docker') {
            steps {
                sh """
                    echo 'Starting pytest inside Docker container on coapnet...'

                    docker run --rm \
                        --network coapnet \
                        -e COAP_HOST=mock-coap \
                        -v "$WORKSPACE:/workspace" \
                        -w /workspace \
                        python:3.10 bash -c "
                            pip install --upgrade pip &&
                            pip install -r requirements.txt &&
                            mkdir -p reports &&
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
