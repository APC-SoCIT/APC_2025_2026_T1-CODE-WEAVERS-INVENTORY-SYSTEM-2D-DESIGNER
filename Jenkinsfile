pipeline {
  agent any
  options { timestamps(); ansiColor('xterm') }
  environment {
    APP_URL = 'http://localhost:8000'
  }
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
    stage('Smoke Test') {
      steps {
        powershell """
          $ErrorActionPreference = 'Stop'
          Write-Host 'Waiting for web to be ready...'
          $retries = 15
          for ($i=0; $i -lt $retries; $i++) {
            try {
              $resp = Invoke-WebRequest -Uri '${APP_URL}' -UseBasicParsing -TimeoutSec 5
              if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500) { Write-Host 'App is up.'; break }
            } catch { Start-Sleep -Seconds 2 }
            if ($i -eq ($retries-1)) { throw 'App did not become ready in time.' }
          }
        """
      }
    }
  }
  post {
    always {
      powershell 'docker ps'
    }
  }
}