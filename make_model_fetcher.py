import requests

kbb_api_url = "https://www.kbb.com/vehicleapp/api/"

class Make(object):
    def __init__(self, dict):
        self.__dict__ = dict

class Model(object):
    def __init__(self, dict):
        self.__dict__ = dict

def get_kbb_makes():
    data = {"operationName":"MAKES_QUERY","variables":{"make":"2"},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"5e9f49f68dfa81f9251ddd7a1a958bebb65ea982a34b7860cf47f47043f1901f"}}}
    response = requests.post(kbb_api_url, json=data)

    res_json = response.json()
    makes_json = res_json["data"]["makes"]

    makes = []

    for make_dict in makes_json:
        makes.append(Make(make_dict))

    return makes

def get_kbb_models_per_make(make):
    data = {"operationName":"MODELS_QUERY","variables":{"vehicleClass":"","vehicleType":"","make":make.id},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"2e7f89c39a5e92eecfe7c82bc4fb797c718952bb33b070be36d6d9be68eab163"}}}
    response = requests.post(kbb_api_url, json=data)

    res_json = response.json()
    models_json = res_json["data"]["models"]

    models = []

    for model_dict in models_json:
        models.append(Model(model_dict))

    return models

'''
makes_list = get_kbb_makes()

get_kbb_models_per_make(makes_list[1])

'''
