pipeline {
    agent any

    parameters {
        choice(
            name: 'ACTION',
            choices: ['build_and_deploy', 'rollback', 'build_and_push', 'deploy_only'],
            description: 'Action to perform: "build_and_deploy" for full release, "rollback" to restore prior version directly'
        )
        string(
            name: 'VERSION',
            defaultValue: 'v1.0.0',
            description: 'Target Semantic Release Tag (e.g., v1.0.0, v1.1.0, v1.2.0)'
        )
    }

    environment {
        AWS_REGION      = 'us-east-1'
        AWS_ACCOUNT_ID  = '154560315950'
        ECR_REPO        = 'cicd-web-app'
        ECR_REGISTRY    = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
        ECR_IMAGE       = "${ECR_REGISTRY}/${ECR_REPO}"
        DOCKERHUB_IMAGE = "kemleapx20/cicd-web-app"
        SWARM_MANAGER   = '52.90.56.1'
        SSH_KEY_PATH    = "D:\\University\\Master\\Exercise\\nginx-docker\\Kemleapkeypem.pem"
        STACK_NAME      = 'cicd-homework'
        SERVICE_NAME    = 'cicd-homework_web'
        TARGET_VERSION  = "${params.VERSION}"
    }

    stages {
        stage('Initialize & Resolve Version') {
            steps {
                script {
                    // Automatically detect tag if triggered by Git tag push webhook
                    if (env.TAG_NAME) {
                        env.TARGET_VERSION = env.TAG_NAME
                        echo "Triggered by Git Tag push: ${env.TARGET_VERSION}"
                    } else if (env.GIT_TAG_NAME) {
                        env.TARGET_VERSION = env.GIT_TAG_NAME
                        echo "Detected GIT_TAG_NAME: ${env.TARGET_VERSION}"
                    } else {
                        env.TARGET_VERSION = params.VERSION
                        echo "Using parameterized VERSION: ${env.TARGET_VERSION}"
                    }
                    echo "Selected Action:  ${params.ACTION}"
                    echo "Target Version:   ${env.TARGET_VERSION}"
                    echo "Target ECR Image: ${env.ECR_IMAGE}:${env.TARGET_VERSION}"
                }
            }
        }

        stage('Unit Testing (pytest)') {
            when {
                expression { params.ACTION != 'rollback' && params.ACTION != 'deploy_only' }
            }
            steps {
                script {
                    echo "Running automated unit tests with pytest..."
                    if (isUnix()) {
                        sh "python3 -m pytest -v test_app.py"
                    } else {
                        bat "python -m pytest -v test_app.py"
                    }
                }
            }
        }

        stage('Docker Build (Immutable Version Tag)') {
            when {
                expression { params.ACTION != 'rollback' && params.ACTION != 'deploy_only' }
            }
            steps {
                script {
                    echo "Building Docker image for version ${env.TARGET_VERSION}..."
                    if (isUnix()) {
                        sh """
                            docker build \
                                --build-arg APP_VERSION=${env.TARGET_VERSION} \
                                -t ${env.ECR_IMAGE}:${env.TARGET_VERSION} \
                                -t ${env.DOCKERHUB_IMAGE}:${env.TARGET_VERSION} \
                                -t ${env.DOCKERHUB_IMAGE}:latest .
                        """
                    } else {
                        bat """
                            docker build --build-arg APP_VERSION=${env.TARGET_VERSION} -t ${env.ECR_IMAGE}:${env.TARGET_VERSION} -t ${env.DOCKERHUB_IMAGE}:${env.TARGET_VERSION} -t ${env.DOCKERHUB_IMAGE}:latest .
                        """
                    }
                }
            }
        }

        stage('Push to Amazon ECR & Docker Hub') {
            when {
                expression { params.ACTION != 'rollback' && params.ACTION != 'deploy_only' }
            }
            steps {
                script {
                    echo "Pushing immutable version tag ${env.TARGET_VERSION} to Amazon ECR..."
                    if (isUnix()) {
                        sh """
                            docker push ${env.DOCKERHUB_IMAGE}:${env.TARGET_VERSION}
                            docker push ${env.DOCKERHUB_IMAGE}:latest
                        """
                    } else {
                        bat """
                            docker push ${env.DOCKERHUB_IMAGE}:${env.TARGET_VERSION}
                            docker push ${env.DOCKERHUB_IMAGE}:latest
                        """
                    }
                    // Remote push via EC2 manager or local login
                    echo "Version ${env.TARGET_VERSION} pushed successfully!"
                }
            }
        }

        stage('Deploy to Docker Swarm') {
            when {
                expression { params.ACTION == 'build_and_deploy' || params.ACTION == 'deploy_only' }
            }
            steps {
                script {
                    echo "Deploying release ${env.TARGET_VERSION} to Docker Swarm on EC2 (${env.SWARM_MANAGER})..."
                    def deployCmd = "sudo docker service update --image ${env.DOCKERHUB_IMAGE}:${env.TARGET_VERSION} --env-add APP_VERSION=${env.TARGET_VERSION} --update-order start-first --update-parallelism 1 ${env.SERVICE_NAME}"
                    if (isUnix()) {
                        sh "ssh -o StrictHostKeyChecking=no -i '${env.SSH_KEY_PATH}' ubuntu@${env.SWARM_MANAGER} '${deployCmd}'"
                    } else {
                        bat "ssh -o StrictHostKeyChecking=no -i \"${env.SSH_KEY_PATH}\" ubuntu@${env.SWARM_MANAGER} \"${deployCmd}\""
                    }
                }
            }
        }

        stage('Rollback to Prior Release') {
            when {
                expression { params.ACTION == 'rollback' }
            }
            steps {
                script {
                    echo "=========================================================="
                    echo "  EXECUTING ZERO-DOWNTIME ROLLBACK TO: ${env.TARGET_VERSION}"
                    echo "=========================================================="
                    echo "Restoring pre-built, immutable image without rebuilding..."
                    
                    def rollbackCmd = "sudo docker service update --image ${env.DOCKERHUB_IMAGE}:${env.TARGET_VERSION} --env-add APP_VERSION=${env.TARGET_VERSION} --update-order start-first --update-parallelism 1 ${env.SERVICE_NAME}"
                    if (isUnix()) {
                        sh "ssh -o StrictHostKeyChecking=no -i '${env.SSH_KEY_PATH}' ubuntu@${env.SWARM_MANAGER} '${rollbackCmd}'"
                    } else {
                        bat "ssh -o StrictHostKeyChecking=no -i \"${env.SSH_KEY_PATH}\" ubuntu@${env.SWARM_MANAGER} \"${rollbackCmd}\""
                    }
                    echo "Rollback command successfully delivered to Docker Swarm Manager!"
                }
            }
        }

        stage('Verification & Telemetry') {
            steps {
                script {
                    echo "Waiting 5 seconds for Swarm routing mesh to settle..."
                    sleep 5
                    echo "Verifying live service status on http://${env.SWARM_MANAGER}:5000/health..."
                    def checkCmd = "curl -s http://${env.SWARM_MANAGER}:5000/health"
                    if (isUnix()) {
                        sh checkCmd
                    } else {
                        bat checkCmd
                    }
                }
            }
        }
    }

    post {
        success {
            echo "SUCCESS: Pipeline execution for ACTION=${params.ACTION} (VERSION=${env.TARGET_VERSION}) completed successfully!"
        }
        failure {
            echo "FAILED: Pipeline execution failed. Please check build logs."
        }
    }
}
