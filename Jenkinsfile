pipeline {
    agent any
    environment {
        IMAGE_NAME = 'abarrotesweb' // Cambia el nombre de la imagen como prefieras
        DOCKER_HUB_REPO = 'rogelio02/abarrotesweb' // Cambia este nombre
    }
    stages {
        stage('Clonar Repositorio') {
            steps {
                git branch:'master', url: 'https://github.com/aldoht/abarrotesWeb.git' // Cambia esta URL a la de tu repositorio
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
            cleanWs()  // Limpia el espacio de trabajo después de cada ejecución
        }
    }
}
