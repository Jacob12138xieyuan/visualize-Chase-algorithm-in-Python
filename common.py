from tabulate import tabulate


def print_df_pretty(df):
    # Convert the DataFrame to a formatted table with borders
    table = tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=True)
    # Print the table
    print(table)


if __name__ == "__main__":
    data = [
        {"Name": "John", "Age": 28, "City": "New York"},
        {"Name": "Alice", "Age": 32, "City": "Chicago"},
        {"Name": "Bob", "Age": 45, "City": "San Francisco"},
    ]

    # 'plain' format
    table = tabulate(data, headers='keys', tablefmt='plain')
    print("plain:\n", table)

    # 'simple' format
    table = tabulate(data, headers='keys', tablefmt='simple')
    print("simple:\n", table)

    # 'grid' format
    table = tabulate(data, headers='keys', tablefmt='grid')
    print("grid:\n", table)

    # 'fancy_grid' format
    table = tabulate(data, headers='keys', tablefmt='fancy_grid')
    print("fancy_grid:\n", table)

    # 'pipe' format
    table = tabulate(data, headers='keys', tablefmt='pipe')
    print("pipe:\n", table)

    # 'orgtbl' format
    table = tabulate(data, headers='keys', tablefmt='orgtbl')
    print("orgtbl:\n", table)

    # 'jira' format
    table = tabulate(data, headers='keys', tablefmt='jira')
    print("jira:\n", table)

    # 'presto' format
    table = tabulate(data, headers='keys', tablefmt='presto')
    print("presto:\n", table)

    # 'pretty' format
    table = tabulate(data, headers='keys', tablefmt='pretty')
    print("pretty:\n", table)

    # 'psql' format
    table = tabulate(data, headers='keys', tablefmt='psql')
    print("psql:\n", table)

    # 'rst' format
    table = tabulate(data, headers='keys', tablefmt='rst')
    print("rst:\n", table)

    # 'mediawiki' format
    table = tabulate(data, headers='keys', tablefmt='mediawiki')