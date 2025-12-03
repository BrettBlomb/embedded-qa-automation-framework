pipeline {
    agent any

    environment {
        // Mark that we're running in CI so tests can behave differently if needed
        CI = "true"

        // App / test config
        API_BASE_URL = "https://example.com"
        UI_BASE_URL  = "https://the-internet.herokuapp.com"
        // ENABLE_UI_IN_CI = "true"   // uncomment if you later want UI tests to run in Jenkins
    }

    options {
        timestamps()
    }

    stages {
        stage('Setup Python') {
            steps {
                sh '''
                    set -e

                    # Create virtualenv
                    python3 -m venv venv

                    # Activate and install deps
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

                    # Run pytest with JUnit + HTML reports
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
            // Publish JUnit results to Jenkins "Tests" view
            junit 'reports/junit.xml'

            // Archive all report files as build artifacts
            archiveArtifacts artifacts: 'reports/*', fingerprint: true

            // Pretty HTML link in the sidebar (HTML Publisher plugin)
            publishHTML(target: [
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
