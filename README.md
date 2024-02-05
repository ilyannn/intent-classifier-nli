# Intent Classifier

## Deploying the Classifier Service

The core classifier service is located in the [`server`](./server) folder.
The preferred method of running is containerized using your favorite container tool.

### In a Container

An example invocation to run the service locally
is in the [`justfile`](justfile) and can be run with something like

```shell
# modify container_tool variable if the file if you use Docker
just serve 8080
```

if you have the **[just](https://github.com/casey/just)** tool installed.

### Local Testing

Alternatively, the script [`server/server.py`](server/server.py) can be run
directly from an appropriate Python environment
(it can be set up from [`server/requirements.txt`](server/requirements.txt))

### Cloud Instance

The demo version of the classifier is deployed to my personal cluster at
**[intents.cluster.megaver.se](https://intents.cluster.megaver.se)**.
It's an economically built cluster, so the performance isn't great, but you can
test it with a request tool of your choice.

The Kubernetes manifest for deploying the service is shown on **[docs.cluster.megaver.se](https://docs.cluster.megaver.se/cluster/automatic/apps/intent-classifier.yaml)**

## Accessing the Classifier Service

### Benchmarking Client

There is a benchmarking client provided in the [`client`](./client) folder.
It computes the average accuracy and F1 scores for the label classes.
You can invoke it on the test part of the ATIS dataset with

```shell
# pip install -r client/requirements.txt -- if necessary
just benchmark
```

### API Access

In addition to the provided requirements regarding the `/version` and `/predict`
endpoints there are the following features implemented:

1. The `/predict` endpoint accepts the `requested_model` key that can select a specific model. Several models can be specified on the command line or using the `MODEL` environment variable. The first model is the default one.
2. A separate endpoint `/info` returns information about the service.

## Testing Results

We run the local benchmark as discussed above:

![local-benchmark-atis-test-1.0-10ep.png](docs/assets/local-benchmark-atis-test-1.0-10ep.png)

The model obtains the accuracy of almost 98% on the test data.
Among the 18 [model errors](docs/assets/local-benchmark-atis-test-1.0-10ep.errors.tsv) we have

- 2 rows with the unknown label `day_name`
- 1 row that seems to be correctly classified by our model as `airfare`
- 1 row that seems to be correctly classified by our model as `flight+airfare`
- 5 rows that seem to be correctly classified by our model as `quantity`
- 6 rows where `flight` and `flight+airfare` are mixed up
- 1 row similarly about `flight_no`
- 1 cut-off phrase
- 1 genuine mistake (`airport` instead of a `flight`)

Overall, we are quite happy about the model's performance.

## Building the Model

See **[docs/README.md](docs/README.md)**

## Contributing

See **[CONTRIBUTING.md](CONTRIBUTING.md)**
