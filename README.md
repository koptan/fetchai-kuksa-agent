# C.A.R.V.I.S
### Car A Rather Very Intelligent System


## To run the code:
1. Clone the Python source code from this repo: https://github.com/zubairhamed/fetchai-kuksa-agent/tree/main/local-agent-payment
2. Go to local-agent-payment folder: `cd fetchai-kuksa-agent/local-agent-payment`
3. Create new python enviroment: `python3 -m venv .venv`
5. Activate the new enviroment: `source .venv/bin/activate`
6. Install dependancies: `pip install -r requirements.txt`
7. Run the code: `python agent-payment.py`
8. At this point, the code will connect to Virtual City Kuksa Data broker (hosted on Cloud) and start receiving signals

## Blockchain Infrastructure:

We have the Ethereum Besu network ready for use (Thanks to IBM for provding the VMs):

- JSON-RPC HTTP service endpoint: http://158.177.1.17:8545
- JSON-RPC WebSocket service endpoint: ws://158.177.1.17:8546
- Web block explorer address: http://158.177.1.17:25000/explorer/nodes

or you can deploy your own Blockchain node using : [Quorum Dev Quickstart](https://github.com/Consensys/quorum-dev-quickstart/tree/master)

### Wallets: 
The following wallets are available for deployment and testing: 


```json
"0xfe3b557e8fb62b89f4916b721be55ceb828dbd73" : {
		"privateKey" : "0x8f2a55949038a9610f50fb23b5883af3b4ecb3c3bb792cbcefbd1542c692be63",
		"balance" : "0x130EE8E7179044400000"
},
"0x627306090abaB3A6e1400e9345bC60c78a8BEf57" : {
		"privateKey" : "0xc87509a1c067bbde78beb793e6fa76530b6382a4c0241e5e4a9ec0a0f44dc0d3",
		"balance" : "90000000000000000000000"
},
"0xf17f52151EbEF6C7334FAD080c5704D77216b732" : {
		"privateKey" : "0xae6ae8e5ccbfb04590405997ee2d52d2b330726137b875053c36d94e974d162f",
		"balance" : "90000000000000000000000"
}
```


# Developing Tools:

 **Blockchain Smart Contract Development**:

[Hardhat Framework](https://hardhat.org/):

 Participants can use the Hardhat framework for developing smart contracts. The Hardhat framework is a development environment for Ethereum that allows developers to compile, test, and deploy smart contracts efficiently. It also provides debugging tools, and a local Ethereum network for testing.

 **Blockchain Interaction**:

[Web3.py](https://web3py.readthedocs.io/en/stable/):

 Use Web3.py for calling smart contracts from the Python project. Web3.py is a Python library that provides easy-to-use interfaces for interacting with Ethereum-based blockchains.
 

## CARVIS Dialogue
Create a google cloud account

Install gcloud CLI: https://cloud.google.com/sdk/docs/install?hl=de

Authenticate with default account login https://cloud.google.com/sdk/gcloud/reference/auth/application-default/login:
    
    $ gcloud auth application-default login

Run the agent_ai.py file:

    $ python carvis-agent/agent_ai.py

