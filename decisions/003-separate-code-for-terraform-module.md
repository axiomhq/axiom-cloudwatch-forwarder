# Separate code for Terraform module


## Context

To build the Terraform module for the Subscriber we re-used the same python code that we had for the Cloudformation Stack. This didn't work as expected
because the `aws_lambda_invocation` resource sends a different data format
than the ones sent by Cloudformation.


### Differneces between Cloudformation and Terraform

- Cloudformation event is different from the one sent by the `aws_lambda_invocation` resource.
- Cloudformation sends requests when its being deleted, those requests needs to be handled so that the resources are deleted properly.

## Decision

- Separating the python code is the easiest choice in that case to avoid
complex and confusing bugs.
