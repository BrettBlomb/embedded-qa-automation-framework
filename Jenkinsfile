pipeline {
    agent any

    environment {
        // Flag tests that they are running in CI
        CI = "true"

        // REST mock server base URL
        API_BASE_URL = "http://127.0.0.1:5001"

        // UI base URL (public demo site)
        UI_BASE_URL  = "https://the-internet.herokuapp.com"

        // CoAP server port (matches mock_coap_server)
        COAP_PORT = "5683"

        // Selenium standalone-chrome endpoint
        SELENIUM_REMOTE_URL = "http://127.0.0.1:4444/wd/hub"
    }

    options {
        timestamps()
    }

    stages {
        stage('Setup Python') {
            steps {
                sh '''
                    set -e

                    python3 -m venv venv

                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt

                    # Extra deps for mocks (Flask, aiocoap already in requirements)
                    pip install flask aiocoap
                '''
            }
        }

        stage('Start Mock Services') {
            steps {
                sh '''
                    set -e
                    . venv/bin/activate

                    # Start REST mock server on 5001
                    nohup python mock_servers/mock_rest_server.py \
                        > rest_mock.log 2>&1 &

                    # Start CoAP mock server on 5683
                    nohup python mock_servers/mock_coap_server.py \
                        > coap_mock.log 2>&1 &

                    # Start Selenium standalone Chrome via Docker
                    # Container will listen on 4444
                    if ! docker ps --format '{{.Names}}' | grep -q '^selenium-standalone$'; then
                      docker run -d --rm \
                        --name selenium-standalone \
                        -p 4444:4444 \
                        -p 7900:7900 \
                        selenium/standalone-chrome:latest
                    fi

                    # Give services a moment to come up
                    sleep 5
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    set -e
                    . venv/bin/activate

                    mkdir -p reports

                    pytest \
                      --junitxml=reports/junit.xml \
                      --html=reports/report.html \
                      --self-contained-html
                '''
            }
        }
    }

    post {
        always {
            // Stop Selenium container if it's still running
            script {
                try {
                    sh 'docker rm -f selenium-standalone || true'
                } catch (ignored) {
                    // ignore docker errors in post
                }
            }

            // Publish JUnit results to Jenkins "Tests" view
            junit 'reports/junit.xml'

            // Archive all report files as build artifacts
            archiveArtifacts artifacts: 'reports/*', fingerprint: true

            // Pretty HTML report in the sidebar
            publishHTML(target: [
                reportDir: 'reports',
                reportFiles: 'report.html',
                reportName: 'Pytest Report',
                keepAll: true,
                alwaysLinkToLastBuild: true,
                allowMissing: true
            ])
        }
    }
}
