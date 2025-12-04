pipeline {
    agent {
        label 'built-in'
    }

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
                    echo 'Stopping old containers...'
                    docker rm -f selenium-standalone || true
                    docker rm -f mock-rest || true
                    docker rm -f mock-coap || true

                    echo 'Starting REST mock server...'
                    docker run -d --name mock-rest -p 8000:8000 \
                        -v /var/jenkins_home/workspace/${JOB_NAME}/mock_servers:/app \
                        python:3.10 bash -c "pip install flask && python /app/mock_rest_server.py"

                    echo 'Starting CoAP mock server...'
                    docker run -d --name mock-coap -p 5683:5683/udp \
                        -v /var/jenkins_home/workspace/${JOB_NAME}/mock_servers:/app \
                        python:3.10 bash -c "pip install aiocoap && python /app/mock_coap_server.py"

                    echo 'Starting Selenium Standalone Chrome...'
                    docker run -d --name selenium-standalone \
                        -p 4444:4444 \
                        --shm-size=2g \
                        selenium/standalone-chrome:latest
                """

                sh """
                    echo 'Waiting for Selenium WebDriver to be ready...'
                    for i in {1..20}; do
                        if curl -s http://127.0.0.1:4444/wd/hub/status | grep -q '"ready":true'; then
                            echo 'Selenium WebDriver is ready!'
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
                        --volumes-from jenkins \
                        -e COAP_HOST=mock-coap \
                        -e PYTHONUNBUFFERED=1 \
                        -e CI=true \
                        -w /var/jenkins_home/workspace/${JOB_NAME} \
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
