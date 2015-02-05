from scraperwiki import sql as sqlite


class SqliteInterface:
    # return all rows in a table
    def fetch_all(self, table):
        return scraperwiki.sql.select("* FROM %s" % table)

    # save row to a table
    def save(self, table, row):
        scraperwiki.sql.save(unique_keys, row, table)
