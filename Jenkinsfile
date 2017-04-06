pipeline {
  agent any
  stages {
    stage('Find path to bed') {
      steps {
        fileExists 'Path-to-sofa.png'
        timeout(time: 2, unit: 'SECONDS') {
          echo 'Hej jonas'
        }
        
      }
    }
  }
}