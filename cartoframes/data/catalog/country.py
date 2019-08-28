from data.catalog.repo import Repository


class Country(object):

    def __init__(self, iso3):
        self.iso3 = iso3
        self.repo = Repository()

    @staticmethod
    def get(self, iso3):
        return [Country(country['country_iso3_code']) for country in self.repo.get_countries('country_iso3_code = ' + iso3)]

    def datasets(self):
        # we need access to Repo class so we can query datasets filter by this country --> Circular dependency!!!
        return self.repo.get_datasets('country_iso3_code = ' + self.iso3)
