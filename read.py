import pickle

with open("fhsz_chat", "rb") as f:
    a = pickle.load(f, encoding="utf8")

print(len(a))