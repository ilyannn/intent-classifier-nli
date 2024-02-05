#!/usr/bin/env python
import csv
import time
from collections import defaultdict
from dataclasses import dataclass
from multiprocessing import Pool
from typing import Union

import click
import numpy as np
import requests

DEFAULT_JOBS = 4
RETRY_SECONDS = 5


@dataclass
class Intent:
    label: str


class IntentClassifierClient:
    def __init__(self, api_url):
        self.api_url = api_url

    def ready(self) -> bool:
        ready_url = self.api_url + "/ready"
        try:
            return requests.get(ready_url).status_code == 200
        except requests.exceptions.ConnectionError:
            return False

    def info(self) -> dict:
        return requests.get(self.api_url + "/info").json()

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


def format_f1_scores(scores: list[tuple[str, int, int, int, float]]):
    return "\n".join(
        f"  {label} ({', '.join(map(format_integer, nums))}): {format_confusion(value)}"
        for label, *nums, value in scores
    )


def format_stream(stream):
    if hasattr(stream, "name"):
        return click.style(stream.name, fg="green", bold=True)
    return click.style(str(stream), fg="green")


def format_integer(n):
    return click.style(int(n), fg="cyan")


def format_model_info(info, model_index):
    model = info["models"][model_index]
    s_name = click.style(model["name"], fg="white", bold=True)
    s_path = format_stream(model["path"])
    if version := info["version"]:
        s_version = " (version {})".format(click.style(version, fg="cyan"))
    else:
        s_version = ""

    return f"{s_name} using {s_path}{s_version}"


def format_ms(seconds):
    return click.style(int(seconds * 1000), fg="yellow") + "ms"


def format_percentage(p):
    return click.style(f"{100 * p:.2f}", fg="green") + "%"


def format_query(query):
    return click.style(query, dim=True)


def format_seconds(s):
    return click.style(f"{s:.1f}" if s != int(s) else s, fg="yellow") + "s"


def format_dim(value):
    return click.style(value, dim=True)


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

    scores = [
        (lb, tp[lb], fn[lb], fp[lb], f1_score(tp[lb], fn[lb], fp[lb]))
        for lb in sorted(all_labels)
    ]

    def gen_average():
        yield "AVERAGE", len(scores), sum(s[-1] for s in scores) / len(scores)

    return scores + list(gen_average())


def _get_intent(client, query, correct_label):
    """Perform a request and return the result as well as request metadata"""
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
    "-m",
    "--model-index",
    type=int,
    default=0,
    help="Model index for the intents API",
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
def benchmark(tsv_file, url: str, jobs: int, model_index: int, output):
    click.echo(f"Using base URL: {format_url(url)}")
    client = IntentClassifierClient(url)

    while not client.ready():
        message = f"API is not ready, will retry in {RETRY_SECONDS} seconds..."
        click.echo(format_dim(message))
        time.sleep(RETRY_SECONDS)

    click.echo(format_model_info(client.info(), model_index))

    data = list(csv.reader(tsv_file, delimiter="\t"))
    total = len(data)
    click.echo(f"Read {format_integer(total)} lines from {format_stream(tsv_file)}")
    if not total:
        click.echo(format_error("No test data found"))
        return 1

    stats: dict[Union[bool, None], int] = defaultdict(int)
    confusion: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    incorrect_lines = []
    req_times = []
    start_time = time.time()

    with click.progressbar(length=total) as progress:

        def success(result):
            model_label, correct_label, query, req_time = result
            stats[model_label == correct_label] += 1
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
        return np.percentile(array, 95)

    f_min, f_max, f_avg, f_med, f_std, f_95 = (
        format_ms(f(req_times))
        for f in (np.min, np.max, np.mean, np.median, np.std, p_95)
    )

    f_rps = format_integer(total / time_taken)

    f_statistics = f"""
Request time: min {f_min}, max {f_max}, avg {f_avg} ± {f_std}, 50% {f_med}, 95% {f_95}
Real time elapsed: {format_seconds(time_taken)} ({f_rps} requests per second)

Received {f_correct} correct and {f_incorrect} incorrect answers ({f_failed} failed)
Accuracy: {format_percentage(accuracy)}

F1 scores for each class:
""" + format_f1_scores(
        f1_scores(confusion)
    )

    click.echo(f_statistics)
    click.echo()

    if output:
        click.echo(f"Incorrect answers to be written to {format_stream(output)}")
        for ml, cl, q in incorrect_lines:
            click.echo(
                "\t".join((format_error(ml), cl, format_query(q))),
                file=output,
            )
    return 0


if __name__ == "__main__":
    benchmark(auto_envvar_prefix="INTENTS_")  # pylint: disable=E1120,E1123
