import requests
import json

fileServer = "https://mdsv-file-server.onrender.com"


def fetchFiles(path):
    response = requests.post(fileServer, json={
        "action": "read",
        "path": path,
        "showHiddenItems": False,
        "data": []
    })

    data = json.loads(json.loads(response.text))

    return data["files"]


def traverse_path(path):
    files = fetchFiles(path)
    tree = []
    for item in files:
        if item["isFile"]:
            tree.append(item["name"])
        else:
            subtree = traverse_path(path + "/" + item["name"])
            if subtree:
                tree.append({"directory": item["name"], "files": subtree})
    return tree


def listFiles():
    tree = traverse_path("/")
    print(json.dumps(tree, indent=2))
    return tree


if __name__ == "__main__":
    listFiles()
