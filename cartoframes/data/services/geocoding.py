# - *- coding: utf- 8 - *-

from __future__ import absolute_import

import re
import logging

from .utils import geocoding_utils
from .utils import geocoding_constants
from .utils import TableGeocodingLock

from .service import Service
from ...core.managers.source_manager import SourceManager
from ...io.carto import read_carto, to_carto, has_table, delete_table, update_table, copy_table, create_table_from_query


class Geocoding(Service):
    """Geocoding using CARTO data services.

    This requires a CARTO account with and API key that allows for using geocoding services;
    (through explicit argument in constructor or via the default credentials).

    To prevent having to geocode records that have been previously geocoded, and thus spend quota unnecessarily,
    you should always preserve the ``the_geom`` and ``carto_geocode_hash`` columns generated by the
    geocoding process. This will happen automatically if your input is a table from CARTO processed in place
    (i.e. without a ``table_name`` parameter) or if you save your results in a CARTO table using the ``table_name``
    parameter, and only use the resulting table for any further geocoding.

    In case you're geocoding local data from a ``DataFrame`` that you plan to re-geocode again, (e.g. because
    you're making your work reproducible by saving all the data preparation steps in a notebook),
    we advise to save the geocoding results immediately to the same store from when the data is originally taken,
    for example:

    .. code:: python

        dataframe = pandas.read_csv('my_data')
        dataframe = Geocoding().geocode(dataframe, 'address').data
        dataframe.to_csv('my_data')

    As an alternative you can use the ``cached`` option to store geocoding results in a CARTO table
    and reuse them in later geocodings. It is needed to use the ``table_name`` parameter with the name
    of the table used to cache the results.

    If the same dataframe if geocoded repeatedly no credits will be spent, but note there is a time overhead
    related to uploading the dataframe to a temporary table for checking for changes.

    .. code:: python

        dataframe = pandas.read_csv('my_data')
        dataframe = Geocoding().geocode(dataframe, 'address', table_name='my_data', cached=True).data

    If you execute the previous code multiple times it will only spend credits on the first geocoding;
    later ones will reuse the results stored in the ``my_data`` table. This will require extra processing
    time. If the CSV file should ever change, cached results will only be applied to unmodified
    records, and new geocoding will be performed only on new or changed records.
    """

    def __init__(self, credentials=None):
        super(Geocoding, self).__init__(credentials=credentials, quota_service=geocoding_constants.QUOTA_SERVICE)

    def geocode(self, source, street,
                city=None, state=None, country=None,
                status=geocoding_constants.DEFAULT_STATUS,
                table_name=None, if_exists='fail',
                dry_run=False, cached=None):
        """Geocode method

        Args:
            source (str, DataFrame, GeoDataFrame, :py:class:`CartoDataFrame <cartoframes.CartoDataFrame>`):
                table, SQL query or DataFrame object to be geocoded.
            street (str): name of the column containing postal addresses
            city (dict, optional): dictionary with either a `column` key
                with the name of a column containing the addresses' city names or
                a `value` key with a literal city value value, e.g. 'New York'.
                It also accepts a string, in which case `column` is implied.
            state (dict, optional): dictionary with either a `column` key
                with the name of a column containing the addresses' state names or
                a `value` key with a literal state value value, e.g. 'WA'.
                It also accepts a string, in which case `column` is implied.
            country (dict, optional): dictionary with either a `column` key
                with the name of a column containing the addresses' country names or
                a `value` key with a literal country value value, e.g. 'US'.
                It also accepts a string, in which case `column` is implied.
            status (dict, optional): dictionary that defines a mapping from geocoding state
                attributes ('relevance', 'precision', 'match_types') to column names.
                (See https://carto.com/developers/data-services-api/reference/)
                Columns will be added to the result data for the requested attributes.
                By default a column ``gc_status_rel`` will be created for the geocoding
                _relevance_. The special attribute '*' refers to all the status
                attributes as a JSON object.
            table_name (str, optional): the geocoding results will be placed in a new
                CARTO table with this name.
            if_exists (str, optional): Behavior for creating new datasets, only applicable
                if table_name isn't None;
                Options are 'fail', 'replace', or 'append'. Defaults to 'fail'.
            cached (bool, optional): Use cache geocoding results, saving the results in a
                table. This parameter should be used along with ``table_name``.
            dry_run (bool, optional): no actual geocoding will be performed (useful to
                check the needed quota)

        Returns:
            A named-tuple ``(data, metadata)`` containing  either a ``data`` :py:class:`CartoDataFrame
            <cartoframes.CartoDataFrame>` and a ``metadata`` dictionary with global information about
            the geocoding process.

            The ``data`` contains a ``geometry`` column with point locations for the geocoded addresses
            and also a ``carto_geocode_hash`` that, if preserved, can avoid re-geocoding
            unchanged data in future calls to geocode.

            The ``metadata``, as described in https://carto.com/developers/data-services-api/reference/,
            contains the following information:

            +-------------+--------+------------------------------------------------------------+
            | Name        | Type   | Description                                                |
            +=============+========+============================================================+
            | precision   | text   | precise or interpolated                                    |
            +-------------+--------+------------------------------------------------------------+
            | relevance   | number | 0 to 1, higher being more relevant                         |
            +-------------+--------+------------------------------------------------------------+
            | match_types | array  | list of match type strings                                 |
            |             |        | point_of_interest, country, state, county, locality,       |
            |             |        | district, street, intersection, street_number, postal_code |
            +-------------+--------+------------------------------------------------------------+

            By default the ``relevance`` is stored in an output column named ``gc_status_rel``. The name of the
            column and in general what attributes are added as columns can be configured by using a ``status``
            dictionary associating column names to status attribute.

        Examples:

            Geocode a DataFrame:

            .. code::

                import pandas
                from data.services import Geocoding
                from cartoframes.auth import set_default_credentials

                set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

                df = pandas.DataFrame([['Gran Vía 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address','city'])
                gc = Geocoding()
                geocoded_cdf, metadata = gc.geocode(df, street='address', city='city', country={'value': 'Spain'})

                geocoded_cdf.head()

            Geocode a table from CARTO:

            .. code::

                from data.services import Geocoding
                from cartoframes import CartoDataFrame
                from cartoframes.auth import set_default_credentials

                set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

                cdf = CartoDataFrame.from_carto('table_name')
                gc = Geocoding()
                geocoded_cdf, metadata = gc.geocode(cdf, street='address')

                geocoded_cdf.head()

            Geocode a query against a table from CARTO:

            .. code::

                from data.services import Geocoding
                from cartoframes import CartoDataFrame
                from cartoframes.auth import set_default_credentials

                set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

                cdf = CartoDataFrame.from_carto('SELECT * FROM table_name WHERE value > 1000')
                gc = Geocoding()
                geocoded_cdf, metadata = gc.geocode(cdf, street='address')

                geocoded_cdf.head()

            Obtain the number of credits needed to geocode a CARTO table:

            .. code::

                from data.services import Geocoding
                from cartoframes import CartoDataFrame
                from cartoframes.auth import set_default_credentials

                set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

                cdf = CartoDataFrame.from_carto('table_name')
                gc = Geocoding()
                geocoded_cdf, metadata = gc.geocode(cdf, street='address', dry_run=True)

                print(metadata['required_quota'])


            Filter results by relevance:

            .. code::

                import pandas
                from data.services import Geocoding
                from cartoframes.auth import set_default_credentials

                set_default_credentials('YOUR_USER_NAME', 'YOUR_API_KEY')

                df = pandas.DataFrame([['Gran Vía 46', 'Madrid'], ['Ebro 1', 'Sevilla']], columns=['address','city'])
                gc = Geocoding()
                geocoded_cdf, metadata = gc.geocode(
                    df,
                    street='address',
                    city='city',
                    country={'value': 'Spain'},
                    status=['relevance']
                )

                # show rows with relevance greater than 0.7:
                print(geocoded_cdf[geocoded_cdf['carto_geocode_relevance'] > 0.7, axis=1)])
        """

        self._source_manager = SourceManager(source, self._credentials)

        self.columns = self._source_manager.get_column_names()

        if cached:
            if not table_name:
                raise ValueError('There is no "table_name" to cache the data')
            return self._cached_geocode(source, table_name, street, city=city, state=state, country=country,
                                        dry_run=dry_run)

        city, state, country = [
            geocoding_utils.column_or_value_arg(arg, self.columns) for arg in [city, state, country]
        ]

        input_table_name, is_temporary = self._table_for_geocoding(source, table_name, if_exists, dry_run)

        metadata = self._geocode(input_table_name, street, city, state, country, status, dry_run)

        if dry_run:
            return self.result(data=None, metadata=metadata)

        cdf = read_carto(input_table_name, self._credentials)

        if is_temporary:
            delete_table(input_table_name, self._credentials, log_enabled=False)

        result = self.result(data=cdf, metadata=metadata)

        print('Success! Data geocoded correctly')

        return result

    def _cached_geocode(self, source, table_name, street, city, state, country, dry_run):
        """
        Geocode a dataframe caching results into a table.
        If the same dataframe if geocoded repeatedly no credits will be spent.
        But note there is a time overhead related to uploading the dataframe to a
        temporary table for checking for changes.
        """
        has_cache = has_table(table_name, self._credentials)

        if has_cache:
            cache_source_manager = SourceManager(table_name, self._credentials)
            cache_columns = cache_source_manager.get_column_names()
            if geocoding_constants.HASH_COLUMN not in cache_columns:
                raise ValueError('Cache table {} exists but is not a valid geocode table'.format(table_name))

        if geocoding_constants.HASH_COLUMN in self.columns or not has_cache:
            return self.geocode(
                source, street=street, city=city, state=state,
                country=country, table_name=table_name, dry_run=dry_run, if_exists='replace')

        tmp_table_name = self._new_temporary_table_name()
        if self._source_manager.is_table():
            raise ValueError('cached geocoding cannot be used with tables')

        to_carto(source, tmp_table_name, self._credentials, force_cartodbfy=True, log_enabled=False)

        self._execute_query(
            """
            ALTER TABLE {tmp_table} ADD COLUMN IF NOT EXISTS {hash} text
            """.format(tmp_table=tmp_table_name, hash=geocoding_constants.HASH_COLUMN))

        hcity, hstate, hcountry = [
            geocoding_utils.column_or_value_arg(arg, self.columns) for arg in [city, state, country]
        ]

        hash_expr = geocoding_utils.hash_expr(street, hcity, hstate, hcountry, table_prefix=tmp_table_name)
        self._execute_query(
            """
            UPDATE {tmp_table} SET {hash}={table}.{hash}, the_geom={table}.the_geom
            FROM {table} WHERE {hash_expr}={table}.{hash}
            """.format(
                tmp_table=tmp_table_name,
                table=table_name,
                hash=geocoding_constants.HASH_COLUMN,
                hash_expr=hash_expr
            ))

        delete_table(table_name, self._credentials, log_enabled=False)

        update_table(
            table_name=tmp_table_name,
            credentials=self._credentials,
            new_table_name=table_name,
            privacy='private',
            log_enabled=False
        )

        # TODO: should remove the cartodb_id column from the result
        # TODO: refactor to share code with geocode() and call self._geocode() here instead
        # actually to keep hashing knowledge encapsulated (AFW) this should be handled by
        # _geocode using an additional parameter for an input table
        cdf, metadata = self.geocode(table_name, street=street, city=city,
                                     state=state, country=country, dry_run=dry_run)
        return self.result(data=cdf, metadata=metadata)

    def _table_for_geocoding(self, source, table_name, if_exists, dry_run):
        is_temporary = False
        input_table_name = table_name
        if self._source_manager.is_table():
            if table_name:
                copy_table(source, input_table_name, self._credentials, if_exists, log_enabled=False)
            else:
                input_table_name = source
        elif self._source_manager.is_query():
            if not input_table_name:
                input_table_name = self._new_temporary_table_name()
                is_temporary = True
            create_table_from_query(source, input_table_name, self._credentials, if_exists, log_enabled=False)
        elif self._source_manager.is_dataframe():
            if not input_table_name:
                input_table_name = self._new_temporary_table_name()
                is_temporary = True
            to_carto(source, input_table_name, self._credentials, if_exists, force_cartodbfy=True, log_enabled=False)
        return (input_table_name, is_temporary)

    # Note that this can be optimized for non in-place cases (table_name is not None), e.g.
    # injecting the input query in the geocoding expression,
    # receiving geocoding results instead of storing in a table, etc.
    # But that would make transition to using AFW harder.

    def _geocode(self, table_name, street, city=None, state=None, country=None, status=None, dry_run=False):
        # Internal Geocoding implementation.
        # Geocode a table's rows not already geocoded in a dataset'

        logging.info('table_name = "%s"', table_name)
        logging.info('street = "%s"', street)
        logging.info('city = "%s"', city)
        logging.info('state = "%s"', state)
        logging.info('country = "%s"', country)
        logging.info('status = "%s"', status)
        logging.info('dry_run = "%s"', dry_run)

        output = {}

        summary = {s: 0 for s in [
            'new_geocoded', 'new_nongeocoded',
            'changed_geocoded', 'changed_nongeocoded',
            'previously_geocoded', 'previously_nongeocoded']}

        # TODO: Use a single transaction so that reported changes (posterior - prior queries)
        # are only caused by the geocoding process. Note that no rollback should be
        # performed once the geocoding update is executed, since
        # quota spent by the Dataservices function would not be rolled back;
        # hence a Python `with` statement is not used here.
        # transaction = connection.begin()

        result = self._execute_prior_summary(table_name, street, city, state, country)
        if result:
            for row in result.get('rows'):
                gc_state = row.get('gc_state')
                count = row.get('count')
                summary[gc_state] = count

        geocoding_utils.set_pre_summary_info(summary, output)

        aborted = False

        if output['required_quota'] > 0 and not dry_run:
            with TableGeocodingLock(self._execute_query, table_name) as locked:
                if not locked:
                    output['error'] = 'The table is already being geocoded'
                    output['aborted'] = aborted = True
                else:
                    sql, add_columns = geocoding_utils.geocode_query(table_name, street, city, state, country, status)

                    add_columns += [(geocoding_constants.HASH_COLUMN, 'text')]

                    logging.info("Adding columns %s if needed", ', '.join([c[0] for c in add_columns]))
                    alter_sql = "ALTER TABLE {table} {add_columns};".format(
                        table=table_name,
                        add_columns=','.join([
                            'ADD COLUMN IF NOT EXISTS {} {}'.format(name, type) for name, type in add_columns]))
                    self._execute_query(alter_sql)

                    logging.debug("Executing query: %s", sql)
                    result = None
                    try:
                        result = self._execute_long_running_query(sql)
                    except Exception as err:
                        logging.error(err)
                        msg = str(err)
                        output['error'] = msg
                        # FIXME: Python SDK should return proper exceptions
                        # see: https://github.com/CartoDB/cartoframes/issues/751
                        match = re.search(
                            r'Remaining quota:\s+(\d+)\.\s+Estimated cost:\s+(\d+)',
                            msg, re.MULTILINE | re.IGNORECASE
                        )
                        if match:
                            output['remaining_quota'] = int(match.group(1))
                            output['estimated_cost'] = int(match.group(2))
                        aborted = True
                        # Don't rollback to avoid losing any partial geocodification:
                        # TODO
                        # transaction.commit()

                    if result and not aborted:
                        # Number of updated rows not available for batch queries
                        # output['updated_rows'] = result.rowcount
                        # logging.info('Number of rows updated: %d', output['updated_rows'])
                        pass

            if not aborted:
                sql = geocoding_utils.posterior_summary_query(table_name)
                logging.debug("Executing result summary query: %s", sql)
                result = self._execute_query(sql)
                geocoding_utils.set_post_summary_info(summary, result, output)

        if not aborted:
            # TODO
            # transaction.commit()
            pass

        return output  # TODO: GeocodeResult object

    def _execute_prior_summary(self, dataset_name, street, city, state, country):
        sql = geocoding_utils.exists_column_query(dataset_name, geocoding_constants.HASH_COLUMN)
        logging.debug("Executing check first time query: %s", sql)
        result = self._execute_query(sql)
        if not result or result.get('total_rows', 0) == 0:
            sql = geocoding_utils.first_time_summary_query(dataset_name, street, city, state, country)
            logging.debug("Executing first time summary query: %s", sql)
        else:
            sql = geocoding_utils.prior_summary_query(dataset_name, street, city, state, country)
            logging.debug("Executing summary query: %s", sql)
        return self._execute_query(sql)
