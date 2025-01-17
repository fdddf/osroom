# -*-coding:utf-8-*-
import json
import os
import shutil
import time
from collections import OrderedDict
from copy import deepcopy
from apps.configs.sys_config import APPS_PATH
from apps.core.logger.web_logging import web_start_log
from init_datas import INIT_DATAS

__author__ = 'Allen Woo'


def update_mdb_collections(mdbs):
    """
    更新数据库mongodb collection, 不存在的colletion则创建
    :param mdbs:
    :return:
    """

    # 读取配置中的数据库json 数据
    with open("{}/configs/collections.json".format(APPS_PATH)) as rf:
        jsondata = rf.read()
        if jsondata:
            collections = json.loads(jsondata)
        else:
            collections = {}

    # 检查数据库collections
    for dbname, colls in collections.items():
        mdb = mdbs[dbname]
        for coll in colls:
            try:
                mdb.dbs.create_collection(coll)
                web_start_log.info(
                    "[DB: {}] Create collection '{}'".format(
                        mdb.name, coll))
            except Exception as e:
                if "already exists" in str(e):
                    web_start_log.info(e)
                else:
                    web_start_log.warning(e)

    # 将最新的数据库结构写入配置文件, 方便开发者了解结构
    new_collections = OrderedDict({})
    for dbname, mdb in mdbs.items():
        new_collections[dbname] = {}
        collnames = mdb.dbs.collection_names()
        for collname in collnames:
            if collname == "system.indexes" or collname.startswith("plug_"):
                continue
            new_collections[dbname][collname] = {}
            data = mdb.dbs[collname].find_one({}, {"_id": 0})
            if data:
                for k, v in data.items():
                    new_collections[dbname][collname][k] = str(type(v))

    with open("{}/configs/collections.json".format(APPS_PATH), "w") as wf:
        collections = json.dumps(new_collections, indent=4, ensure_ascii=False)
        wf.write(collections)


def init_datas(mdbs):
    """
    初始web化数据
    :return:
    """

    # 复制最新配置文件
    config_sample_path = "{}/configs/config_sample.py".format(APPS_PATH)
    target_path = "{}/configs/config.py".format(APPS_PATH)
    if os.path.exists(config_sample_path):
        print("Copy config file")
        if os.path.exists(target_path):
            os.remove(target_path)
        shutil.copy(config_sample_path, target_path)

    # 初始化其他数据
    for data in INIT_DATAS:
        db = mdbs["sys"]
        if data["db"] == "osr_web":
            db = mdbs["web"]
        elif data["db"] == "osr_user":
            db = mdbs["user"]
        q = {}
        if "condition" in data:
            q = data["condition"]
        if db.dbs[data["coll"]].find_one(q):
            continue
        else:
            print("* [Initialization data] {}".format(data["coll"]))
            db.dbs[data["coll"]].insert_many(data["datas"])

    # 初始化主题数据
    init_theme_data(mdbs)


def init_theme_data(mdbs):
    theme = mdbs["sys"].dbs["sys_config"].find_one({"project": "theme", "key": "CURRENT_THEME_NAME"})
    if theme:
        theme_name = theme["value"]
    else:
        return True

    if mdbs["sys"].dbs["theme_display_setting"].find_one({"theme_name": theme_name}):
        print("* [Init theme] No initialization required")
        return True

    init_file = "{}/themes/{}/init_setting.json".format(APPS_PATH, theme_name)
    if os.path.exists(init_file):
        # 读取数据
        with open(init_file) as rf:
            jsondata = rf.read()
            if jsondata:
                init_data = json.loads(jsondata)

    # 初始化主题数据
    for data in init_data:
        tempdata = deepcopy(data)
        tempdata["theme_name"] = theme_name
        # 查找是否存在分类
        r = mdbs["web"].dbs["theme_category"].find_one({
            "name": tempdata["category"],
            "type": tempdata["type"],
            "theme_name": theme_name,
            "user_id": 0})
        if r:
            tempdata["category_id"] = str(r["_id"])
        else:
            # 不存在则创建
            r = mdbs["web"].dbs["theme_category"].insert_one(
                {"name": tempdata["category"],
                 "type": tempdata["type"],
                 "theme_name": theme_name,
                 "user_id": 0})
            tempdata["category_id"] = str(r.inserted_id)
        fields = ["title", "link", "text", "name", "code", "code_type"]
        for field in fields:
            if field not in tempdata:
                tempdata[field] = ""
        tempdata["time"] = time.time()
        mdbs["sys"].dbs["theme_display_setting"].insert_one(tempdata)


def compatible_processing(mdbs):
    """
    兼容上一个版本
    :return:
    """
    # 当前主题设置加上主题名称
    theme = mdbs["sys"].dbs["sys_config"].find_one({"project": "theme", "key": "CURRENT_THEME_NAME"})
    if theme:
        theme_name = theme["value"]
        mdbs["sys"].dbs["theme_display_setting"].update_many({"theme_name": {"$exists": False}},
                                                         {"$set": {"theme_name": theme_name}})

        # 主题设置的数据分类信息转移
        categorys = mdbs["web"].db.category.find({"type": {"$regex": ".+_theme$"}})
        for category in categorys:
            category["type"] = category["type"].replace("_theme", "")
            category["theme_name"] = theme_name
            r = mdbs["web"].db.theme_category.insert_one(category)
            if r.inserted_id:
                mdbs["web"].db.category.delete_one({"_id": category["_id"]})
