### Server installation:

``` python
pip3 install flask==0.12.2
pip3 install flask_cors==3.0.3
pip3 install pymongo
pip3 install bcrypt
```

```
brew install mongodb
```

> import database_backup/users_collection.json and  database_backup/success_upload_collection.json into MongoDB.

run server.py and flaskserver.py
```
python3 server.py
python3 flask_server.py
```

---

### Client installation:

> IMPORTANT: Don't install in venvirlen, due to the wxPython installation problem.

```python
pip3 install boto3
pip3 install --upgrade --pre -f https://wxpython.org/Phoenix/snapshot-builds/ wxPython
pip3 install uuid
```

run uploader.py
```
python3 uploader.py
```


