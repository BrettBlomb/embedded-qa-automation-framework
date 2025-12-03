pipeline {
    agent any

    environment {
        CI = "true"
        API_BASE_URL = "https://httpbin.org"
        UI_BASE_URL = "https://example.com"
        # COAP_HOST and COAP_PORT could be set to a running mock device
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/YOURNAME/embedded-qa-automation.git'
            }
        }

        stage('Setup Python') {
            steps {
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install --upgrade pip'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }
        }

        stage('Run API Tests') {
            steps {
                sh '. venv/bin/activate && pytest tests/api -v'
            }
        }

        stage('Run UI Tests') {
            steps {
                sh '. venv/bin/activate && pytest tests/ui -v'
            }
        }

        stage('Run Embedded & Network Tests') {
            steps {
                sh '. venv/bin/activate && pytest tests/embedded tests/network -v'
            }
        }

        stage('Run Security Tests') {
            steps {
                sh '. venv/bin/activate && pytest tests/security -v'
            }
        }

        stage('Full Suite with Reports') {
            steps {
                sh 'mkdir -p reports'
                sh '. venv/bin/activate && pytest'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/*.html', fingerprint: true
            junit 'reports/junit.xml'
        }
    }
}
