from tabulate import tabulate


def print_df_pretty(df):
    # Convert the DataFrame to a formatted table with borders
    table = tabulate(df, headers='keys', tablefmt='fancy_grid', showindex=True)
    # Print the table
    print(table)

def get_all_subsets(list, cur_subset, index, max_attrs):
    '''
    Use recursion to generate all possible subsets of a given list,
    meanwhile, filtering out those don't satisfy len(subset) == max_attrs
    '''
    # finish one recursion
    if index == len(list):
        if count_attributes(cur_subset) == max_attrs:  # Filter out subsets that don't have full attributes
            yield cur_subset
    else:
        # Skip element at index, continue recursion
        yield from get_all_subsets(list, cur_subset, index + 1,max_attrs)
        # Collect element at index, continue recursion
        yield from get_all_subsets(list, cur_subset + [list[index]], index + 1,max_attrs)

                
def is_parent_subset(parent, child):
    """
    Check if parent list contains child list
    eg. parent [A->B,B->A,B->C,A->C]  child [A->B,B->A,B->C]
    """
    return all(fd in parent for fd in child)

def get_key_string(input):
        '''
        for set or list, compute an unique string
        '''
        s = sorted(input)
        return ','.join(map(str,s))
    
def count_attributes(fd_list):
    '''
    Computes the number of attributes shown in the fds
    '''
    all_attributes = set()
    for fd in fd_list:
        all_attributes |= set(fd[0]) | set(fd[1])
    return len(all_attributes)

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