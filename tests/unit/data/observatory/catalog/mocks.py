class BigQueryClientMock(object):
    def __init__(self, response):
        self.response = response

        self.bq_public_project = 'public_data_project'
        self.bq_project = 'user_data_project'
        self.bq_dataset = 'username'
        self._gcs_bucket = 'bucket_name'

    def query(self, _1):
        return True

    def download_to_file(self, _1, column_names=None):
        if isinstance(self.response, Exception):
            raise self.response
        else:
            return self.response

    def get_table_column_names(self, _1, _2, _3):
        return True
