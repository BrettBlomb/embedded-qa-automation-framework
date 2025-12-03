pipeline {
    agent any

    environment {
        CI = "true"
        API_BASE_URL = "https://example.com"
        UI_BASE_URL  = "https://the-internet.herokuapp.com"
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

            // --- JUnit test page in Jenkins ---
            junit 'reports/junit.xml'

            // --- Archive all files in reports/ folder ---
            archiveArtifacts artifacts: 'reports/*', fingerprint: true

            // --- Publish pretty HTML report ---
            publishHTML([
                reportDir: 'reports',
                reportFiles: 'report.html',
                reportName: 'Pytest Report',
                keepAll: true,
                alwaysLinkToLastBuild: true,
                allowMissing: false
            ])
        }
    }
}
