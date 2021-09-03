package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"os/signal"
	"strings"
	"syscall"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
	"github.com/axiomhq/axiom-go/axiom"
	"github.com/axiomhq/pkg/version"

	"github.com/axiomhq/axiom-cloudwatch-lambda/parser"
	"github.com/axiomhq/axiom-cloudwatch-lambda/parser/eks"
	lambdaParser "github.com/axiomhq/axiom-cloudwatch-lambda/parser/lambda"
)

const (
	exitOK int = iota
	exitConfig
)

func main() {
	os.Exit(Main())
}

func Main() int {
	// Export `AXIOM_TOKEN`, `AXIOM_ORG_ID` and `AXIOM_DATASET` for Axiom Cloud
	// Export `AXIOM_URL`, `AXIOM_TOKEN` and `AXIOM_DATASET` for Axiom Selfhost

	log.Print("starting axiom-cloudwatch-lambda version ", version.Release())

	ctx, cancel := signal.NotifyContext(context.Background(),
		os.Interrupt,
		os.Kill,
		syscall.SIGHUP,
		syscall.SIGINT,
		syscall.SIGQUIT,
	)
	defer cancel()

	dataset := os.Getenv("AXIOM_DATASET")
	if dataset == "" {
		log.Print("AXIOM_DATASET is required")
		return exitConfig
	}

	client, err := axiom.NewClient()
	if err != nil {
		log.Print(err)
		return exitConfig
	} else if err = client.ValidateCredentials(ctx); err != nil {
		log.Print(err)
		return exitConfig
	}

	lambda.StartWithContext(ctx, handler(client, dataset))

	return exitOK
}

func handler(client *axiom.Client, dataset string) func(context.Context, events.CloudwatchLogsEvent) error {
	return func(ctx context.Context, logsEvent events.CloudwatchLogsEvent) error {
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

		res, err := client.Datasets.IngestEvents(ctx, dataset, axiom.IngestOptions{}, events...)
		if err != nil {
			return fmt.Errorf("failed to send events: %w", err)
		}

		log.Printf("ingested %d of %d events into %q", res.Ingested, res.Failed, dataset)

		return nil
	}
}
