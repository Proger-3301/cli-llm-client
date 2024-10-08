from openai import OpenAI
import json
import sys
import os

MAX_MSGS_NUM = 12

cfg_path = os.path.join(os.path.dirname(__file__), 'config.json')
cfg = json.loads(open(cfg_path, 'r').read())

client = OpenAI(
  base_url = cfg["base-url"],
  api_key = cfg["api-key"]
)

sys_prompt = cfg["main-prompt"]
if len(sys.argv) > 1:
  sys_prompt = cfg[sys.argv[1]+"-prompt"]

msgs = []

def get_files(prompt):
  try:
    for i in range(len(prompt)):
      if prompt[i:i+5] == "file{":
        for j in range(i+5, len(prompt)):
          if prompt[j] == "}":
            return get_files(prompt[:i]+'\n'+open(prompt[i+5:j], 'r').read()+'\n'+prompt[j+1:])
    return prompt
  except:
    return "just write: No such file or directory"

def get_msg(content):
  return client.chat.completions.create(
    model=cfg["model"],
    messages=[{"role":"system","content":sys_prompt}]+content,
    temperature=0.2,
    top_p=0.7,
    max_tokens=4096,
    stream=True
  )

if len(sys.argv) > 2:
  text = ""
  for ar in sys.argv[2:]:
      text += ar + ' '
  text = get_files(text)
  msg = {"role":"user","content":text}
  completion = get_msg([msg])
  print("", end="", flush=True)
  for chunk in completion:
    ch = chunk.choices[0].delta.content
    if ch is not None:
      print(ch, end="", flush=True)
  print('\n')
  exit()

os.system("clear")

while True:
  tx = input("\x1b[32m>>> ")
  print("\x1b[0m", end="")
  if tx == "/clear":
    os.system("clear")
    msgs = []
    continue
  tx = get_files(tx)
  if tx == "/exit":
    exit()

  msg = {"role":"user","content":tx}
  msgs.append(msg)
  completion = get_msg(msgs)
  print("", end="", flush=True)
  assis_tx = ""

  for chunk in completion:
    ch = chunk.choices[0].delta.content
    if ch is not None:
      assis_tx += ch
      print(ch, end="", flush=True)
  assis_msg = {"role":"assistant","content":assis_tx}

  msgs.append(assis_msg)
  msgs = msgs[-MAX_MSGS_NUM:]
  print("\n")
