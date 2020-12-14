# axiom-cloudwatch-ingestor

## Table of Contents
- 

### Building:

1. go mod vendor
2. docker run -v $(PWD):/app -it golang bash
3. cd app/<sub-dir>
4. go build -o <name>
5. zip <name.zip> <name>

### Deployment:

Upload zip and set the following env varialbes:
```
AXIOM_AUTHKEY:	<axiom-auth-key>
AXIOM_DATASET:	<dataset-name>
AXIOM_URL: <axiom-url>
```
