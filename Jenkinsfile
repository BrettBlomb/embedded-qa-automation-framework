pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Start Mock Services') {
            steps {
                sh '''
                    echo "Starting REST mock server..."
                    nohup venv/bin/python mock/rest_mock_server.py > rest.log 2>&1 &

                    echo "Starting CoAP mock server..."
                    nohup venv/bin/python mock/coap_mock_server.py > coap.log 2>&1 &

                    echo "Starting Selenium Standalone Chrome..."
                    docker run -d --rm --name selenium-standalone -p 4444:4444 selenium/standalone-chrome:latest

                    sleep 5
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest --junitxml=reports/junit.xml --html=reports/report.html
                '''
            }
        }
    }

    post {
        always {
            sh 'docker rm -f selenium-standalone || true'
            junit 'reports/junit.xml'
            archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
            publishHTML(reportDir: 'reports', reportFiles: 'report.html', reportName: 'Test Report')
        }
    }
}
