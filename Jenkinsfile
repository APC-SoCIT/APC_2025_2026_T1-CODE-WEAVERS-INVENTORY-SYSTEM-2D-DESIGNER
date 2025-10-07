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
          def hasComposeV2 = sh(returnStatus: true, script: 'docker compose version >/dev/null 2>&1') == 0
          env.COMPOSE_CMD = hasComposeV2 ? 'docker compose' : 'docker-compose'
          echo "Using ${env.COMPOSE_CMD}"
        }
      }
    }
    stage('Prepare Env') {
      steps {
        sh 'cp -f .env.docker .env || true'
      }
    }
    stage('Build') {
      steps {
        sh '''
          $COMPOSE_CMD build
        '''
      }
    }
    stage('Start Services') {
      steps {
        sh '''
          $COMPOSE_CMD up -d
        '''
      }
    }
    stage('Migrate') {
      steps {
        sh '''
          $COMPOSE_CMD run --rm web python manage.py migrate --noinput
        '''
      }
    }
    stage('Collect Static') {
      steps {
        sh '''
          $COMPOSE_CMD run --rm web python manage.py collectstatic --noinput
        '''
      }
    }
    stage('Tests') {
      steps {
        sh '''
          $COMPOSE_CMD run --rm web python manage.py test
        '''
      }
    }
  }
  post {
    always {
      sh '''
        if docker compose version >/dev/null 2>&1; then
          docker compose down -v
        else
          docker-compose down -v
        fi || true
      '''
    }
  }
}