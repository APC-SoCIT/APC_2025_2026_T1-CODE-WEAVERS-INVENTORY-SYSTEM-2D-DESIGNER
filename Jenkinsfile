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
          set +e
          # Try built-in venv first
          python3 -m venv "$VENV"
          VENV_OK=$?
          if [ "$VENV_OK" -eq 0 ] && [ -x "$VENV/bin/python" ]; then
            echo "PY_BIN=$VENV/bin/python" > py.env
            echo "PIP_BIN=$VENV/bin/pip" >> py.env
            "$VENV/bin/pip" install --upgrade pip
            "$VENV/bin/pip" install -r requirements.txt
            exit 0
          fi

          echo "Built-in venv failed; attempting virtualenv..."
          # Ensure pip is available; install via get-pip if missing
          if ! command -v pip3 >/dev/null 2>&1; then
            curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
            python3 get-pip.py --user || true
          fi
          # Install virtualenv user-wide, if possible
          python3 -m pip install --user virtualenv >/dev/null 2>&1 || true
          python3 -m virtualenv "$VENV"
          VIRTUALENV_OK=$?
          if [ "$VIRTUALENV_OK" -eq 0 ] && [ -x "$VENV/bin/python" ]; then
            echo "PY_BIN=$VENV/bin/python" > py.env
            echo "PIP_BIN=$VENV/bin/pip" >> py.env
            "$VENV/bin/pip" install --upgrade pip
            "$VENV/bin/pip" install -r requirements.txt
            rm -f get-pip.py || true
            exit 0
          fi

          echo "Virtualenv also failed; falling back to system Python/pip."
          # Final fallback to system Python/pip
          echo "PY_BIN=python3" > py.env
          # Use python3 -m pip to avoid pip3 command dependency
          if ! python3 -m pip --version >/dev/null 2>&1; then
            curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
            python3 get-pip.py --user || true
          fi
          python3 -m pip install --user --upgrade pip || true
          python3 -m pip install --user -r requirements.txt
          rm -f get-pip.py || true
        '''
      }
    }
    stage('Migrate') {
      steps {
        sh '. py.env && "$PY_BIN" manage.py migrate --noinput'
      }
    }
    stage('Collect Static') {
      steps {
        sh '. py.env && "$PY_BIN" manage.py collectstatic --noinput'
      }
    }
    stage('Run Server') {
      steps {
        sh '''
          . py.env
          nohup "$PY_BIN" manage.py runserver 0.0.0.0:${PORT} > runserver.log 2>&1 &
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