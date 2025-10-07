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
          env.COMPOSE_CMD = 'docker compose'
          echo "Using ${env.COMPOSE_CMD}"
          sh '${COMPOSE_CMD} version || (echo "Docker Compose v2 plugin not available. Install Compose v2 or adjust pipeline." && exit 1)'
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
        $COMPOSE_CMD down -v || true
      '''
    }
  }
}