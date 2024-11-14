pipeline {
    agent any
    tools {
        git "Default"
    }
    environment {
        IMAGE_NAME = 'abarrotesweb'
        DOCKER_HUB_REPO = 'rogelio02/abarrotesweb'
    }
    stages {
        stage('Clonar Repositorio') {
            steps {
                git branch: 'master', url: 'https://github.com/aldoht/abarrotesWeb.git'
            }
        }
        stage('Construir Imagen Docker') {
            steps {
                script {
                    docker.build("${DOCKER_HUB_REPO}:${env.BUILD_ID}")
                }
            }
        }
        stage('Iniciar sesión en Docker Hub') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-credentials') {
                        sh 'echo Sesión iniciada con éxito'
                    }
                }
            }
        }
        stage('Publicar Imagen') {
            steps {
                script {
                    docker.image("${DOCKER_HUB_REPO}:${env.BUILD_ID}").push()
                }
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}
