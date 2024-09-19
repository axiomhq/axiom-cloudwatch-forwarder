# Rename Ingestoer to Forwarder


## Context

The `Ingester` is used to ship/forward the logs from CloudWatch to Axiom.
Ingesting is not the correct wording for the process and we wanted to come up
with another name that better explains the process.


## Decision

After studying the topic with the Product team a decision was made to use
`Forwarder` instead as it implies forwarding logs from CW => Axiom.
