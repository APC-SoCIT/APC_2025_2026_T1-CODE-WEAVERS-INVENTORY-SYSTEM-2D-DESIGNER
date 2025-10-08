pipeline {
  agent any
  options { timestamps() }
  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }
    stage('Detect Compose Command') {
      steps {
        script {
          def hasV2 = powershell(returnStatus: true, script: '$ErrorActionPreference = "SilentlyContinue"; docker compose version') == 0
          def hasV1 = powershell(returnStatus: true, script: '$ErrorActionPreference = "SilentlyContinue"; docker-compose --version') == 0
          if (hasV2) {
            env.COMPOSE_CMD = 'docker compose'
          } else if (hasV1) {
            env.COMPOSE_CMD = 'docker-compose'
          } else {
            error('Docker Compose not found. Install Docker Desktop (Compose v2) or docker-compose.')
          }
          echo "Using ${env.COMPOSE_CMD}"
        }
      }
    }
    stage('Prepare Env') {
      steps {
        powershell 'if (Test-Path ".env.docker") { Copy-Item -Force .env.docker .env }'
      }
    }
    stage('Build') {
      steps {
        powershell '''
          $env:COMPOSE_CMD build
        '''
      }
    }
    stage('Start Services') {
      steps {
        powershell '''
          $env:COMPOSE_CMD up -d
        '''
      }
    }
    stage('Migrate') {
      steps {
        powershell '''
          $env:COMPOSE_CMD run --rm web python manage.py migrate --noinput
        '''
      }
    }
    stage('Collect Static') {
      steps {
        powershell '''
          $env:COMPOSE_CMD run --rm web python manage.py collectstatic --noinput
        '''
      }
    }
    stage('Tests') {
      steps {
        powershell '''
          $env:COMPOSE_CMD run --rm web python manage.py test
        '''
      }
    }
  }
  post {
    always {
      script {
        powershell(returnStatus: true, script: '$env:COMPOSE_CMD down -v')
      }
    }
  }
}