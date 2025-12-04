stage('Start Mock Services') {
    steps {
        sh """
            # Cleanup old containers
            docker rm -f selenium-standalone || true
            docker rm -f mock-rest || true
            docker rm -f mock-coap || true

            # Create network if not exists
            docker network create coapnet || true

            echo "Starting REST mock..."
            docker run -d --name mock-rest \
                --network coapnet \
                -p 8000:8000 \
                -v "$WORKSPACE/mock_servers:/app" \
                python:3.10 bash -c "pip install flask && python /app/mock_rest_server.py"

            echo "Starting CoAP mock..."
            docker run -d --name mock-coap \
                --network coapnet \
                -p 5683:5683/udp \
                -v "$WORKSPACE/mock_servers:/app" \
                python:3.10 bash -c "pip install aiocoap && python /app/mock_coap_server.py"

            echo "Starting Selenium Standalone Chrome..."
            docker run -d --name selenium-standalone \
                --network coapnet \
                -p 4444:4444 \
                --shm-size=2g \
                selenium/standalone-chrome:latest
        """

        // Selenium readiness wait
        sh """
            echo 'Waiting for Selenium WebDriver...'
            for i in {1..20}; do
                if curl -s http://127.0.0.1:4444/wd/hub/status | grep -q '"ready":true'; then
                    echo 'Selenium is ready!'
                    break
                fi
                echo 'Still waiting...'
                sleep 2
            done
        """

        // CoAP readiness wait
        sh """
            echo 'Waiting for CoAP mock server...'
            for i in {1..20}; do
                if docker exec mock-coap sh -c "netstat -anu | grep 5683" > /dev/null 2>&1; then
                    echo 'CoAP server is ready!'
                    break
                fi
                echo 'Still waiting for CoAP...'
                sleep 1
            done
        """
    }
}
