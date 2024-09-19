# Separate code for Terraform module


## Context

To build the Terraform module for the Subscriber we re-used the same
python code that we had for the Cloudformation Stack. This didn't work as expected
because the `aws_lambda_invocation` resource sends a different data format
than the ones sent by Cloudformation.


## Decision

- Separating the python code is the easiest choice in that case to avoid
complex and confusing bugs.
