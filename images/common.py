from os import environ

def log(message: str) -> None:
  print("[%s] %s" % (environ["USER"], message))
