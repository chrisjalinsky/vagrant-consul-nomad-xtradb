job "solar-nginx" {
  
    region = "galaxy"
    datacenters = ["solarsystem"]
    type = "service"

    update {
        stagger = "5s"
        max_parallel = 1
    }

    group "nginxs" {
        count = 1
        restart {
            attempts = 3
            delay = "10s"
            interval = "1h"
            mode = "fail"
        }

        task "nginx" {
            driver = "exec"
            config {
                command = "/etc/init.d/nginx"
                args = ["start"]
            }
            
            service {
                name = "${BASE}-http1"
                port = "http1"
                check {
                    type = "tcp"
                    interval = "10s"
                    timeout = "2s"
                }
            }
            
            service {
                name = "${BASE}-http2"
                port = "http2"
                check {
                    type = "tcp"
                    interval = "10s"
                    timeout = "2s"
                }
            }

            env {
                EXAMPLE_VAR = "ThisIsAnArbitraryEnvironmentVariable"
            }

            resources {
                cpu = 500	#MHz
                memory = 512	#2048 MB RAM
                network {
                    mbits = 1
                    port "http1" {}
                    port "http2" {}
                }
            }
        }
    }
}
