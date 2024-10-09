terraform {
  required_providers {
    axiom = {
      source  = "axiomhq/axiom"
      version = "1.1.2"
    }
  }
}

provider "axiom" {
  api_token = ""
}
