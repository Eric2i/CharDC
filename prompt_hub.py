import json
from pathlib import Path

PROMPTS = {}

PROMPTS["del_char"] = {
    "step1_prompt": "Convert '{input_string}' into a list sequence of characters. Please only return the list.",
    "step2_prompt": "Replace the character '{obj}' with ''(empty string) in the following list: '{sequence}'.",
    "step3_prompt": "Perform a MECHANICAL concatenation of the elements in the list {sequence} into a single string, treating each element as a literal string to be joined. Show each algorithmic concatenation step. Notice that the result may not be a real word. Do NOT auto-correct the result. Do NOT add additional space(s) into the result. Finally, simply wrap up the final result with <ans>...</ans>.",
}
PROMPTS["ins_char"] = {
    "step1_prompt": "Convert '{input_string}' into a list sequence of characters. Please only return the list.",
    "step2_prompt": "Update the character '{obj}' into '{obj}{ist}' in the following list: '{sequence}'. Do not use extra formatting like markdown triple quotes and please only return the updated list!",
    "step3_prompt": "Perform a MECHANICAL concatenation of the elements in the list {sequence} into a single string, treating each element as a literal string to be joined. Show each algorithmic concatenation step. Notice that the result may not be a real word. Do NOT auto-correct the result. Do NOT add additional space(s) into the result. Finally, simply wrap up the final result with <ans>...</ans>.",
}

# ins_char_seq_v1 is a variation of ins_char, using json format for the sequence representation.
PROMPTS["ins_char_seq_v1"] = {
    "step1_prompt": "Please break the string '{input_string}' into characters in json format with indices as the keys and the corresponding characters as the values. Only return the json data without extra formatting or explanation.",
    "step2_prompt": "Consider the following json data: {sequence}. Update all key-value pairs whose value equal to '{obj}' into '{obj}{ist}'. Only return the json data without extra formatting or explanation.",
    "step3_prompt": "Consider the following json data: {sequence}. Sequentially concatenate all values of the key-value pairs above into a single string without delimiters or whitespaces. do it step by step explicitly before presenting the final answer. Finally, simply wrap up the final result with <ans>...</ans>.",
}

PROMPTS["sub_char"] = {
    "step1_prompt": "Convert '{input_string}' into a list sequence of characters. Please only return the list.",
    "step2_prompt": "Update the character '{obj}' into '{rep}' in the following list: '{sequence}'.  Do not use extra formatting like markdown triple quotes and please only return the updated list!",
    "step3_prompt": "Perform a MECHANICAL concatenation of the elements in the list {sequence} into a single string, treating each element as a literal string to be joined. Show each algorithmic concatenation step. Notice that the result may not be a real word. Do NOT auto-correct the result. Do NOT add additional space(s) into the result. Finally, simply wrap up the final result with <ans>...</ans>.",
}

# abl-step1 is a set of prompts for the step-1 ablation study with diff shot examples.
PROMPTS["abl-step1"] = {
    "3shots_prompt": "Convert given string into a list of characters. Simply return the list without explanation as exampled. Example1, input:'hello', output:['h', 'e', 'l', 'l', 'o']; Example2, input:'artificial', output:['a', 'r', 't', 'i', 'f', 'i', 'c', 'i', 'a', 'l']. Example3: input:'learning', output:['l', 'e', 'a', 'r', 'n', 'i', 'n', 'g']. Task: input:'{input_string}' output:",
    "2shots_prompt": "Convert given string into a list of characters. Simply return the list without explanation as exampled. Example1, input:'hello', output:['h', 'e', 'l', 'l', 'o']; Example2, input:'artificial', output:['a', 'r', 't', 'i', 'f', 'i', 'c', 'i', 'a', 'l']. Task: input:'{input_string}' output:",
    "1shots_prompt": "Convert given string into a list of characters. Simply return the list without explanation as exampled. Example1, input:'hello' output:['h', 'e', 'l', 'l', 'o']; Task: input:'{input_string}' output:",
    "0shots_prompt": "Convert string '{input_string}' into a list of characters. Simply return the list without explanation.",
}

PROMPTS["abl-step2-sub"] = {
    "0shots_prompt": """Replace all occurrences of a specified character in the given list with another character. Do not explicitly show your reasoning process. Directly return the updated list.
Task:
Input: {input}, Character to replace: '{obj}', Replacement character: '{tar}'
Output:""",
    "1shots_prompt": """Replace all occurrences of a specified character in the given list with another character. Do not explicitly show your reasoning process. Refer to the example below for guidance.
Example 1:
Input: ['h', 'e', 'l', 'l', 'o'], Character to replace: 'l', Replacement character: 'j'
Output: ['h', 'e', 'j', 'j', 'o']

Task:
Input: {input}, Character to replace: '{obj}', Replacement character: '{tar}'
Output:""",
    "2shots_prompt": """Replace all occurrences of a specified character in the given list with another character. Do not explicitly show your reasoning process. Refer to the example below for guidance.
Example 1:
Input: ['h', 'e', 'l', 'l', 'o'], Character to replace: 'l', Replacement character: 'j'
Output: ['h', 'e', 'j', 'j', 'o']

Example 2:
Input: ['a', 'b', 'a', 'a', 'c'], Character to replace: 'a', Replacement character: 'z'
Output: ['z', 'b', 'z', 'z', 'c']

Task:
Input: {input}, Character to replace: '{obj}', Replacement character: '{tar}'
Output:""",
    "3shots_prompt": """Replace all occurrences of a specified character in the given list with another character. Do not explicitly show your reasoning process. Refer to the example below for guidance.
Example 1:
Input: ['h', 'e', 'l', 'l', 'o'], Character to replace: 'l', Replacement character: 'j'
Output: ['h', 'e', 'j', 'j', 'o']

Example 2:
Input: ['a', 'b', 'a', 'a', 'c'], Character to replace: 'a', Replacement character: 'z'
Output: ['z', 'b', 'z', 'z', 'c']

Example 3:
Input: ['m', 'a', 'r', 'k', 'e', 't'], Character to replace: 'e', Replacement character: 'x'
Output: ['m', 'a', 'r', 'k', 'x', 't']

Task:
Input: {input}, Character to replace: '{obj}', Replacement character: '{tar}'
Output:""",
}
PROMPTS["abl-step2-del"] = {
    "0shots_prompt": "Update ALL item '{obj}' into '{tar}' in the following list: '{input}'. Do not use extra formatting like markdown triple quotes and please only return the updated list!",
    "1shots_prompt": "Complete the task learning from the example. Do not use extra formatting like markdown triple quotes and please only return the updated list! Example1: Update ALL item 'l' into '' in the following list:'['h', 'e', 'l', 'l', 'o']'. Output:['h', 'e', '', '', 'o']; Task: Update ALL character '{obj}' into '{tar}' in the following list: '{input}'. Output:",
    "2shots_prompt": "Complete the task learning from the examples. Do not use extra formatting like markdown triple quotes and please only return the updated list! Example1: Update ALL item 'l' into '' in the following list:'['h', 'e', 'l', 'l', 'o']'. Output:['h', 'e', '', '', 'o']; Example2: Update ALL item 'i' into '' in the following list:'['l', 'i', 'n', 'g', 'u', 'i', 's', 't', 'i', 'c', 's']'. Output:['l', '', 'n', 'g', 'u', '', 's', 't', '', 'c', 's']; Task: Update ALL character '{obj}' into '{tar}' in the following list: '{input}'. Output:",
    "3shots_prompt": "Complete the task learning from the examples. Do not use extra formatting like markdown triple quotes and please only return the updated list! Example1: Update ALL item 'l' into '' in the following list:'['h', 'e', 'l', 'l', 'o']'. Output:['h', 'e', '', '', 'o']; Example2: Update ALL item 'i' into '' in the following list:'['l', 'i', 'n', 'g', 'u', 'i', 's', 't', 'i', 'c', 's']'. Output:['l', '', 'n', 'g', 'u', '', 's', 't', '', 'c', 's']; Example3: Update ALL item 'o' into '' in the following list:'['d', 'i', 's', 't', 'r', 'o']'. Output:['d', 'i', 's', 't', 'r', '']; Task: Update ALL character '{obj}' into '{tar}' in the following list: '{input}'. Output:",
}
PROMPTS["abl-step2-ins"] = {
    "0shots_prompt": "Update ALL item '{obj}' into '{tar}' in the following list: '{input}'. Do not use extra formatting like markdown triple quotes and please only return the updated list!",
    "1shots_prompt": "Complete the task learning from the example. Example1: Update ALL item 'l' into 'lj' in the following list:'['h', 'e', 'l', 'l', 'o']'. Output:['h', 'e', 'lj', 'lj', 'o']; Task: Update ALL character '{obj}' into '{tar}' in the following list: '{input}'. Output:",
    "2shots_prompt": "Complete the task learning from the examples. Example1: Update ALL item 'l' into 'lj' in the following list:'['h', 'e', 'l', 'l', 'o']'. Output:['h', 'e', 'lj', 'lj', 'o']; Example2: Update ALL item 'i' into 'ij' in the following list:'['l', 'i', 'n', 'g', 'u', 'i', 's', 't', 'i', 'c', 's']'. Output:['l', 'ij', 'n', 'g', 'u', 'ij', 's', 't', 'ij', 'c', 's']; Task: Update ALL character '{obj}' into '{tar}' in the following list: '{input}'. Output:",
    "3shots_prompt": "Complete the task learning from the examples. Example1: Update ALL item 'l' into 'lj' in the following list:'['h', 'e', 'l', 'l', 'o']'. Output:['h', 'e', 'lj', 'lj', 'o']; Example2: Update ALL item 'i' into 'ij' in the following list:'['l', 'i', 'n', 'g', 'u', 'i', 's', 't', 'i', 'c', 's']'. Output:['l', 'ij', 'n', 'g', 'u', 'ij', 's', 't', 'ij', 'c', 's']; Example3: Update ALL item 'o' into 'op' in the following list:'['d', 'i', 's', 't', 'r', 'o']'. Output:['d', 'i', 's', 't', 'r', 'op']; Task: Update ALL character '{obj}' into '{tar}' in the following list: '{input}'. Output:",
}

PROMPTS["abl-step3"] = {
    "0shots_prompt": """Perform a MECHANICAL concatenation of the elements in the given list into a single string. Treat each element as a literal string to be joined.
Notice that: 1) the result may not be a real word. 2) do NOT auto-correct the result. 3) do NOT add additional space(s) into the result.     
Simply wrap up the final result with <ans>...</ans>.

Task:
input: {input}.
output:""",
    "1shots_prompt": """Perform a MECHANICAL concatenation of the elements in the given list into a single string. Treat each element as a literal string to be joined.
Notice that: 1) the result may not be a real word. 2) do NOT auto-correct the result. 3) do NOT add additional space(s) into the result.     
Simply wrap up the final result with <ans>...</ans>.

Example 1:
input: ['h', 'e', 'j', 'j', 'o']
output: <ans>hejjo</ans>

Task:
input: {input}.
output:""",
    "2shots_prompt": """Perform a MECHANICAL concatenation of the elements in the given list into a single string. Treat each element as a literal string to be joined.
Notice that: 1) the result may not be a real word. 2) do NOT auto-correct the result. 3) do NOT add additional space(s) into the result.     
Simply wrap up the final result with <ans>...</ans>.

Example 1:
input: ['h', 'e', 'j', 'j', 'o']
output: <ans>hejjo</ans>

Example 2:
input: ['u', 'r', 'k', 'i', 'f', 'i', 'c', 'i', 'u', 'l']
output: <ans>urkificiul</ans>

Task:
input: {input}.
output:""",
    "3shots_prompt": """Perform a MECHANICAL concatenation of the elements in the given list into a single string. Treat each element as a literal string to be joined.
Notice that: 1) the result may not be a real word. 2) do NOT auto-correct the result. 3) do NOT add additional space(s) into the result.     
Simply wrap up the final result with <ans>...</ans>.

Example 1:
input: ['h', 'e', 'j', 'j', 'o']
output: <ans>hejjo</ans>

Example 2:
input: ['u', 'r', 'k', 'i', 'f', 'i', 'c', 'i', 'u', 'l']
output: <ans>urkificiul</ans>

Example 3: 
input: ['l', 'e', 'a', 'r', 'n', '1', 'nn', 'g']
output: <ans>learn1nng</ans>

Task:
input: {input}.
output:""",
}


def get_prompts(task):
    if task not in PROMPTS:
        raise KeyError(f"Task not found in prompts hub: {task}")
    return PROMPTS[task]
