import json
from pathlib import Path
from types import SimpleNamespace

from datasets import load_dataset
from tqdm import tqdm

from client_pool import get_client, get_completion
from prompt_hub import get_prompts

# -----------------------------------------------------------------------------
# experiment arguments
ARGS = {
    "model_path": "gpt-4o-mini-2024-07-18",  # supported_models = ["llama3-8b-8192", "gemma2-9b-it", "gpt-4o-mini-2024-07-18", "gpt-3.5-turbo-0125"]
    "task": "ins_char",
    "max_new_tokens": 150,
    "output_dir": "result/CAD",
    "testing_dataset_range": (0, 1000),
    "resumable": True,
}
ARGS.update(
    get_prompts(ARGS["task"] if "_rand" not in ARGS["task"] else ARGS["task"][:-5])
)  # make sure that ARGS["task"] is defined in prompts.json
print(ARGS)
args = SimpleNamespace(**ARGS)
# -----------------------------------------------------------------------------

client = get_client(args.model_path)

OUTPUT_PATH = Path(f"{args.output_dir}") / args.task / args.model_path.split("/")[-1]
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# write config to file
with open(OUTPUT_PATH / "config.json", "w") as f:
    json.dump(vars(args), f, indent=4)

dataset = load_dataset(
    "csv", data_files=f"./data/{args.task}.tsv", split="train", sep="\t"
)

if args.resumable:
    labels_file = OUTPUT_PATH / "labels.txt"
    if labels_file.exists():
        # read existing progress
        with open(labels_file, "r") as f:
            progress = len(f.readlines())
        # resume working on the rest data samples
        dataset = dataset.select(range(progress, len(dataset)))


# tool function to extract clean output as final answer
def clean_output(out):
    try:
        out = out.strip()
        out = out.split("Answer:")[-1]
        out = out.split("<s>")[0]
        out = out.split('"')[1] if '"' in out else out
        out = out.split("'")[1] if "'" in out else out
        return out
    except Exception:
        # something wasn't generated properly, discard
        return ""


outputs = []
for data in tqdm(dataset):
    # -------------------------------------------------------------------------
    # reasoning process
    seq = get_completion(
        client,
        model=args.model_path,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": args.step1_prompt.format(input_string=data["input3"]),
            },
        ],
        temperature=0,
        top_p=0.95,
        max_tokens=args.max_new_tokens,
    )

    updated_seq = get_completion(
        client,
        model=args.model_path,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": args.step2_prompt.format(
                    obj=data["input2"], ist=data["input1"], sequence=seq
                ),
            },
        ],
        temperature=0,
        top_p=0.95,
        max_tokens=args.max_new_tokens,
    )

    out = get_completion(
        client,
        model=args.model_path,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": args.step3_prompt.format(sequence=updated_seq),
            },
        ],
        temperature=0,
        top_p=0.95,
        max_tokens=1024,  # reasoning process requires more tokens
    )
    # -------------------------------------------------------------------------

    # cleaned_out = clean_output(out)
    cleaned_out = out.split("<ans>")[-1].split("</ans>")[0]

    outputs.append(cleaned_out)

    # write outputs and labels to file
    with open(OUTPUT_PATH / "raw_outputs.txt", "a+") as f:
        f.write(updated_seq.replace("\n", " ") + "\n")

    with open(OUTPUT_PATH / "outputs.txt", "a+") as f:
        f.write(cleaned_out.replace("\n", " ") + "\n")

    with open(OUTPUT_PATH / "labels.txt", "a+") as f:
        f.write(data["label"] + "\n")
