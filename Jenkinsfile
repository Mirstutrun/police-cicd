// Какая ветка сейчас собирается: у Pipeline-job'а из Git она лежит
// в GIT_BRANCH ("origin/master"), у Multibranch-job'а - в BRANCH_NAME ("master")
def currentBranch() {
    return env.BRANCH_NAME ?: env.GIT_BRANCH ?: ''
}

def isMaster() {
    def b = currentBranch()
    return b == 'master' || b.endsWith('/master')
}

pipeline {
    agent any
    options {
        // не запускать две сборки одновременно
        disableConcurrentBuilds()
    }
    environment {
        // Jenkins работает как служба Windows и обращается к Docker Desktop по TCP
        DOCKER_HOST = 'tcp://localhost:2375'
        // у каждой сборки свой тег образа, например police-app:police-ci-7
        IMAGE_TAG   = "police-app:${env.JOB_NAME}-${env.BUILD_NUMBER}"
    }
    stages {
        stage('Build') {
            steps {
                echo "Branch: ${currentBranch()}"
                bat 'docker build -t %IMAGE_TAG% .'
            }
        }
        stage('Test') {
            steps {
                // тесты запускаются внутри только что собранного образа
                bat 'docker run --rm %IMAGE_TAG% python -m pytest -v'
            }
        }
        // CD: только для master и только если тесты прошли
        stage('Deploy') {
            when { expression { isMaster() } }
            steps {
                // пересобрать и перезапустить изменившиеся контейнеры, дождаться их готовности
                bat 'docker compose up -d --build --wait'
                bat 'docker compose ps'
            }
        }
        stage('Smoke test') {
            when { expression { isMaster() } }
            steps {
                // сайт должен открываться через nginx на порту 80
                bat 'curl.exe -fsS --retry 5 --retry-delay 2 --retry-connrefused -o NUL http://localhost/'
                echo 'App is running: http://localhost/'
            }
        }
    }
    post {
        always {
            // удалить тестовый образ этой сборки, чтобы не копились
            bat script: 'docker rmi %IMAGE_TAG%', returnStatus: true
        }
    }
}