# Define a job called my-service
job "my-service" {
    # Job should run in the US region
    region = "galaxy"

    # Spread tasks between us-west-1 and us-east-1
    datacenters = ["solarsystem"]

    # run this job globally
    type = "system"

    # Rolling updates should be sequential
    update {
        stagger = "30s"
        max_parallel = 1
    }

    group "webs" {
        # We want 5 web servers
        count = 5

        # Create a web front end using a docker image
        task "frontend" {
            driver = "docker"
            config {
                image = "hashicorp/web-frontend"
            }
            service {
                port = "http"
                check {
                    type = "http"
                    path = "/health"
                    interval = "10s"
                    timeout = "2s"
                }
            }
            env {
                DB_HOST = "client1.mountain"
                DB_USER = "cj"
                DB_PASSWORD = "pw"
            }
            resources {
                cpu = 500
                memory = 128
                network {
                    # mbits = 100
                    # Request for a dynamic port
                    port "http" {
                    }
                    # Request for a static port
                    port "https" {
                        static = 443
                    }
                }
            }
        }
    }
}