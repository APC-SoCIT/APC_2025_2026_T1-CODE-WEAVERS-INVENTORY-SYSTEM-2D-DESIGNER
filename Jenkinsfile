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
            env.COMPOSE_EXE = 'docker'
            env.COMPOSE_SUBCMD = 'compose'
            echo 'Using docker compose (v2)'
          } else if (hasV1) {
            env.COMPOSE_EXE = 'docker-compose'
            env.COMPOSE_SUBCMD = ''
            echo 'Using docker-compose (v1)'
          } else {
            error('Docker Compose not found. Install Docker Desktop (Compose v2) or docker-compose.')
          }
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
          if ($env:COMPOSE_SUBCMD) { & $env:COMPOSE_EXE $env:COMPOSE_SUBCMD build } else { & $env:COMPOSE_EXE build }
        '''
      }
    }
    stage('Start Services') {
      steps {
        powershell '''
          if ($env:COMPOSE_SUBCMD) { & $env:COMPOSE_EXE $env:COMPOSE_SUBCMD up -d } else { & $env:COMPOSE_EXE up -d }
        '''
      }
    }
    stage('Migrate') {
      steps {
        powershell '''
          if ($env:COMPOSE_SUBCMD) { & $env:COMPOSE_EXE $env:COMPOSE_SUBCMD run --rm web python manage.py migrate --noinput } else { & $env:COMPOSE_EXE run --rm web python manage.py migrate --noinput }
        '''
      }
    }
    stage('Collect Static') {
      steps {
        powershell '''
          if ($env:COMPOSE_SUBCMD) { & $env:COMPOSE_EXE $env:COMPOSE_SUBCMD run --rm web python manage.py collectstatic --noinput } else { & $env:COMPOSE_EXE run --rm web python manage.py collectstatic --noinput }
        '''
      }
    }
    stage('Tests') {
      steps {
        powershell '''
          if ($env:COMPOSE_SUBCMD) { & $env:COMPOSE_EXE $env:COMPOSE_SUBCMD run --rm web python manage.py test } else { & $env:COMPOSE_EXE run --rm web python manage.py test }
        '''
      }
    }
  }
  post {
    always {
      script {
        powershell(returnStatus: true, script: 'if ($env:COMPOSE_SUBCMD) { & $env:COMPOSE_EXE $env:COMPOSE_SUBCMD down -v } else { & $env:COMPOSE_EXE down -v }')
      }
    }
  }
}