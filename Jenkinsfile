
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
       
        disableConcurrentBuilds()
    }
    environment {
     
        REGISTRY_USER = 'mirroness'
        
        APP_IMAGE = "${REGISTRY_USER}/police-app"
    
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
                
                bat 'docker run --rm %APP_IMAGE%:%TAG% python -m pytest -v'
            }
        }
     
        stage('Push') {
            when { expression { isMaster() } }
            steps {
                
                withCredentials([usernamePassword(credentialsId: 'dockerhub',
                                 usernameVariable: 'DH_USER', passwordVariable: 'DH_TOKEN')]) {
                    bat 'echo %DH_TOKEN%| docker login -u %DH_USER% --password-stdin'
                }
               
                bat 'docker tag %APP_IMAGE%:%TAG% %APP_IMAGE%:%BUILD_NUMBER%'
                bat 'docker tag %APP_IMAGE%:%TAG% %APP_IMAGE%:latest'
                bat 'docker push %APP_IMAGE%:%BUILD_NUMBER%'
                bat 'docker push %APP_IMAGE%:latest'
            }
        }
        stage('Deploy') {
            when { expression { isMaster() } }
            steps {
             
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
           
            bat script: 'docker rmi %APP_IMAGE%:%TAG%', returnStatus: true
            bat script: 'docker rmi %APP_IMAGE%:%BUILD_NUMBER%', returnStatus: true
            bat script: 'docker logout', returnStatus: true
        }
    }
}