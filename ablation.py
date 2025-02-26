import json
import re
from pathlib import Path
from types import SimpleNamespace

from datasets import load_dataset
from tqdm import tqdm

from client_pool import get_client, get_completion
from prompt_hub import get_prompts

# -----------------------------------------------------------------------------
# experiment arguments
ARGS = {
    "model_path": "gemma2-9b",  # "llama3-70b-8192",  # "llama3-8b-8192",  # "gemma2-9b-it",  # "gemma2-7b-it", # "gpt-4o-mini-2024-07-18",  # "gpt-3.5-turbo-0125"
    "output_dir": "result/abl/step3",
    "resumable": True,
    "task": "abl-step3",
    "shots": 3,
    "local": False,  # inference with local accelerator(GPU)
}
ARGS.update(
    get_prompts(ARGS["task"])
)  # make sure that prompt_tag is defined in prompts.json
print(ARGS)
args = SimpleNamespace(**ARGS)
# -----------------------------------------------------------------------------

client = get_client(args.model_path, local=args.local)

OUTPUT_PATH = (
    Path(f"{args.output_dir}") / f"{args.shots}shots" / args.model_path.split("/")[-1]
)
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# write config to file
with open(OUTPUT_PATH / "config.json", "w") as f:
    json.dump(vars(args), f, indent=4)

dataset = load_dataset("csv", data_files="data/" + f"{args.task}.csv", split="train")

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
    out = re.sub(r"```.*?\n(.*?)\n```", r"\1", out, flags=re.DOTALL)
    out = re.sub(r"```.*?\s(.*?)\s```", r"\1", out, flags=re.DOTALL)
    out = re.sub(r"<ans>(.*?)</ans>", r"\1", out, flags=re.DOTALL)
    return out


outputs = []
for data in tqdm(dataset):
    # -------------------------------------------------------------------------
    # reasoning process
    out = get_completion(
        client,
        model=args.model_path,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": ARGS[str(args.shots) + "shots_prompt"].format(
                    input=data["input"],
                    # obj=data["obj"],
                    # tar=data["tar"],
                ),
            },
        ],
        temperature=0,
        top_p=0.95,
        max_tokens=1024,
    )
    # -------------------------------------------------------------------------

    # print(out)
    cleaned_out = clean_output(out)
    outputs.append(cleaned_out)

    with open(OUTPUT_PATH / "outputs.txt", "a+") as f:
        f.write(cleaned_out.replace("\n", " ") + "\n")

    with open(OUTPUT_PATH / "labels.txt", "a+") as f:
        f.write(data["label"] + "\n")
