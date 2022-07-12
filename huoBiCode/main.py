# encoding: utf-8
from multiprocessing import Process
import yaml, sys, json
sys.path.append('../huoBiCode')

# from huoBi_monitor import main as huoBi_main_


class ModelProcess(Process):
    def __init__(self, name):
        self.name = name

    def run(self):
        pass


def main():
    # with open("config/process.yaml", 'r') as f:
    #     config_data = yaml.load(f, Loader=yaml.full_load_all())

    with open("config/process.json", 'r') as f:
        config_data = json.loads(f.read())

    for name in config_data:
        module_name = name
        process_cf = config_data[name]
        module = __import__(module_name)
        p = Process(target=module.main, args=(process_cf,))
        p.start()


if __name__ == '__main__':
    main()