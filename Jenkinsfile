#!groovy

pipeline {
	   agent {
          label "puppet-test-server"
	   }

      parameters {
       booleanParam(defaultValue: false, description: 'Nuke the docker image', name: 'DROP_DOCKER_IMAGES')
       string(name: 'DOCKER_IMAGE_NAME', defaultValue: 'catalogtest-puppet4-test', description: 'A defined image with a specific puppet release')
      }

      options{
         buildDiscarder(logRotator(artifactDaysToKeepStr: '10', artifactNumToKeepStr: '10', daysToKeepStr: '3', numToKeepStr: '20'))
      }

      stages {
              stage('Preparing Docker Image') {
                     steps {
                        checkout scm
                        ansiColor('xterm') {
                           sh """
                           cd ${WORKSPACE}/
                           if [ "${DROP_DOCKER_IMAGES}" = "true" ];then
                              docker images|grep -q "ubuntu:16.04" && docker rmi ubuntu:16.04
                              docker images|grep -q "${DOCKER_IMAGE_NAME}" && docker rmi -f ${DOCKER_IMAGE_NAME}
                           fi
                           sudo /usr/local/sbin/docker-gc
                           docker build -t ${DOCKER_IMAGE_NAME} .
                           """
                        }
                     }
              }
              stage('Test Catalog Testing Tool') {
                     steps {
                         sh """
                         cd ${WORKSPACE}/
								 mkdir -p ${WORKSPACE}/results/junit/ ${WORKSPACE}/results/coverage
                         docker run -v ${WORKSPACE}/:/tmp/catalog-tests/puppet-catalog-check/ -t ${DOCKER_IMAGE_NAME} nosetests3 -w /tmp/catalog-tests/puppet-catalog-check/ --with-xunit --xunit-file=/tmp/catalog-tests/puppet-catalog-check/results/junit/xunit.xml --with-coverage --cover-html --cover-html-dir=/tmp/catalog-tests/puppet-catalog-check/results/coverage --cover-package=catalogtests -s
                         """
                     }
              }

      }
      post  {
         always {
           archiveArtifacts "results/junit/*.xml"
           archiveArtifacts "results/coverage/*"
           junit "results/junit/*.xml"
           publishHTML (target: [
               allowMissing: false,
               alwaysLinkToLastBuild: true,
               keepAll: true,
               reportDir: 'results/coverage/',
               reportFiles: 'index.html',
               reportName: "Coverage Report"
             ])

         }
      }
}

