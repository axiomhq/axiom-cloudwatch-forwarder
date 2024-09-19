# Creation of subscriber and unsubscriber components


## Context

The Forwarder is responsible of creating subscriptions for itself,
and it only supports passing list of names of log groups. We want to provide
our customers with an easier way to subscribe and unsubscribe from log groups,
will being able to do this process repeatedly without affecting the Forwarder.


## Decision

- Rename `Backfill` to Subscriber
- The Subscriber is responsible for creating new Subscription Filters for the Forwarder
- A new component `Unsubscriber` is introduced to manage removing Subscription Filters
- Rename the log groups listener to just `Listener`, which will automatically creaate
  Subscription Filters for new log groups.
