terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}
#sample
provider "local" {}

resource "local_file" "example" {
  filename = "hello.txt"
  content  = "Hello, Terraform!"
}
