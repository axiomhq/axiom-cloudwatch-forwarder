package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"strings"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/axiomhq/axiom-go/axiom"
	"github.com/axiomhq/pkg/version"

	"github.com/axiomhq/axiom-cloudwatch-lambda/parser"
	"github.com/axiomhq/axiom-cloudwatch-lambda/parser/eks"
	lambdaParser "github.com/axiomhq/axiom-cloudwatch-lambda/parser/lambda"
)

var (
	deploymentURL = os.Getenv("AXIOM_DEPLOYMENT_URL")
	accessToken   = os.Getenv("AXIOM_ACCESS_TOKEN")
	dataset       = os.Getenv("AXIOM_DATASET")
)

func main() {
	log.Print("starting axiom-cloudwatch-lambda version ", version.Release())

	if deploymentURL == "" {
		log.Fatal("missing AXIOM_DEPLOYMENT_URL")
	}
	if accessToken == "" {
		log.Fatal("missing AXIOM_ACCESS_TOKEN")
	}
	if dataset == "" {
		log.Fatal("missing AXIOM_DATASET")
	}

	lambda.Start(handler)
}

func handler(ctx context.Context, logsEvent events.CloudwatchLogsEvent) error {
	data, _ := logsEvent.AWSLogs.Parse()
	if len(data.LogEvents) == 0 {
		return nil
	}

	events := make([]axiom.Event, 0, len(data.LogEvents))

	service, group, sgParsed := lambdaParser.ParseServiceGroup(data.LogGroup)

	for _, logEvent := range data.LogEvents {
		cw := map[string]string{
			"id":     logEvent.ID,
			"group":  data.LogGroup,
			"stream": data.LogStream,
			"type":   data.MessageType,
			"owner":  data.Owner,
		}
		if sgParsed {
			cw["service"] = service
			cw["group_name"] = group
		}

		var dict map[string]interface{}
		switch cw["service"] {
		case "lambda":
			dict, cw["format"] = lambdaParser.MatchMessage(logEvent.Message)
		case "eks":
			dict, cw["format"] = eks.MatchMessage(data.LogStream, logEvent.Message)
		default:
			dict, cw["format"] = parser.MatchUnknownMessage(logEvent.Message)
		}

		if dict["format"] != parser.FormatJSON && service != "" {
			dict = map[string]interface{}{
				service: dict,
			}
		}

		ev := axiom.Event{}
		for k, v := range dict {
			if !strings.HasPrefix(k, "cloudwatch.") && k != "cloudwatch" {
				ev[k] = v
			}
		}

		ev["cloudwatch"] = cw
		ev[axiom.TimestampField] = logEvent.Timestamp

		events = append(events, ev)
	}

	if err := sendEvents(ctx, events); err != nil {
		return fmt.Errorf("failed to send events: %w", err)
	}

	return nil
}

func sendEvents(ctx context.Context, events []axiom.Event) error {
	client, err := axiom.NewClient(deploymentURL, accessToken)
	if err != nil {
		return err
	}

	res, err := client.Datasets.IngestEvents(ctx, dataset, axiom.IngestOptions{}, events...)
	if err != nil {
		return err
	}

	log.Printf("ingested %d of %d events into %q", res.Ingested, res.Failed, dataset)

	return nil
}
