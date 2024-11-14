pipeline {
    agent any
    environment {
        REPO_URL = 'https://github.com/aldoht/abarrotesWeb.git'
    }
    stages {
        stage('Clone Repository') {
            steps {
                echo 'Cloning the repository...'
                git url: "https://github.com/aldoht/abarrotesWeb.git", branch: 'master'
            }
        }
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                sh 'docker compose build'
            }
        }
        stage('Run Docker Containers') {
            steps {
                echo 'Starting Docker containers...'
                sh 'docker compose up -d'
            }
        }
    }
}
