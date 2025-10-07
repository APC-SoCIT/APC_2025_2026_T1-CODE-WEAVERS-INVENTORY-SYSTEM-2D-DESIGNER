pipeline {
  agent any
  options { timestamps() }
  parameters {
    booleanParam(name: 'KEEP_RUNNING', defaultValue: false, description: 'Keep the Django server running after the job')
    string(name: 'PORT', defaultValue: '8000', description: 'Port for runserver')
  }
  environment {
    VENV = "${WORKSPACE}/.venv"
  }
  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }
    stage('Prepare Env') {
      steps {
        sh 'cp -f .env.example .env 2>/dev/null || true'
      }
    }
    stage('Setup Python') {
      steps {
        sh '''
          python3 -m venv "$VENV"
          "$VENV/bin/pip" install --upgrade pip
          "$VENV/bin/pip" install -r requirements.txt
        '''
      }
    }
    stage('Migrate') {
      steps {
        sh '"$VENV/bin/python" manage.py migrate --noinput'
      }
    }
    stage('Collect Static') {
      steps {
        sh '"$VENV/bin/python" manage.py collectstatic --noinput'
      }
    }
    stage('Run Server') {
      steps {
        sh '''
          nohup "$VENV/bin/python" manage.py runserver 0.0.0.0:${PORT} > runserver.log 2>&1 &
          echo $! > runserver.pid
          echo "Server started at http://localhost:${PORT}"
        '''
        script {
          if (params.KEEP_RUNNING) {
            echo "KEEP_RUNNING=true: tailing logs to keep job active."
            sh 'tail -f runserver.log'
          }
        }
      }
    }
  }
  post {
    always {
      script {
        if (!params.KEEP_RUNNING) {
          sh '''
            if [ -f runserver.pid ]; then
              kill $(cat runserver.pid) || true
              rm -f runserver.pid
            fi
          '''
        }
      }
    }
  }
}