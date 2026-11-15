# Jenkins CI/CD Cheat Sheet

> **Status:** Legacy reference — technical validation pending

A reference for Jenkins continuous integration and delivery (CI/CD) jobs, agents, Pipeline definitions, and build troubleshooting.

## Safety

Inspect the job configuration, source revision, and previous build before starting a run. Deployment stages can change production services; keep credentials in the configured credential store and review agent and plugin changes before applying them.

## Quick reference

### Introduction to Jenkins

Jenkins is an open-source automation server that enables developers to build, test, and deploy their software. It facilitates continuous integration and continuous delivery in software projects by automating various stages of the delivery process. Jenkins supports numerous plugins which extend its functionality for building, deploying, and automating across various platforms.

### Key Concepts

- **Job/Project**: The basic entity in Jenkins, representing a task or a series of tasks to be executed.

- **Build**: The process of executing a job/project.

- **Node/Agent**: A machine which is part of the Jenkins environment and is capable of executing jobs.

- **Executor**: A slot for execution in a node, determining how many jobs can run simultaneously on that node.

- **Workspace**: A directory on the node where Jenkins executes the build.

- **Pipeline**: A suite of jobs or a single job that defines the sequence of steps for continuous delivery.

- **Plugin**: An add-on that extends Jenkins' capabilities.

- **Jenkinsfile**: A text file containing the definition of a Jenkins Pipeline, typically checked into source control.

### Jenkins Operations

- **Starting Jenkins**
  - Typically, Jenkins runs as a standalone application in its own process with the built-in Java servlet container/application server (Jetty).

- **Accessing Jenkins**
  - Jenkins listens on port 8080 by default (`http://<jenkins-server>:8080`); production controllers should be reached over HTTPS through a reverse proxy or a configured TLS listener.

- **Creating a Job**
  - In Jenkins, jobs can be created through the web interface, typically by selecting "New Item", then choosing the job type.

- **Configuring a Job**
  - Each job can be configured with specific parameters, source control settings, build triggers, build steps, and post-build actions.

- **Running a Build**
  - A build can be triggered manually, by source control changes, or on a schedule.

- **Monitoring Build Results**
  - Jenkins provides detailed results on the web interface for each build, including console output, test results, and artifacts.

### Jenkins Pipeline

- **Pipeline Script**
  - Jenkins Pipeline uses a specific domain-specific language (DSL) for defining builds. This can be scripted in a `Jenkinsfile`.

- **Declarative vs. Scripted Pipeline Syntax**
  - Declarative Pipeline syntax is newer and provides a simpler and more readable syntax. Scripted Pipeline offers more flexibility and control.

- **Pipeline Stages**
  - Pipelines are typically divided into stages, such as Build, Test, and Deploy, each of which contains steps to execute.

- **Pipeline Steps**
  - Steps are individual tasks that execute commands, scripts, or actions.

- **Jenkinsfile Example**
  - A `Jenkinsfile` might look like this:
    ```groovy
    pipeline {
        agent any
        stages {
            stage('Build') {
                steps {
                    sh 'make build'
                }
            }
            stage('Test') {
                steps {
                    sh 'make test'
                }
            }
            stage('Deploy') {
                steps {
                    echo 'Deploy steps go here'
                }
            }
        }
    }
    ```
  - Every `steps` block needs at least one step; a block that holds only comments fails validation.

- **Validate a Jenkinsfile before committing**
  - Use the controller's declarative linter. Authenticate with a user API token, never a password:
    ```bash
    curl --user <user>:<api-token> -X POST \
      -F "jenkinsfile=<Jenkinsfile" \
      https://<jenkins-server>/pipeline-model-converter/validate
    ```

- **Replay and restart**
  - `Replay` reruns a build with an edited Pipeline script without a commit; `Restart from Stage` reruns a declarative Pipeline from a chosen top-level stage using the original inputs.

### Controller Maintenance Notes

- Jenkins releases as a weekly line and a Long-Term Support (LTS) line; use LTS for anything shared. Current releases require Java 17 or 21 on the controller and agents.
- Do not run builds on the built-in node; set its executors to 0 and use agents.
- Keep the controller URL behind TLS. The plain `http://<jenkins-server>:8080` listener is only the package default.
- Read the plugin's security advisories and take a `JENKINS_HOME` backup before updating plugins; plugin updates are the most common cause of a broken controller.
- Configuration as Code (JCasC) and the Job DSL or multibranch Pipelines keep controller and job configuration in source control.

### Advanced Features

- **Distributed Builds**
  - Jenkins can distribute build tasks across multiple nodes, enabling faster builds and tests.

- **Notifications**
  - Jenkins can notify stakeholders of build results through various means like email, Slack, etc.

- **Integration with Version Control Systems**
  - Jenkins integrates with systems like Git, Subversion, etc., to trigger builds on code changes.

- **Plugins**
  - Jenkins' functionality can be extended through plugins, which are available for a wide range of tools and platforms.

## Troubleshooting workflow

1. Confirm the job, failed stage, source revision, agent, and build number.
2. Inspect the build result, console output, queue, and agent availability before rerunning anything.
3. Collect timestamps, test results, and relevant controller and agent logs; redact credentials.
4. Compare the Jenkinsfile, parameters, credentials bindings, and plugin changes with the last successful run.
5. Correct the smallest affected job or agent setting and run a controlled build.
6. Verify the affected stage and downstream result; record the change and recovery configuration.

## Official references

- [Jenkins handbook](https://www.jenkins.io/doc/book/)
- [Pipeline documentation](https://www.jenkins.io/doc/book/pipeline/)
