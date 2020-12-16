package main

import (
	"context"
	"fmt"
	"os"
	"strings"

	// TODO(lukasmalkmus): Make sure we open-source them or make them part of
	// this project.
	"axicode.axiom.co/watchmakers/logmanager"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"

	"github.com/axiomhq/axiom-cloudwatch-lambda/parser"
	"github.com/axiomhq/axiom-cloudwatch-lambda/parser/eks"
	lambdaParser "github.com/axiomhq/axiom-cloudwatch-lambda/parser/lambda"
	"github.com/axiomhq/axiom-go/axiom"
)

var logger = logmanager.GetLogger("axiom.cloudwatch.aws-lambda")

func main() {
	lambda.Start(handler)
}

func handler(ctx context.Context, logsEvent events.CloudwatchLogsEvent) {
	data, _ := logsEvent.AWSLogs.Parse()
	if len(data.LogEvents) == 0 {
		return
	}

	events := make([]axiom.Event, 0, len(data.LogEvents))
	service, group, sgParsed := lambdaParser.ParseServiceGroup(data.LogGroup)

	for _, logEvent := range data.LogEvents {
		cw := map[string]interface{}{
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

		if dict["format"] != "json" && service != "" {
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
		ev["_time"] = logEvent.Timestamp

		events = append(events, ev)
	}

	if err := sendEvents(ctx, events); err != nil {
		_ = logger.Error("failed to send events: %s", err)
		os.Exit(-1)
	}
}

func sendEvents(ctx context.Context, events []axiom.Event) error {
	var (
		url     = os.Getenv("AXIOM_URL")
		authkey = os.Getenv("AXIOM_AUTHKEY")
		dataset = os.Getenv("AXIOM_DATASET")
	)

	client, err := axiom.NewClient(url, authkey)
	if err != nil {
		return err
	}

	res, err := client.Datasets.IngestEvents(ctx, dataset, axiom.IngestOptions{}, events...)
	if err != nil {
		return err
	}

	logger.Info(fmt.Sprintf("ingested %d of %d events into %q", res.Ingested, res.Failed, dataset))

	return nil
}
