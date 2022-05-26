from flask import (
    Flask,
    render_template,
    render_template_string,
    url_for,
    request,
    redirect,
)
from web3 import Web3
from solcx import compile_standard, install_solc
import json

ganache_url = "http://localhost:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))
print("connected")
acc_1 = web3.eth.accounts[0]
acc_2 = web3.eth.accounts[1]
web3.eth.defaultAccount = acc_1
private_key = "a93d196c2460693068d81f99cf618bcc71d9c5f6d543f7d6be073c59e3822f87"

# Reading the Contract
with open("Solution.sol", "r") as f:
    solution_file = f.read()
    # print(simple_storage_file)


# Compiling the Contract
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"Solution.sol": {"content": solution_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.8.1",
)
# print(compiled_sol)

# Dump the Compiled solc file into json file
with open("compiled_sol.json", "w") as file:
    json.dump(compiled_sol, file)

# get Bytecode for Deploying
bytecode = compiled_sol["contracts"]["Solution.sol"]["solution"]["evm"]["bytecode"][
    "object"
]

# get ABI (Application Binary Interface)
abi = compiled_sol["contracts"]["Solution.sol"]["solution"]["abi"]

solutions = web3.eth.contract(abi=abi, bytecode=bytecode)


def new_contract(name, donation, event):
    nonce = web3.eth.getTransactionCount(acc_1)

    # Build the Transaction, The First Smart Contract.
    # transaction = solutions.constructor().buildTransaction(
    #     {
    #         "nonce": nonce,
    #         "gasPrice": web3.toWei(5, "gwei"),
    #         "gas": 2000000,
    #         "from": acc_1,
    #     }
    # )

    # THIS IS A WORKING LINE. USE THIS
    tx_hash = solutions.constructor(name, donation, event).transact()

    # tx_hash = (
    #     solutions.constructor(name, donation)
    #     .buildTransaction(
    #         {
    #             "nonce": nonce,
    #             "gasPrice": web3.toWei(5, "gwei"),
    #             "gas": 2000000,
    #             "from": acc_1,
    #             # "to": acc_2,
    #             "value": donation,
    #         }
    #     )
    #     .transact()
    # )

    # Sign the transaction
    # signed_transaction = web3.eth.account.signTransaction(transaction, private_key=private_key)

    # Sending the transaction
    # transaction_hash = web3.eth.sendRawTransaction(signed_transaction)

    # Waiting for the Transaction to finish
    # web3.eth.waitForTransactionReceipt(transaction_hash)
    first_tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    print(
        f"Transaction Hash: {first_tx_receipt}, Address: {first_tx_receipt.contractAddress}"
    )

    solution_setter = web3.eth.contract(
        address=first_tx_receipt.contractAddress, abi=abi
    )
    print(solution_setter.functions.name().call())
    print(solution_setter.functions.singleDonation().call())


# def contract_donator(name, donation):
#     # new_tx_hash = solution_setter.functions.donate(name, donation).transact()
#     new_tx_hash = solution_setter.functions.donate(name, donation).transact()
#     tx_receipt = web3.eth.wait_for_transaction_receipt(new_tx_hash)
#     # print(type(donation))
#     print(solution_setter.functions.nameviewer().call())
#     print(solution_setter.functions.getTotalDonations().call())
#     print(
#         web3.eth.get_transaction(
#             "0x97a335b765700ad2de4aeb6c2c731c999d7a09949aa0a40417509b72566fc397"
#         )
#     )


app = Flask(__name__)

Username = ""
Role = 0


@app.route("/", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        re_password = request.form["re_password"]
        option = request.form["position"]
        global Role
        if option == "organiser":
            Role = 0
        else:
            Role = 1
        names = []
        with open("user.csv", "r") as f:
            datalist = f.readlines()
            for lines in datalist:
                entry = lines.split(",")
                names.append(entry[0])
        # print(name, names)
        if name in names:
            return redirect(url_for("already"))
        else:
            if password != re_password:
                return redirect(url_for("mismatch"))
            else:
                with open("user.csv", "a") as f:
                    f.writelines(f"{name},{password},{Role},{email}\n")
                return redirect(url_for("success_signup"))
    return render_template("signup.html")


@app.route("/success_signup", methods=["POST", "GET"])
def success_signup():
    return render_template("success_signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form["name"]
        password = request.form["password"]
        with open("user.csv", "r") as f:
            datalist = f.readlines()
            for line in datalist:
                entry = line.split(",")
                print(entry[0], entry[1], name, password)
                if not (name == entry[0] and password == entry[1]):
                    continue
                else:
                    global Role
                    Role = entry[2]
                    return redirect(url_for("index", Name=name, role=entry[2]))
    return render_template("login.html", value=0)


@app.route("/mismatch", methods=["POST", "GET"])
def mismatch():
    return render_template("mismatch.html")


@app.route("/already", methods=["POST", "GET"])
def already():
    return render_template("already.html")


@app.route("/index", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        name = request.args.get("Name")
        # Role = request.args.get("role")
        global Username
        Username = name
        if request.form.get("Organisation"):
            return redirect(url_for("organisation"))
        elif request.form.get("Donator"):
            return redirect(url_for("donator", Name=Username))
        elif request.form.get("Transactions"):
            return redirect(url_for("transactions"))
        elif request.form.get("Logout"):
            return redirect(url_for("login"))
    else:
        return render_template("index.html", role=Role)
    return render_template("index.html", role=Role)


@app.route("/organisation", methods=["POST", "GET"])
def organisation():
    if request.method == "POST":
        name = request.form["Name"]
        amount = request.form["Amount"]
        with open("events.csv", "a") as f:
            f.writelines(f"{name},{amount}\n")
            return redirect(url_for("eventSuccess", Name=name, Amount=amount))
    return render_template("organisation.html")


@app.route("/eventSuccess")
def eventSuccess():
    name = request.args.get("Name")
    amount = request.args.get("Amount")
    return render_template("eventSuccess.html", name=name, amount=amount)


@app.route("/donator", methods=["POST", "GET"])
def donator():
    eventName = []
    # name1 = request.args.get("Name")
    with open("events.csv", "r") as f:
        dataList = f.readlines()
        for line in dataList:
            entry = line.split(",")
            eventName.append(entry[0])
    if request.method == "POST":
        name = Username
        donation = int(request.form["Donation"])
        event = request.form["Event"]
        print(name, donation)
        # print(type(donation))
        new_contract(name, donation, event)
        return redirect(url_for("success_donations", Name=name, Donation=donation))
    return render_template("donator.html", eventName=eventName, name=Username)


@app.route("/transactions")
def transactions():
    block_numbers = web3.eth.block_number
    # print(f"Total Block numbers are: {block_numbers}")
    data = []
    sum = 0
    keys = ["name", "donation", "event"]
    for i in reversed(range(1, block_numbers + 1)):
        block_data = web3.eth.get_block(i)
        # print(f"Block data: {block_data}")
        block_data_transaction = block_data["transactions"][0]
        # print(f"Block transaction: {block_data_transaction}")
        transaction_receipt = web3.eth.get_transaction_receipt(block_data_transaction)
        # print(f"Transaction receipt: {transaction_receipt}")
        transaction_receipt_address = transaction_receipt["contractAddress"]
        # print(f"Transaction receipt address: {transaction_receipt_address}")
        getter = web3.eth.contract(address=transaction_receipt_address, abi=abi)
        name = getter.functions.name().call()
        donation = getter.functions.singleDonation().call()
        event = getter.functions.event1().call()
        sum += donation
        data.append(dict(zip(keys, [name, donation, event])))
    # print(data)
    return render_template("transactions.html", data=data, total=sum)


@app.route("/success_donations")
def success_donations():
    Name = request.args.get("Name", None)
    Donation = request.args.get("Donation", None)
    return render_template("success_donations.html", name=Name, donation=Donation)


if __name__ == "__main__":
    app.run(debug=True)
