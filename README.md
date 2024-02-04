# Intent Classifier


## Deploying the Classifier Service

The core classifier service is in the [`server`](./server) folder.
It's containerized and can be built using your favorite container tool.

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

There is a benchmarking client provided in the [`server`](./server) folder.
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



## Building the Model

See **[docs/README.md](docs/README.md)**


## Contributing

See **[CONTRIBUTING.md](CONTRIBUTING.md)**
