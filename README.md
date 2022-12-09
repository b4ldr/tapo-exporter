A promethous exporter to collect power usage statistics for tapo p110 plugs

= Usage =
To run first of all create a config such as

```yaml
port: 8000
listent: 127.0.0.1
email: user@example.com
password: password
plugs:
  - 192.168.0.42
```

Then run the exporter with
```shell
$ tapo-exporter -c config.yaml
```

By default the exporter will listen on localhost:8000

= Install =
pip install should be comming soon for now the following will work 

```shell
$ python3 -m build
$ pip3 install dist/tapo_exporter-*-py3-none-any.whl
```
