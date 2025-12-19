# nocodb class

from enum import Enum

import requests
import json
import urllib
import logging

# inherit the parent logger
log = logging.getLogger('')
log.propagate= True

"""
Class for access to a NOCODB instance
"""

class Nocodb:

    def __init__(self, host, auth_token, verify=True):
        self.host = host
        self.auth_token = auth_token
        self.verify = verify

        self.session = requests.Session()
        self.session.headers.update({"accept": "application/json", "xc-token": self.auth_token})
        self.session.verify = self.verify


    def _url(self, path):
        return f"{self.host}/api/v2/meta/bases/{path}"


    def list_bases(self) -> dict:
        """ 
        [META] List Bases
        List all base meta data
        https://meta-apis-v2.nocodb.com/#tag/Base/operation/base-list
        GET http://localhost:8080/api/v2/meta/bases/
        """
        url = self._url("")
        log.debug(f"Nocodb list_bases() url={url}")
        res = self.session.get(url, params={}).json()
        log.debug(f"  response", extra={"res": res})

        ret = {}
        for i in res['list']:
            ret[i['id']] = i['title']

        log.debug(f"return", extra={"ret": ret})

        return ret


    def create_base(self, title, color=None, description=None, base_type=None) -> dict:
        """
        [META] Create Base
        Create a new base
        https://meta-apis-v2.nocodb.com/#tag/Base/operation/base-create
        POST http://localhost:8080/api/v2/meta/bases/
        """

        url = self._url("")

        data = {"title": title}
        if color:
            data["color"] = color
        if description:
            data["description"] = description

        if base_type:
            data["type"] = base_type.name

        log.debug(f"Nocodb create_base() url={url}", extra={"data": data})
        res = self.session.post(url, data=data).json()
        log.debug(f"  response", extra={"res": res})

        if 'msg' in res and res['msg'] == 'Invalid token':
            log.error(f"Nocodb create_base() 'Invalid token' url={url}", extra={"data": data, "res": res})
            raise Exception("Invalid token")

        return res


    def get_base_object(self, title):

        # check if such a table exists
        all_bases = self.list_bases()

        for base_id, base_title in all_bases.items():
            if title == base_title:
                return Base(base_id, nocodb=self)

        log.warning(f"Nocodb get_base_object(): No base with title '{title}' found")

        return None


    def delete_base(self, base_id) -> dict:
        """
        [META] Delete Base
        Delete the given base
        DELETE http://localhost:8080/api/v2/meta/bases/{baseId}
        """
        url = self._url(base_id)
        headers = {"accept": "application/json", "xc-token": self.auth_token}

        log.debug(f"Nocodb delete_base() url={url}", extra= {"headers": headers})
        res= requests.delete(url, headers=headers).json()
        log.debug(f"  response", extra={"res": res})

        return res


"""
Class for access to a NOCODB base == one database in the Nocodb instance
"""


class Base:

    def __init__(self, base_id, nocodb=None, host=None, auth_token=None, verify=True):

        # Don't keep the parent Nocodb object because we can work without it
        # Accessing a Base only needs the baseid and the auth_token
        # Thus like this one can create a Base object without a Nocodb object.
        # #self.nocodb= nocodb
        self.base_id = base_id
        self.verify = verify
        self.session = None

        if nocodb:

            self.host = nocodb.host
            self.auth_token = nocodb.auth_token
            self.verify = nocodb.verify
            self.session = nocodb.session  # re-use the same session

        else:

            assert None != host
            assert None != auth_token

            self.host = host
            self.auth_token = auth_token

            self.session = requests.Session()
            self.session.headers.update({"accept": "application/json", "xc-token": self.auth_token})
            self.session.verify = self.verify

        self.info = self.get_base_info()
        self.metadata = self.get_base()


    class Type(Enum):
        database = 'database'
        documentation = 'documentation'
        dashboard = 'dashboard'


    def debug(self):
        print("class Base: ", self.base_id)
        print(json.dumps(self.info, indent=4))
        print(json.dumps(self.metadata, indent=4))


    def _url(self, path):
        return f"{self.host}/api/v2/meta/bases/{self.base_id}/{path}"


    def get_base_info(self) -> dict:
        """
        [META] Get Base info
        Get info such as node version, arch, platform, is docker, rootdb and package version of a given base
        https://meta-apis-v2.nocodb.com/#tag/Base/operation/base-meta-get
        GET http://localhost:8080/api/v2/meta/bases/{baseId}/info
        """

        url = self._url("info")
        log.debug(f"Base get_base_info() url={url}")
        res = self.session.get(url, params={}).json()
        log.debug(f"  response", extra={"res": res})

        return res


    def get_base(self) -> dict:
        """
        [META] Get Base
        Get the info of a given base
        https://meta-apis-v2.nocodb.com/#tag/Base/operation/base-read
        GET http://localhost:8080/api/v2/meta/bases/{baseId}
        """

        url = self._url("")
        log.debug(f"Base get_base() url={url}")
        res = self.session.get(url, params={}).json()
        log.debug(f"  response", extra={"res": res})

        return res


    def list_tables(self) -> dict:
        """
        [META] List Tables
        List all tables in a given base
        https://meta-apis-v2.nocodb.com/#tag/DB-Table/operation/db-table-list
        GET http://localhost:8080/api/v2/meta/bases/{baseId}/tables
        """

        url = self._url("tables")
        log.debug(f"Base list_tables() url={url}")
        res = self.session.get(url, params={}).json()
        log.debug(f"  response", extra={"res": res})

        ret = {}
        for i in res['list']:
            ret[i['title']] = i['id']

        log.debug(f"  return", extra={"ret": ret})

        return ret


    def create_table(self, name, columns, color=None):
        """
        [META] Create Table
        Create a new table in a given base
        https://meta-apis-v2.nocodb.com/#tag/DB-Table/operation/db-table-create
        POST http://localhost:8080/api/v2/meta/bases/{baseId}/tables
        TBD
        """

        url = self._url("tables")

        data = {
            "columns": columns,
            "table_name": name,
            "title": name
        }

        if color:
            data["color"] = color

        log.debug(f"Base create_table() url={url}", extra={"data": data})
        res = self.session.post(url, json=data).json()
        log.debug(f"  response", extra={"res": res})

        if "errors" in res or "msg" in res:
            log.error(f"Base create_table() url={url}", extra={"data": data, "res": res})
            return None

        return res['id']


    def get_table_object(self, title):

        # check if such a table exists
        alltables = self.list_tables()

        if title in alltables:

            return Table(alltables[title], base=self)

        else:

            return None


class Table:
    """
    Class for access to a NOCODB table
    """

    def __init__(self, tableid, base=None, host=None, auth_token=None, verify=True):

        # Don't keep the parent Base object because we can work without it
        # Accessing a Table only needs the tableid and the auth_token
        # Thus like this one can create a Table object without a Base object.
        # self.base= base
        self.tableid = tableid
        self.verify = verify
        self.session = None

        if base:

            self.host = base.host
            self.auth_token = base.auth_token
            self.verify = base.verify
            self.session = base.session

        else:

            assert None != host
            assert None != auth_token

            self.host = host
            self.auth_token = auth_token

            self.session = requests.Session()
            self.session.headers.update({"accept": "application/json", "xc-token": self.auth_token})
            self.session.verify = self.verify

        # connection test
        log.debug(f"Table __init__() connection test")
        res = self.count()
        log.debug(f"  response", extra={"res": res})

        assert 'count' in res
        assert 'msg' not in res


    def debug(self):
        print("class Table: ", self.tableid )
        metadata = self.read_table()
        metadata['columnsById'] = "<skipped>"
        print(json.dumps(metadata, indent=4))


    def _meta_url(self, path: str) -> str:
        return f"{self.host}/api/v2/meta/tables/{self.tableid}/{path}"


    def _data_url(self, path: str) -> str:
        return f"{self.host}/api/v2/tables/{self.tableid}/{path}"


    def read_table(self):
        """
        [META] Read Table
        Read the table meta data by the given table ID
        https://meta-apis-v2.nocodb.com/#tag/DB-Table/operation/db-table-read
        GET http://localhost:8080/api/v2/meta/tables/{tableId}
        """
        url = self._meta_url("")

        log.debug(f"Table read_table() url={url}")
        res = self.session.get(url, params={}).json()
        log.debug(f"  response", extra={"res": res})

        return res


    def insert(self, data) -> dict:
        """
        [DATA] Create Table Records
        https://data-apis-v2.nocodb.com/#tag/Table-Records/operation/db-data-table-row-list
        POST http://localhost:8080/api/v2/tables/{tableId}/records
        """

        url = self._data_url("records")
        log.debug(f"Table insert() url={url}", extra={"data": data})
        res = self.session.post(url, json=data)
        log.debug(f"  response", extra={"res": res})

        return res


    def update(self, data):
        """
        [DATA] Update Table Records
        https://data-apis-v2.nocodb.com/#tag/Table-Records/operation/db-data-table-row-update
        PATCH http://localhost:8080/api/v2/tables/{tableId}/records
        """

        url = self._data_url("records")
        log.debug(f"Table update() url={url}", extra={"data": data})
        res= self.session.patch(url, data=data).json()
        log.debug(f"  response", extra={"res": res})

        return res


    def read_table_record(self, primary_key: any) -> dict:
        """
        [DATA] Read Table Record
        This API endpoint allows you to retrieve a single record identified by Record-ID, serving as unique identifier for the record from a specified table.
        https://data-apis-v2.nocodb.com/#tag/Table-Records/operation/db-data-table-row-read
        GET http://localhost:8080/api/v2/tables/{tableId}/records/{recordId}
        """
        url = self._data_url(f"records/{primary_key}")
        log.debug(f"Table read_table_record() url={url}")
        res= self.session.get(url).json()
        log.debug(f"  response", extra={"res": res})

        return res


    def update_record(self, pk: int, key: str, value: object) -> dict:
        record = [{'Primary Key': pk, f'{key}': value}]
        return self.update(record)


    def count(self, where=None):
        """ 
        [DATA] Count Table Records
        This API endpoint allows you to retrieve the total number of records from a specified table or a view. You can narrow down search results by applying where query parameter
        https://data-apis-v2.nocodb.com/#tag/Table-Records/operation/db-data-table-row-count
        Get http://localhost:8080/api/v2/tables/{tableId}/records/count
        """

        url = self._data_url("records/count")

        params = {}

        if where:
            params['where'] = where

        log.debug(f"Table count() url={url}", extra={"params": params})
        res = self.session.get(url, params=params).json()
        log.debug(f"  response", extra={"res": res})

        return res


    def list(self, fields=None, sort=None, where=None, offset=0, limit=None):
        """ 
        [DATA] List Table Records
        This API endpoint allows you to retrieve records from a specified table. 
        https://data-apis-v2.nocodb.com/#tag/Table-Records/operation/db-data-table-row-list
        Get http://localhost:8080/api/v2/tables/{tableId}/records
        """

        url = self._data_url("records")

        params = {}

        if fields:
            params['fields'] = fields
        if sort:
            params['sort'] = sort
        if offset:
            params['offset'] = offset
        if where:
            params['where'] = where
        if limit:
            params['limit'] = limit

        log.debug(f"Table list() url={url}", extra={"params": params})
        res = self.session.get(url, params=params).json()
        log.debug(f"  response", extra={"res": res})

        return res


    def list_all_records(self, fields=None, sort=None, where=None, offset=0):
        """ 
        [DATA] List All Table Records
        This API endpoint allows you to retrieve records from a specified table. 
        https://data-apis-v2.nocodb.com/#tag/Table-Records/operation/db-data-table-row-list
        Get http://localhost:8080/api/v2/tables/{tableId}/records
        """
        url = self._data_url("records")
        params = {}
        limit = self.count().get('count', 0)

        if fields:
            params['fields'] = fields
        if sort:
            params['sort'] = sort
        if offset:
            params['offset'] = offset
        if where:
            params['where'] = where
        if limit:
            params['limit'] = limit

        log.debug(f"Table list_all_records() url={url}", extra={"params": params})
        res = self.session.get(url, params=params).json()
        log.debug(f"  response", extra={"res": res})

        page_number = res.get('pageInfo', {}).get('pageNumber', 1)
        # Make sure to get ALL results (not just first 1k)
        log.debug(f"  response", extra={"res": res})
        while (res.get('pageInfo', {}).get('isLastPage', True) == False):
            params['page'] = page_number + 1
            log.debug(f"  next page url={url}", extra={"params": params})
            res2 = self.session.get(url, params=params).json()
            log.debug(f"  response", extra={"res2": res2})
            res['list'].extend(res2.get('list', []))
            res['pageInfo'] = res2.get('pageInfo', {})
            page_number = page_number + 1
            # print("Page number: ", page_number)

        return res


    def delete(self, list=None):
        """
        [DATA] Delete Table Records
        This API endpoint allows deleting existing records within a specified table identified by 
        an array of Record-IDs, serving as unique identifier for the record. Records to be deleted are input as an array of record-identifiers.
        https://data-apis-v2.nocodb.com/#tag/Table-Records/operation/db-data-table-row-delete
        DELETE http://localhost:8080/api/v2/tables/{tableId}/records
        """
        url = self._data_url("records")

        if list is None:
            log.debug(f"Table delete() without list url={url}")
            res = self.session.delete(url).json()
        else:
            log.debug(f"Table delete() with list url={url}", extra={"list": list})
            res = self.session.delete(url, data=list).json()

        log.debug(f"  response", extra={"res": res})

        return res


    def create_column(self, column_name, column_type, extra_options=None):
        """
        [DATA] Create Table Column
        This API endpoint allows creating a new column within a specified table.
        https://data-apis-v2.nocodb.com/#tag/Table-Records/operation/db-data-table-row-create
        POST http://localhost:8080/api/v2/meta/tables/{tableId}/columns
        """
        url = self._meta_url("columns")

        data = {
            "title": column_name,
            "uidt": column_type
        }

        if extra_options:
            data.update(extra_options)

        log.debug(f"Table create_column() url={url}", extra={"data": data})
        res = self.session.post(url, json=data).json()
        log.debug(f"  response", extra={"res": res})

        return res


    def link_records(self, linkFieldId, recordId, refRowPKValue = None, refRowPKValues = None) -> requests.Response:
        """
        [DATA] Link Records
        This API endpoint allows linking records within a specified table.
        POST https://app.nocodb.com/api/v1/db/data/{orgs}/{baseName}/{tableName}/{rowId}/{relationType}/{columnName}/{refRowId}
        """
        table_metadata = self.read_table()
        base_id = table_metadata['base_id']
        column_link_type = table_metadata['columnsById'][linkFieldId]['colOptions']['type']
        # Encode the recordId to ensure it is URL-safe
        encoded_record_id = urllib.parse.quote(str(recordId), safe='')
        if not refRowPKValues:
            refRowPKValues = refRowPKValue
        if isinstance(refRowPKValues, list):
            for i in range(len(refRowPKValues)):
                refRowPKValues[i] = urllib.parse.quote(str(refRowPKValues[i]), safe='')
        else:
            refRowPKValues = urllib.parse.quote(str(refRowPKValues), safe='')


        if isinstance(refRowPKValues, list):
            for refRowPKValue in refRowPKValues:
                url = f"{self.host}/api/v1/db/data/noco/{base_id}/{self.tableid}/{encoded_record_id}/{column_link_type}/{linkFieldId}/{refRowPKValue}"
                log.debug(f"Table link_records() with list", extra={"url": url})
                res = self.session.post(url)
                log.debug(f"  response", extra={"res": res})

                if res.status_code != 200:
                    log.warning(f"Table link_records() with list status_code != 200 Failed to link record {refRowPKValue} with {recordId}: {res.text}",
                        extra={"res": res})

        else:
            url = f"{self.host}/api/v1/db/data/noco/{base_id}/{self.tableid}/{encoded_record_id}/{column_link_type}/{linkFieldId}/{refRowPKValues}"
            log.debug(f"Table link_records() else", extra={"url": url})
            res = self.session.post(url)
            log.debug(f"  response", extra={"res": res})

            if res.status_code != 200:
                log.warning(f"Table link_records() without list status_code != 200 Failed to link record {refRowPKValue} with {recordId}: {res.text}",
                    extra={"res": res})

        return res.json()


    def list_linked_records(self, linkFieldId, recordId) -> requests.Response:
        """ 
        [DATA] List Linked Records
        This API endpoint allows you to retrieve all records linked to a specified record within a table.
        https://data-apis-v2.nocodb.com/#tag/Table-Records/operation/db-data-table-row-linked-records
        Get https://app.nocodb.com/api/v2/tables/{tableId}/links/{linkFieldId}/records/{recordId}
        """
        encoded_record_id = urllib.parse.quote(str(recordId), safe='')
        url = self._data_url(f"links/{linkFieldId}/records/{encoded_record_id}")
        log.debug(f"Table list_linked_records() url={url}")
        res = self.session.get(url).json()
        log.debug(f"  response", extra={"res": res})

        links_list = res.get('list')
        if (not links_list is None):
            totalRows = res.get('pageInfo', {}).get('totalRows', 0)
            if (totalRows > len(links_list)):
                url = self._data_url(f"links/{linkFieldId}/records/{encoded_record_id}?limit={totalRows}")
                log.debug(f"Table list_linked_records() with links_list url={url}")
                res = self.session.get(url).json()
                log.debug(f"  response", extra={"res": res})

        return res


    def unlink_records(self, linkFieldId, recordId, refRowPKValue = None, refRowPKValues = None) -> requests.Response:
        """
        [DATA] Unlink Records
        This API endpoint allows unlinking records within a specified table.
        POST https://app.nocodb.com/api/v1/db/data/{orgs}/{baseName}/{tableName}/{rowId}/{relationType}/{columnName}/{refRowId}
        """
        table_metadata = self.read_table()
        base_id = table_metadata['base_id']
        column_link_type = table_metadata['columnsById'][linkFieldId]['colOptions']['type']
        # Encode the recordId to ensure it is URL-safe
        encoded_record_id = urllib.parse.quote(str(recordId), safe='')
        if not refRowPKValues:
            refRowPKValues = refRowPKValue
        if isinstance(refRowPKValues, list):
            for i in range(len(refRowPKValues)):
                refRowPKValues[i] = urllib.parse.quote(str(refRowPKValues[i]), safe='')
        else:
            refRowPKValues = urllib.parse.quote(str(refRowPKValues), safe='')


        if isinstance(refRowPKValues, list):
            for refRowPKValue in refRowPKValues:
                url = f"{self.host}/api/v1/db/data/noco/{base_id}/{self.tableid}/{encoded_record_id}/{column_link_type}/{linkFieldId}/{refRowPKValue}"
                log.debug(f"Table unlink_records() from list url={url}")
                res = self.session.delete(url)
                log.debug(f"  response", extra={"res": res})

                if res.status_code != 200:
                    log.warning(f"Table unlink_records() Failed to link record {refRowPKValue} with {recordId}: {res.text}")
        else:
            url = f"{self.host}/api/v1/db/data/noco/{base_id}/{self.tableid}/{encoded_record_id}/{column_link_type}/{linkFieldId}/{refRowPKValues}"
            log.debug(f"Table unlink_records() else url={url}")
            res = self.session.delete(url)
            log.debug(f"  response", extra={"res": res})

            if res.status_code != 200:
                log.warning(f"Table unlink_records() Failed to link record {refRowPKValues} with {recordId}: {res.text}")

        return res.json()