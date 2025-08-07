pipeline {
    agent any
    stages {
        stage('Clone Repo') {
            steps {
                git url: '<azure_devops_repo_url>', credentialsId: '<azure_devops_credentials>'
            }
        }
        stage('Update Env Vars') {
            steps {
                sh 'python update_env.py --cluster QualityEdge --namespace fb-13-oracle --service data-archival-engine --ticket 12345 --engineer "John Doe" --env_vars env_vars.json'
            }
        }
        stage('Commit Changes') {
            steps {
                sh '''
                git add env_vars.json update_log.txt
                git commit -m "Updated env vars for ticket #12345 by John Doe"
                git push origin main
                '''
            }
        }
    }
}
