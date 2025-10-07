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
        sh '''
          if docker compose version >/dev/null 2>&1; then
            echo "COMPOSE_CMD=docker compose" > compose.env
          else
            echo "COMPOSE_CMD=docker-compose" > compose.env
          fi
        '''
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
          . compose.env
          $COMPOSE_CMD build
        '''
      }
    }
    stage('Start Services') {
      steps {
        sh '''
          . compose.env
          $COMPOSE_CMD up -d
        '''
      }
    }
    stage('Migrate') {
      steps {
        sh '''
          . compose.env
          $COMPOSE_CMD run --rm web python manage.py migrate --noinput
        '''
      }
    }
    stage('Collect Static') {
      steps {
        sh '''
          . compose.env
          $COMPOSE_CMD run --rm web python manage.py collectstatic --noinput
        '''
      }
    }
    stage('Tests') {
      steps {
        sh '''
          . compose.env
          $COMPOSE_CMD run --rm web python manage.py test
        '''
      }
    }
  }
  post {
    always {
      sh '''
        if [ -f compose.env ]; then
          . compose.env
          $COMPOSE_CMD down -v
        else
          docker compose down -v || docker-compose down -v || true
        fi
      '''
    }
  }
}