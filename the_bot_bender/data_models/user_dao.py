import azure.cosmos.cosmos_client as cosmos_client

from data_models.user_profile import UserProfile
from config import DefaultConfig

CONFIG = DefaultConfig()

uri = CONFIG.COSMOS_DB_URI
key = CONFIG.COSMOS_DB_PRIMARY_KEY
database_name = CONFIG.COSMOS_DB_DATABASE_ID
container_name = CONFIG.COSMOS_DB_CONTAINER_ID


# classe che permette operazioni CRUD per il database
class UserDAO:

    @staticmethod
    def insertUser(user: UserProfile):
        client = cosmos_client.CosmosClient(uri, {"masterKey":key})

        client.UpsertItem(
            "dbs/" + database_name + "/colls/" + container_name,
            {
            'id': user.id,
            'name': user.name,
            'surname': user.surname,
            'city': user.city,
            'favorite_books': user.favorite_books
        })

    @staticmethod
    def searchUserById(id_user: str):
        client = cosmos_client.CosmosClient(uri, {"masterKey":key})

        for item in client.QueryItems(
                "dbs/" + database_name + "/colls/" + container_name,
                f'SELECT * FROM {container_name} u WHERE u.id LIKE "{id_user}"',
                {'enableCrossPartitionQuery': True}):
            user = UserProfile(item['id'], item['name'], item['surname'], item['city'],
                               item['favorite_books'])
            return user

        """for item in container.query_items(query=f'SELECT * FROM {container_name} u WHERE u.id LIKE "{id_user}"',
                                          enable_cross_partition_query=True):
            user = UserProfile(item['id'], item['name'], item['surname'], item['city'],
                               item['favorite_books'].split(","))"""


    @staticmethod
    def updateUserById(user: UserProfile):
        client = cosmos_client.CosmosClient(uri, {"masterKey":key})

        client.UpsertItem(
            "dbs/" + database_name + "/colls/" + container_name,
            {
                'id': user.id,
                'name': user.name,
                'surname': user.surname,
                'city': user.city,
                'favorite_books': user.favorite_books
            })


        """for item in container.query_items(query=f'SELECT * FROM {container_name} u WHERE u.id LIKE "{user.id}"',
                                          enable_cross_partition_query=True):
            container.replace_item(item, {
                'id': user.id,
                'name': user.name,
                'surname': user.surname,
                'city': user.city,
                'telephone': user.surname,
                'favorite_books': ','.join(user.favorite_books)
            }, populate_query_metrics=None, pre_trigger_include=None, post_trigger_include=None)
            return"""
