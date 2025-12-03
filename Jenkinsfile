pipeline {
    agent any

    environment {
        CI = "true"
        API_BASE_URL = "http://localhost:8000/api"
        UI_BASE_URL  = "https://the-internet.herokuapp.com"
    }

    stages {

        stage('Setup Python') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install flask aiocoap webdriver-manager
                '''
            }
        }

        stage('Start Mock Services') {
            steps {
                sh '''
                    # Start REST server
                    python3 mock_rest_server.py &
                    # Start CoAP mock
                    python3 mock_coap_server.py &

                    sleep 3
                '''
            }
        }

        stage('Install Chrome for Selenium') {
            steps {
                sh '''
                    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -
                    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
                         > /etc/apt/sources.list.d/google-chrome.list

                    apt-get update
                    apt-get install -y google-chrome-stable xvfb
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
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
            junit 'reports/junit.xml'
            archiveArtifacts 'reports/*'
            publishHTML([
                reportDir: 'reports',
                reportFiles: 'report.html',
                reportName: 'Test Report',
                keepAll: true,
                alwaysLinkToLastBuild: true
            ])
        }
    }
}
