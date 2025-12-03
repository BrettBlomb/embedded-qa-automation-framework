pipeline {
    agent any

    environment {
        CI = "true"

        # Use local mock REST API
        API_BASE_URL = "http://localhost:8000/api"

        # Selenium UI base URL
        UI_BASE_URL  = "https://the-internet.herokuapp.com"
    }

    options {
        timestamps()
    }

    stages {

        /* -----------------------------
         * SETUP PYTHON + DEPENDENCIES
         * ----------------------------- */
        stage('Setup Python') {
            steps {
                sh '''
                    set -e

                    python3 -m venv venv
                    . venv/bin/activate

                    pip install --upgrade pip

                    # Project dependencies
                    pip install -r requirements.txt

                    # UI + Mock server dependencies
                    pip install selenium webdriver-manager flask aiocoap
                '''
            }
        }

        /* -----------------------------
         * INSTALL GOOGLE CHROME
         * ----------------------------- */
        stage('Install Chrome') {
            steps {
                sh '''
                    set -e

                    # Add Google signing key
                    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add -

                    # Add Chrome repo
                    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
                        > /etc/apt/sources.list.d/google-chrome.list

                    apt-get update
                    apt-get install -y google-chrome-stable xvfb
                '''
            }
        }

        /* -----------------------------
         * START MOCK REST & COAP SERVERS
         * ----------------------------- */
        stage('Start Mock Services') {
            steps {
                sh '''
                    set -e
                    . venv/bin/activate

                    # Start REST mock server (Flask)
                    python3 mock_servers/mock_rest_server.py &
                    
                    # Start CoAP mock server
                    python3 mock_servers/mock_coap_server.py &

                    # Give them time to boot
                    sleep 3
                '''
            }
        }

        /* -----------------------------
         * RUN ALL TESTS
         * ----------------------------- */
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

    /* -----------------------------
     * POST: ALWAYS PUBLISH REPORTS
     * ----------------------------- */
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
