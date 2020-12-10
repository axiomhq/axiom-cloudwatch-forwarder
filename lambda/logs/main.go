package main

import (
	"context"
	"fmt"
	"io/ioutil"
	"os"
	"strings"

	acLambda "axicode.axiom.co/watchmakers/axiom-cloudwatch-lambda/lambda"
	"axicode.axiom.co/watchmakers/axiomdb/client"
	"axicode.axiom.co/watchmakers/axiomdb/core/common"
	proxy "axicode.axiom.co/watchmakers/go-lambda-proxy"
	"axicode.axiom.co/watchmakers/logmanager"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
)

var (
	logger = logmanager.GetLogger("axiom.cloudwatch.aws-lambda")
	once   = &common.OnceErr{}

	// adapter is created on cold-start and re-used afterwards.
	adapter *proxy.Adapter
)

func main() {
	lambda.Start(handler)
}

func handler(ctx context.Context, logsEvent events.CloudwatchLogsEvent) {
	data, _ := logsEvent.AWSLogs.Parse()
	if len(data.LogEvents) == 0 {
		return
	}

	events := make([]map[string]interface{}, 0, len(data.LogEvents))
	service, group, sgParsed := acLambda.ParseServiceGroup(data.LogGroup)

	for _, logEvent := range data.LogEvents {
		cw := map[string]interface{}{
			"id":      logEvent.ID,
			"group":   data.LogGroup,
			"stream":  data.LogStream,
			"type":    data.MessageType,
			"owner":   data.Owner,
			"message": logEvent.Message,
		}
		if sgParsed {
			cw["service"] = service
			cw["group_name"] = group
		}

		data, typ, err := acLambda.MatchMessage(logEvent.Message)
		if err != nil && err != acLambda.ErrNotParsable {
			logger.Error("%v", err)
		}
		cw["format"] = typ

		ev := map[string]interface{}{}
		for k, v := range data {
			if !strings.HasPrefix(k, "cloudwatch.") && k != "cloudwatch" {
				ev[k] = v
			}
		}
		ev["cloudwatch"] = cw
		ev["_time"] = logEvent.Timestamp
		events = append(events, ev)
	}

	if err := sendEvents(ctx, events); err != nil {
		logger.Error("%v", err)
		os.Exit(-1)
	}

	return
}

func sendEvents(ctx context.Context, events []map[string]interface{}) error {
	var (
		url     = os.Getenv("AXIOM_URL")
		authkey = os.Getenv("AXIOM_AUTHKEY")
		dataset = os.Getenv("AXIOM_DATASET")
	)

	axiClient, err := client.NewClient(url)
	if err != nil {
		return err
	}

	req, err := axiClient.Datasets.NewIngestEventsRequest(ctx, dataset, client.IngestOptions{}, events...)
	if err != nil {
		return err
	}

	if authkey != "" {
		req.Header.Set("Authorization", "Bearer "+authkey)
	}

	resp, err := axiClient.Do(req)
	if err != nil {
		logger.Error("error sending request: %s", err)
		return err
	}

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		return err
	}

	logger.Info(fmt.Sprintf("\ndataset %v:\n%s\n%s", dataset, resp.Status, string(body)))
	return nil
}
