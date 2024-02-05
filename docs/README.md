# Building the Entailment Model

## Model Training

The process is documented in the Jupyter notebooks in this folder:

  - In **[analysis.ipynb](analysis.ipynb)** we build some simple decision tree models for the problem which provide baseline accuracy of about 90%
  - In **[analysis2.ipynb](analysis2.ipynb)** we implement F1 scores that allow us to go deeper than the accuracy metrics and test some simple predictors with not very satisfactory results
  - In **[analysis3.ipynb](analysis3.ipynb)** we use the HuggingFace zero-short classification pipeline as-is, but do not get good performance on our validation set, even using the 400m parameters model
  - In **[analysis4.ipynb](analysis4.ipynb)** we add some smaller models, bringing the total number to 5 (see the model structure in **[analysis4-models.md](analysis4-models.md)**) and start using custom hypotheses instead of standard ones
  - In **[analysis5.ipynb](analysis5.ipynb)** we fine-tune the smallest 12-million-parameter model **[MoritzLaurer/xtremedistil-l6-h256-zeroshot-v1.1-all-33](https://huggingface.co/MoritzLaurer/xtremedistil-l6-h256-zeroshot-v1.1-all-33)** on our dataset and export it as [the _ml-xtremedistil-l6-h256-in-tune-1.0-10ep_ model](../server/models/ml-xtremedistil-l6-h256-in-tune-1.0-10ep)


The relevant training arguments were as follows:

        num_train_epochs = 10,             # Total number of training epochs
        per_device_train_batch_size = 128, # Batch size per device during training
        per_device_eval_batch_size = 256,  # Batch size for evaluation
        warmup_steps = 500,                # Number of warmup steps for learning rate scheduler
        weight_decay = 0.01,               # Strength of weight decay
        lr_scheduler_type="inverse_sqrt",
        save_strategy='epoch',

## Model Structure

To perform the inference, we need the following data:
 
  - our finetuned model
  - tokenizer (which we did not change)
  - list of possible labels, including multilabels like `flight+airfare`
  - list of base labels, like `flight` and `airfare`
  - [list of hypotheses for each base label](../server/models/ml-xtremedistil-l6-h256-in-tune-1.0-10ep/base_labels.tsv)

We use custom hypotheses, for example 

> This example asks for a rental car or taxi price

instead of standard

> This example is about ground_fare


To improve the performance, we only perform inference on base labels and combine them
into multiclass labels (the "probability" of a multiclass label is computed as a 
sum of base label probabilities with a penalty).

We return top 3 label choices, provided their probability is above the 0.2 threshold.
However,
for the train and test set the probability is usually close to 1 for single-class labels
which reflects their relative simplicity.


## Considerations

We have considered how to simplify model deployment for the new set of intents.
In the simplest case intents can be added directly to [`labels.txt`]((../server/models/ml-xtremedistil-l6-h256-in-tune-1.0-10ep/labels.txt)) and [`base_labels.tsv`](../server/models/ml-xtremedistil-l6-h256-in-tune-1.0-10ep/base_labels.tsv).
If that is not sufficient, a similar fine-tuning procedure can be performed.

The A/B testing or blue/green deployment strategies are made easier by the ability of the service to dynamically switch models.


## References:

Articles:

  - [Zero-Shot Learning in Modern NLP (blog post)](https://joeddav.github.io/blog/2020/05/29/ZSL.html)
  - [Finetuning Hugging Face Facebook Bart Model (Medium post)](https://medium.com/@lidores98/finetuning-huggingface-facebook-bart-model-2c758472e340)
  - [How to finetune a zero-shot model for text classification (Stack Overflow)](https://stackoverflow.com/a/76213874)
  - [Fine-tuning BERT-NLI (summer school by Moritz Laurer)](https://github.com/MoritzLaurer/summer-school-transformers-2023/blob/main/4_tune_bert_nli.ipynb)

HuggingFace:

  - [Fine-tune a pretrained model (docs)](https://huggingface.co/docs/transformers/main/en/training)
  - [Zero-Shot Classification Pipeline (source)](src/transformers/pipelines/zero_shot_classification.py)

arXiv:

  - [[1909.00161] Benchmarking Zero-shot Text Classification: Datasets, Evaluation and Entailment Approach](https://arxiv.org/abs/1909.00161)
