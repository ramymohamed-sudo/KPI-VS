
// https://www.jenkins.io/doc/book/pipeline/

node{

    def commit_id 
    def customImage
    def ml_type

    stage('Preparation'){
        checkout scm
        sh 'git rev-parse --short HEAD > .git/commit-id'  
        commit_id = readFile('.git/commit-id').trim()
    }


    stage('Build'){

// Build from image        
//        def myTestContainer = docker.image('jupyter/scipy-notebook')
//         myTestContainer.pull()
//         myTestContainer.inside{
//              sh 'pip install joblib'
//              sh 'python3 train.py'
//         }

    // Build from Dockerfile  // from Dockerfile in "./"
    // customImage = docker.build("my-image:${env.BUILD_ID}", "./")    
    customImage = docker.build("ramyrr/machinelearning:${commit_id}", "./")  
    }
    
    stage('Run'){
        
        customImage.inside {
        sh 'ls'
        sh 'echo Hello KPI-Visualization System'
        sh 'python3 ./kpi_vs_class_10_5.py'

        
    }
    }


    // stage('Push'){
    //     docker.withRegistry('https://index.docker.io/v1/', '7ec5aa2d-ed10-4282-ba0a-527c27a55a11'){  
    //         // 'dockerhub'   replaced with '7ec5aa2d-ed10-4282-ba0a-527c27a55a11'
    //         // def app = docker.build("ramyrr/machinelearning:${commit_id}", '.').push()            
    //         customImage.push()

    //     }
    // }    
    
}


