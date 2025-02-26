import json
from pathlib import Path
from types import SimpleNamespace

from datasets import load_dataset
from tqdm import tqdm

from client_pool import get_client

# -----------------------------------------------------------------------------
# experiment arguments
ARGS = {
    "model_path": "llama3-8b-8192",  # "llama3-70b-8192",  # "llama3-8b-8192",  # "gemma2-9b-it",  # "gpt-4o-mini-2024-07-18",  # "gpt-3.5-turbo-0125"
    "task": "sub_char",
    "baseline": "1s",
    "output_dir": "result/1s",
    "max_new_tokens": 1024,
    "testing_dataset_range": (0, 1000),
    "resume": False,
    "del_char_1s_prompt": 'Delete every instance of a specified letter in a given word, based on the following examples:\n\
            \n\
            e.g.: Delete every instance of "a" in "alphabet". Answer: "lphbet"\n\
            \n\
            Question: Delete every instance of "{}" in "{}".',
    "ins_char_1s_prompt": 'Add the specified letter after every instance of the second specified letter in a given word, based on the following examples:\n\
            \n\
            e.g.: Add an "e" after every "a" in "alphabet". Answer: "aelphaebet"\n\
            \n\
            Question: Add an "{}" after every "{}" in "{}".',
    "sub_char_1s_prompt": 'Substitute the first specified letter with the second specified letter in a given word, based on the following examples:\n\
            \n\
            e.g.: Substitute "a" with "b" in "alphabet". Answer: "blphbbet"\n\
            \n\
            Question: Substitute "{}" with "{}" in "{}".',
    "del_char_fs_prompt": 'Delete every instance of a specified letter in a given word, based on the following examples:\n\
            \n\
            1. Delete every instance of "a" in "alphabet". Answer: "lphbet"\n\
            2. Delete every instance of "l" in "hello". Answer: "heo"\n\
            3. Delete every instance of "z" in "zebra". Answer: "ebra"\n\
            4. Delete every instance of "u" in "tongue". Answer: "tonge"\n\
            \n\
            Question: Delete every instance of "{}" in "{}".',
    "ins_char_fs_prompt": 'Add the specified letter after every instance of the second specified letter in a given word, based on the following examples:\n\
            \n\
            1. Add an "e" after every "a" in "alphabet". Answer: "aelphaebet"\n\
            2. Add an "l" after every "l" in "hello". Answer: "hellllo"\n\
            3. Add an "t" after every "z" in "zebra". Answer: "ztebra"\n\
            4. Add an "f" after every "u" in "tongue". Answer: "tongufe"\n\
            \n\
            Question: Add an "{}" after every "{}" in "{}".',
    "sub_char_fs_prompt": 'Substitute the first specified letter with the second specified letter in a given word, based on the following examples:\n\
            \n\
            1. Substitute "a" with "b" in "alphabet". Answer: "blphbbet"\n\
            2. Substitute "h" with "e" in "hello". Answer: "eello"\n\
            3. Substitute "z" with "a" in "zebra". Answer: "aebra"\n\
            4. Substitute "u" with "e" in "tongue". Answer: "tongee"\n\
            \n\
            Question: Substitute "{}" with "{}" in "{}".',
    "del_char_cot_prompt": 'Delete every instance of "{}" in "{}". Show you reasoning process step by step. Please provide the final answer at the end with "Answer:".',
    "ins_char_cot_prompt": 'Add an "{}" after every "{}" in "{}". Show you reasoning process step by step. Please provide the final answer at the end with "Answer:".',
    "sub_char_cot_prompt": 'Substitute "{}" with "{}" in "{}". Show you reasoning process step by step. Please provide the final answer at the end with "Answer:".',
}
args = SimpleNamespace(**ARGS)
# -----------------------------------------------------------------------------

client = get_client(args.model_path)

CHAR_TASKS = [
    'ins_char',
    'del_char',
    'sub_char',
    'swap_char',
    'contains_char',
]

WORD_TASKS = [
    'ins_word',
    'del_word',
    'sub_word',
    'swap_word',
    'contains_word',
]

OUTPUT_PATH = Path(f"{args.output_dir}") / args.task / args.model_path
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# write config to file
with open(OUTPUT_PATH / "config.json", "w") as f:
    json.dump(vars(args), f, indent=4)

dataset = load_dataset(
    'csv', data_files=f"./data/{args.task}.tsv", split='train', sep="\t"
)
if not args.resume and args.testing_dataset_range:
    dataset = dataset.select(range(*args.testing_dataset_range))
elif args.resume:
    # read existing progress
    with open(OUTPUT_PATH / "labels.txt", 'r') as f:
        progress = len(f.readlines())
    # resume working on the rest data samples
    dataset = dataset.select(range(progress, len(dataset)))

# ignore case for word tasks
if args.task in WORD_TASKS:
    dataset = dataset.map(
        lambda x: {**x, "label": x["label"].lower()},
        batched=True,
        num_proc=10,
    )


# tool function to extract clean output as final answer
def clean_output(out):
    try:
        out = out.strip()
        out = out.split("Answer:")[-1]
        out = out.split("<s>")[0]
        out = out.replace(".", "").strip()
        out = out.split("\"")[-2] if '"' in out else out
        out = out.split("'")[-2] if "'" in out else out
        return out
    except Exception:
        # something wasn't generated properly, discard
        return ''


outputs = []
for data in tqdm(dataset):
    # build prompt
    prompt_argument = (data["input1"], data["input2"])
    if "input3" in data:
        prompt_argument += (data["input3"],)

    prompt = ARGS[f"{args.task}_{args.baseline}_prompt"].format(*prompt_argument)

    # -------------------------------------------------------------------------
    # reasoning process
    step1 = client.chat.completions.create(
        model=args.model_path,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0,
        top_p=0.95,
        max_tokens=args.max_new_tokens,
    )
    out = step1.choices[0].message.content.strip()
    # -------------------------------------------------------------------------

    cleaned_out = clean_output(out)

    if args.task in WORD_TASKS:
        cleaned_out = cleaned_out.lower()
    outputs.append(cleaned_out)

    # write outputs and labels to file
    with open(OUTPUT_PATH / "raw_outputs.txt", "a+") as f:
        f.write(out.replace("\n", " ") + "\n")

    with open(OUTPUT_PATH / "outputs.txt", "a+") as f:
        f.write(cleaned_out.replace("\n", " ") + "\n")

    with open(OUTPUT_PATH / "labels.txt", "a+") as f:
        f.write(data["label"] + "\n")
