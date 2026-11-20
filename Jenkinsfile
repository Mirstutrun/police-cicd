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
        // логин на Docker Hub (только строчные буквы)
        REGISTRY_USER = 'mirstutrun'
        // имя образа в реестре: <логин>/police-app
        APP_IMAGE = "${REGISTRY_USER}/police-app"
        // временный тег этой сборки, например police-ci-7
        TAG = "${env.JOB_NAME}-${env.BUILD_NUMBER}"
    }
    stages {
        stage('Build') {
            steps {
                echo "Branch: ${currentBranch()}"
                bat 'docker build -t %APP_IMAGE%:%TAG% .'
            }
        }
        stage('Test') {
            steps {
                // тесты запускаются внутри только что собранного образа
                bat 'docker run --rm %APP_IMAGE%:%TAG% python -m pytest -v'
            }
        }
        // в реестр попадает только протестированный образ из master
        stage('Push') {
            when { expression { isMaster() } }
            steps {
                // логин и токен Docker Hub хранятся в Jenkins (Credentials, ID dockerhub)
                withCredentials([usernamePassword(credentialsId: 'dockerhub',
                                 usernameVariable: 'DH_USER', passwordVariable: 'DH_TOKEN')]) {
                    bat 'echo %DH_TOKEN%| docker login -u %DH_USER% --password-stdin'
                }
                // версия с номером сборки (для истории и отката) и latest (текущая)
                bat 'docker tag %APP_IMAGE%:%TAG% %APP_IMAGE%:%BUILD_NUMBER%'
                bat 'docker tag %APP_IMAGE%:%TAG% %APP_IMAGE%:latest'
                bat 'docker push %APP_IMAGE%:%BUILD_NUMBER%'
                bat 'docker push %APP_IMAGE%:latest'
            }
        }
        stage('Deploy') {
            when { expression { isMaster() } }
            steps {
                // nginx собирается из своего Dockerfile, приложение берется из образа, отправленного в реестр
                bat 'docker compose build nginx'
                bat 'docker compose up -d --wait'
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
            // убрать временные теги этой сборки и выйти из реестра
            bat script: 'docker rmi %APP_IMAGE%:%TAG%', returnStatus: true
            bat script: 'docker rmi %APP_IMAGE%:%BUILD_NUMBER%', returnStatus: true
            bat script: 'docker logout', returnStatus: true
        }
    }
}