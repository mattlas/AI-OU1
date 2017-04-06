pipeline {
  agent any
  stages {
    stage('Find path to bed') {
      steps {
        parallel(
          "Find path to bed": {
            fileExists 'Path-to-bed.json'
            
          },
          "Path to sofa": {
            fileExists 'Path-to-sofa.json'
            
          }
        )
      }
    }
  }
}