pipeline {
  agent any
  stages {
    stage('Find path to bed') {
      steps {
        fileExists 'Path-to-sofa.png'
        timeout(time: 1, unit: 'NANOSECONDS')
      }
    }
  }
}