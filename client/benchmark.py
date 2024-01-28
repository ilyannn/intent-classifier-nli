#!/usr/bin/env python
import csv
import time
from collections import defaultdict
from dataclasses import dataclass
from multiprocessing import Pool

import click
import numpy as np
import requests

RETRY_SECONDS = 5
DEFAULT_JOBS = 4


@dataclass
class Intent:
    label: str


class IntentClassifierClient:
    def __init__(self, api_url):
        self.api_url = api_url

    def ready(self) -> bool:
        ready_url = self.api_url + "/ready"
        return requests.get(ready_url).status_code == 200

    def intents(self, text):
        intent_url = self.api_url + "/intent"
        response = requests.post(intent_url, json={"text": text})
        if response.status_code != 200:
            return None
        intents = response.json().get("intents")
        return [Intent(label=obj["label"]) for obj in intents]


def format_confusion(c):
    return click.style(f"{c:.02}", fg="green")


def format_error(s):
    return click.style(s, fg="red", bold=True)


def format_stream_name(stream):
    if hasattr(stream, "name"):
        return click.style(stream.name, fg="green", bold=True)
    return click.style(str(stream), fg="green")


def format_integer(n):
    return click.style(int(n), fg="cyan")


def format_ms(seconds):
    return click.style(int(seconds * 1000), fg="yellow") + "ms"


def format_percentage(p):
    return click.style(f"{100 * p:.2f}", fg="green") + "%"


def format_query(query):
    return click.style(query, dim=True)


def format_s(seconds):
    return (
        click.style(
            f"{seconds:.1f}" if seconds != int(seconds) else seconds, fg="yellow"
        )
        + "s"
    )


def format_dim(s):
    return click.style(s, dim=True)


def format_url(url):
    return click.style(url, fg="blue", underline=True)


def f1_score(tp, fp, fn):
    assert tp or fn or fp
    return 2 * tp / (2 * tp + fn + fp)


def f1_scores(confusion_matrix):
    tp = defaultdict(float)
    fn = defaultdict(float)
    fp = defaultdict(float)
    all_labels = set(confusion_matrix)

    for actual, row in confusion_matrix.items():
        for predicted, value in row.items():
            all_labels.add(predicted)
            if predicted == actual:
                tp[actual] = value
            else:
                fp[actual] += value
                fn[predicted] += value

    return [
        (lb, tp[lb], fn[lb], fp[lb], f1_score(tp[lb], fn[lb], fp[lb]))
        for lb in sorted(all_labels)
    ]


def _get_intent(client, query, correct_label):
    """Perform a request and return the result is correct as well as request time"""
    start_time = time.time()
    intents = client.intents(query)
    return intents[0].label, correct_label, query, time.time() - start_time


@click.command()
@click.argument("tsv_file", type=click.File())
@click.option(
    "-u",
    "--url",
    required=True,
    help="Base URL for the intents API",
)
@click.option(
    "-j",
    "--jobs",
    type=int,
    default=DEFAULT_JOBS,
    show_default=True,
    help="The number of requests to run in parallel",
)
@click.option(
    "-o",
    "--output",
    type=click.File("w"),
    show_default=True,
    help="Output errors in TSV format (- for stdout)",
)
def benchmark(tsv_file, url: str, jobs: int, output):
    click.echo(f"Using base URL: {format_url(url)}")
    client = IntentClassifierClient(url)

    while not client.ready():
        message = format_dim(
            f"API is not ready, will retry in {RETRY_SECONDS} seconds..."
        )
        click.echo(message)
        time.sleep(RETRY_SECONDS)

    data = list(csv.reader(tsv_file, delimiter="\t"))
    total = len(data)
    click.echo(
        f"Read {format_integer(total)} lines from {format_stream_name(tsv_file)}"
    )
    if not total:
        click.echo(format_error("No test data found"))
        return 1

    stats = defaultdict(int)
    confusion = defaultdict(lambda: defaultdict(int))
    incorrect_lines = []
    all_labels = {label for _, label in data}
    req_times = []
    start_time = time.time()

    with click.progressbar(length=total) as progress:

        def success(result):
            model_label, correct_label, query, req_time = result
            stats[model_label == correct_label] += 1
            all_labels.add(model_label)
            confusion[correct_label][model_label] += 1
            req_times.append(req_time)
            if correct_label != model_label:
                incorrect_lines.append((model_label, correct_label, query))
            progress.update(1)

        def failure(_):
            stats[None] += 1
            progress.update(1)

        with Pool(jobs) as pool:
            for datum in data:
                _ = pool.apply_async(
                    _get_intent,
                    (client, *datum),
                    callback=success,
                    error_callback=failure,
                )
            pool.close()
            pool.join()

        progress.finish()

    time_taken = time.time() - start_time
    assert total == sum(stats.values())
    accuracy = stats[True] / total

    # Displaying statistics about stats and req_times
    f_correct, f_incorrect, f_failed = (
        format_integer(stats[key]) for key in (True, False, None)
    )

    def p_95(array):
        np.percentile(array, 95)

    f_min, f_max, f_avg, f_med, f_std, f_95 = (
        format_ms(f(req_times))
        for f in (np.min, np.max, np.mean, np.median, np.std, p_95)
    )

    f_rps = format_integer(total / time_taken)

    f_statistics = f"""
Request time: min {f_min}, max {f_max}, avg {f_avg} ± {f_std}, 50% {f_med}, 95% {f_95}
Real time elapsed: {format_s(time_taken)} ({f_rps} requests per second)

Received {f_correct} correct and {f_incorrect} incorrect answers ({f_failed} failed)
Accuracy: {format_percentage(accuracy)}

F1 scores for each class:
""" + "\n".join(
        f"  {label} ({', '.join(map(format_integer, nums))}): {format_confusion(value)}"
        for label, *nums, value in f1_scores(confusion)
    )

    click.echo(f_statistics)
    click.echo()

    if output:
        click.echo(f"Incorrect answers to be written to {format_stream_name(output)}")
        for model_label, correct_label, query in incorrect_lines:
            click.echo(
                "\t".join(
                    (format_error(model_label), correct_label, format_query(query))
                ),
                file=output,
            )
    return 0


if __name__ == "__main__":
    benchmark(auto_envvar_prefix="INTENTS_")  # pylint: disable=E1120,E1123
