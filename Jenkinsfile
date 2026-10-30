
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
        PYTHON     = 'C:\\Users\\Alex\\AppData\\Local\\Python\\bin\\python.exe'
        DEPLOY_DIR = 'C:\\police-app'
        APP_PORT   = '5000'
    }
    stages {
        stage('Install') {
            steps {
                echo "Branch: ${currentBranch()}"
                bat '"%PYTHON%" -m venv venv'
                bat 'venv\\Scripts\\python -m pip install --disable-pip-version-check -r requirements.txt'
            }
        }
        stage('Test') {
            steps {
                bat 'venv\\Scripts\\python -m pytest -v'
            }
        }
        
        stage('Deploy') {
            when { expression { isMaster() } }
            steps {
               
                withEnv(['JENKINS_NODE_COOKIE=dontKillMe']) {
                    bat 'powershell -NoProfile -ExecutionPolicy Bypass -File deploy.ps1 -DeployDir "%DEPLOY_DIR%" -Port %APP_PORT% -Python "%PYTHON%"'
                }
            }
        }
    }
}