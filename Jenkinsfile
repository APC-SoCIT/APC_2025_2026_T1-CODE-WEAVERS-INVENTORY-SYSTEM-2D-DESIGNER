pipeline {
    agent any

    environment {
        PYTHON = 'python3'
        VENV_DIR = '.venv'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh "${PYTHON} -m venv ${VENV_DIR}"
                sh ". ${VENV_DIR}/bin/activate && pip install --upgrade pip"
                sh ". ${VENV_DIR}/bin/activate && pip install -r requirements.txt"
            }
        }

        stage('Run Website') {
            steps {
                sh ". ${VENV_DIR}/bin/activate && ${PYTHON} app.py"
            }
        }
    }

    post {
        always {
            echo 'Website pipeline completed.'
        }
    }
}
