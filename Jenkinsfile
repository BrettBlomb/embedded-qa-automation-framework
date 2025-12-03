pipeline {
    agent {
        docker {
            image 'selenium/standalone-chrome:latest'
            args '-u root'
        }
    }

    environment {
        CI = "true"
        API_BASE_URL = "http://localhost:8000/api"
        UI_BASE_URL  = "https://the-internet.herokuapp.com"
    }

    options { timestamps() }

    stages {

        stage('Setup Python') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install selenium webdriver-manager flask aiocoap
                '''
            }
        }

        stage('Start Mock Services') {
            steps {
                sh '''
                    . venv/bin/activate
                    python3 mock_servers/mock_rest_server.py &
                    python3 mock_servers/mock_coap_server.py &
                    sleep 3
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    mkdir -p reports
                    pytest --junitxml=reports/junit.xml --html=reports/report.html --self-contained-html
                '''
            }
        }
    }

    post {
        always {
            junit 'reports/junit.xml'
            archiveArtifacts artifacts: 'reports/*', fingerprint: true
            publishHTML([
                reportDir: 'reports',
                reportFiles: 'report.html',
                reportName: 'Test Report',
                keepAll: true,
                alwaysLinkToLastBuild: true,
                allowMissing: false
            ])
        }
    }
}
