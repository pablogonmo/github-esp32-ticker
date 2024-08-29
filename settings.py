import ujson

def read_config(var):
    try:
        with open('settings.json', 'r', encoding = 'utf-8') as f:
            content = ujson.loads(f.read())
            f.close()
        return content[var]
    except Exception as e:
        print(str(e))
        return False

def save_config(var, val):
    with open('settings.json', 'r', encoding = 'utf-8') as f:
        config = ujson.loads(f.read())
        f.close()
    config[var] = val

    with open('settings.json', 'w') as f:
        config_str = ujson.dumps(config)
        f.write(config_str)
        f.close()

    print(f' > Saving config: {config}')