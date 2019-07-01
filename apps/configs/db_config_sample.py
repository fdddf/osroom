# -*-coding:utf-8-*-
__author__ = "Allen Woo"

import os

DB_CONFIG = {
    "redis": {
        "host": [
            os.getenv('REDIS_HOST', '127.0.0.1')
        ],
        "password": os.getenv('REDIS_PASSWORD', ''),
        "port": [
            os.getenv('REDIS_PORT', 6379)
        ]
    },
    "mongodb": {
        "web": {
            "dbname": os.getenv('MONGODB_WEB_DB', 'osr_web'),
            "password": os.getenv('MONGODB_WEB_PWD', ''),
            "config": {
                "fsync": False,
                "replica_set": None
            },
            "host": [
                os.getenv('MONGODB_WEB_HOST', '127.0.0.1:27017')
            ],
            "username": os.getenv('MONGODB_WEB_USER', 'root')
        },
        "user": {
            "dbname": os.getenv('MONGODB_USER_DB', 'osr_user'),
            "password": os.getenv('MONGODB_USER_PWD', ''),
            "config": {
                "fsync": False,
                "replica_set": None
            },
            "host": [
                os.getenv('MONGODB_USER_HOST', '127.0.0.1:27017')
            ],
            "username": os.getenv('MONGODB_USER_USER', 'root')
        },
        "sys": {
            "dbname": os.getenv('MONGODB_SYS_DB', 'osr_sys'),
            "password": os.getenv('MONGODB_SYS_PWD', ''),
            "config": {
                "fsync": False,
                "replica_set": None
            },
            "host": [
                os.getenv('MONGODB_SYS_HOST', '127.0.0.1:27017')
            ],
            "username": os.getenv('MONGODB_SYS_USER', 'root')
        }
    }
}