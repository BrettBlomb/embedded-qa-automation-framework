pipeline {
    agent any

    environment {
        CI = "true"
        API_BASE_URL = "https://httpbin.org"
        UI_BASE_URL = "https://the-internet.herokuapp.com"
        // COAP_HOST and COAP_PORT could be set to a running mock device
        // COAP_HOST = "localhost"
        // COAP_PORT = "5683"
    }

    stages {
        stage('Checkout') {
            steps {
                // Optional: Jenkins already checked out the repo via "Pipeline from SCM"
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install --upgrade pip'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'mkdir -p reports'
                sh '. venv/bin/activate && pytest'
            }
        }
    }

    post {
        always {
            // Publish reports if plugins are installed
            junit 'reports/junit.xml'
            archiveArtifacts artifacts: 'reports/*.html', fingerprint: true
        }
    }
}
