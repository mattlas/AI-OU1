pipeline {
  agent any
  stages {
    stage('Find path to bed') {
      steps {
        fileExists 'Path-to-bed.json'
        fileExists 'Path-to-sofa.png'
      }
    }
  }
}