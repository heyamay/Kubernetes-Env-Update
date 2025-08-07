pipeline {
    agent any
    stages {
        stage('Clone Repo') {
            steps {
                git url: 'https://github.com/heyamay/Kubernetes-Env-Update'
            }
        }
        stage('Update Env Vars') {
            steps {
                sh 'python3 update_env.py --cluster QualityEdge --namespace fb-13-oracle --service data-archival-engine --ticket 12345 --engineer "John Doe" --env_vars env_vars.json'
            }
        }
        stage('Commit Changes') {
            steps {
                sh '''
                git config --global user.email "you@example.com"
                git config --global user.name "Your Name"
                git add env_vars.json update_log.txt
                git commit -m "Updated env vars for ticket #12345 by John Doe" || echo "No changes to commit"
                git push origin main
                '''
            }
        }
    }
}

