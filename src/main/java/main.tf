terraform {
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
    }
  }
}
# This is a single-line comment
provider "local" {}

resource "local_file" "example" {
  filename = "hello.txt"
  content  = "Hello, Terraform!"
}
