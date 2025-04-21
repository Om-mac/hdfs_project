python3 run_namenode.py
python3 run_datanode.py --id datanode1 --port 5001 --storage data/datanode1
python3 run_datanode.py --id datanode2 --port 5002 --storage data/datanode2

python3 run_client.py upload sample.txt
python3 run_client.py download sample.txt  //path=example.txt then shasum command
python3 run_client.py list
python3 run_client.py delete <file>


